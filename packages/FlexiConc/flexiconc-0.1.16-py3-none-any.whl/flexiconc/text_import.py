import sqlite3
import pandas as pd

class TextImport:
    def __init__(self, db_path):
        self._db_path = str(db_path)
        self._conn = sqlite3.connect(self._db_path)
        self._conn.create_function("REGEXP", 2, self._sqlite_regexp)
        self._token_count = self._get_token_count()
        self._token_attributes = self._get_token_attributes()
        self._span_types = self._list_span_tables()
        self._span_counts = {stype: self._get_span_count(stype) for stype in self._span_types}

    def _sqlite_regexp(self, pattern, value):
        import re
        if value is None or pattern is None:
            return False
        try:
            # Case-insensitive if pattern starts with (?i)
            if pattern.startswith("(?i)"):
                flags = re.IGNORECASE
                pattern = pattern[4:]
            else:
                flags = 0
            return re.fullmatch(pattern, value, flags) is not None
        except re.error:
            return False

    def _get_token_count(self):
        cursor = self._conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tokens")
        return cursor.fetchone()[0]

    def _get_token_attributes(self):
        cursor = self._conn.cursor()
        cursor.execute("PRAGMA table_info(tokens)")
        columns = [row[1] for row in cursor.fetchall()]
        return [col for col in columns if col != "cpos"]

    def _list_span_tables(self):
        cursor = self._conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'spans\\_%' ESCAPE '\\'")
        return [name[0][len("spans_"):] for name in cursor.fetchall()]

    def _get_span_count(self, span_type):
        table = f"spans_{span_type}"
        cursor = self._conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        return cursor.fetchone()[0]

    @property
    def token_count(self):
        """Total number of tokens in the corpus."""
        return self._token_count

    @property
    def token_attributes(self):
        """List of token attributes (columns in tokens table except cpos)."""
        return list(self._token_attributes)

    @property
    def span_types(self):
        """List of span types (table suffixes after 'spans_')."""
        return list(self._span_types)

    @property
    def span_counts(self):
        """Dict mapping span type to count."""
        return dict(self._span_counts)

    def tokens(self, columns=None, cpos_slice=None):
        query = "SELECT * FROM tokens"
        if cpos_slice is not None:
            query += f" WHERE cpos >= {cpos_slice.start if cpos_slice.start is not None else 0}"
            if cpos_slice.stop is not None:
                query += f" AND cpos < {cpos_slice.stop}"
        df = pd.read_sql_query(query, self._conn)
        if columns is not None:
            df = df[columns]
        return df

    def get_spans(self, span_type, columns=None, span_id_slice=None):
        table = f"spans_{span_type}"
        query = f"SELECT * FROM {table}"
        if span_id_slice is not None:
            query += f" WHERE id >= {span_id_slice.start if span_id_slice.start is not None else 0}"
            if span_id_slice.stop is not None:
                query += f" AND id < {span_id_slice.stop}"
        df = pd.read_sql_query(query, self._conn)
        if columns is not None:
            df = df[columns]
        return df

    def find_spans_covering(self, cpos, span_type):
        table = f"spans_{span_type}"
        query = f"SELECT * FROM {table} WHERE start <= ? AND end > ?"
        df = pd.read_sql_query(query, self._conn, params=(cpos, cpos))
        return df

    def __repr__(self):
        span_info = ", ".join(f"{stype} ({self.span_counts[stype]})" for stype in self.span_types)
        attr_info = ", ".join(self.token_attributes)
        return (f"<Corpus: {self.token_count} tokens"
                f" | token attributes: [{attr_info}]"
                f" | spans: {span_info}>")

    def close(self):
        self._conn.close()

    def _find_sequence_matches_sql(self, query):
        from flexiconc.utils import cqp_tools

        # Try to parse as CQP
        try:
            patterns = cqp_tools.parse_cqp(query)
        except Exception:
            patterns = None

        # If parse fails or patterns is empty, treat as simple sequence and retry with CQP-style [word="..."] slots
        if not patterns:
            tokens = query.strip().split()
            # Default: case-insensitive
            cqp_query = " ".join(f'[word="{tok}" %c]' for tok in tokens)
            patterns = cqp_tools.parse_cqp(cqp_query)

        # If still empty or error, return no matches
        if not patterns:
            return []

        # Now match the sequence slot by slot
        con = self._conn
        table = "tokens"
        # For each slot, get the set of cpos indices matching that pattern
        slot_indices = [set(cqp_tools.match_token_sqlite(con, table, p['pattern']['token'])) for p in patterns]

        # Sequence matching: Find all positions where the sequence matches in order
        qlen = len(patterns)
        first_indices = slot_indices[0]
        candidates = set(i for i in first_indices if all(
            (i + j) in slot_indices[j] for j in range(qlen)
        ))

        return [(i-1, i + qlen - 2) for i in sorted(candidates)] #-1 and -2 to return correct cpos rather than row numbers

    def _filter_matches_in_span(self, matches, limit_context_span, context_size):
        if not (limit_context_span and limit_context_span in self.span_types):
            results = []
            left_size, right_size = context_size
            for matchstart, matchend in matches:
                contextstart = max(0, matchstart - left_size)
                contextend = matchend + right_size
                results.append(((matchstart, matchend), (contextstart, contextend)))
            return results

        spans_df = self.get_spans(limit_context_span)
        spans = sorted(spans_df[["start", "end"]].values.tolist())
        matches = sorted(matches)
        filtered = []
        span_idx = 0
        num_spans = len(spans)
        left_size, right_size = context_size
        for matchstart, matchend in matches:
            while span_idx < num_spans and spans[span_idx][1] - 1 < matchstart:
                span_idx += 1
            if span_idx < num_spans:
                start, end = spans[span_idx]
                # Now span covers indices start..end-1, so inclusive end is end-1
                if start <= matchstart and end >= matchend:
                    contextstart = max(start, matchstart - left_size)
                    contextend = min(end, matchend + right_size)
                    filtered.append(((matchstart, matchend), (contextstart, contextend)))
        return filtered

    def query(self, query, context_size=(10, 10), limit_context_span='text'):
        matches = self._find_sequence_matches_sql(query)
        matches = self._filter_matches_in_span(matches, limit_context_span, context_size)
        return matches

    def build_concordance(self, matches, span_types_for_metadata=None):
        from flexiconc import Concordance
        import pandas as pd
        from intervaltree import IntervalTree

        if not matches:
            return Concordance(
                metadata=pd.DataFrame(),
                tokens=pd.DataFrame(),
                matches=pd.DataFrame()
            )

        num_tokens = self.token_count

        if span_types_for_metadata is None:
            span_types_for_metadata = list(self.span_types)

        # Pre-load and build interval trees for fast span lookup
        spans_tables = {}
        span_trees = {}
        for stype in span_types_for_metadata:
            spans_df = self.get_spans(stype)
            spans_tables[stype] = spans_df
            tree = IntervalTree()
            for i, row in spans_df.iterrows():
                tree[row["start"]:row["end"] + 1] = row.to_dict()
            span_trees[stype] = tree

        conn = self._conn

        # Gather all needed token indices, with repetitions allowed (in order of context extraction)
        all_token_cpos = []
        per_line_token_cpos = []  # For mapping per-line context to concordance indices
        for (matchstart, matchend), (contextstart, contextend) in matches:
            context_token_indices = [cpos for cpos in range(contextstart, contextend + 1) if 0 <= cpos < num_tokens]
            all_token_cpos.extend(context_token_indices)
            per_line_token_cpos.append(context_token_indices)

        # Retrieve all unique token rows from the DB (keep cpos as a column)
        unique_cpos = sorted(set(all_token_cpos))
        if not unique_cpos:
            tokens_df_full = pd.DataFrame()
        else:
            placeholders = ",".join("?" for _ in unique_cpos)
            query = f"SELECT * FROM tokens WHERE cpos IN ({placeholders})"
            tokens_df_full = pd.read_sql_query(query, conn, params=unique_cpos).set_index("cpos")

        # Build the tokens table for the concordance, with possible repetitions
        tokens_records = []
        matches_records = []
        metadata_records = []
        global_token_idx = 0

        for line_id, (((matchstart, matchend), (contextstart, contextend)), context_token_indices) in enumerate(
                zip(matches, per_line_token_cpos)):
            # Map each cpos in this context to its index in the concordance tokens df (for this match only)
            cpos_to_conc_idx = {}
            for idx_in_line, cpos in enumerate(context_token_indices):
                if cpos not in tokens_df_full.index:
                    continue
                row = tokens_df_full.loc[cpos].to_dict()
                row.update({
                    "line_id": line_id,
                    "id_in_line": idx_in_line,
                    "cpos": cpos  # keep cpos in the output tokens table
                })
                tokens_records.append(row)
                cpos_to_conc_idx[cpos] = global_token_idx
                global_token_idx += 1

            # Calculate relative match_start and match_end
            # Find the *first* and *last* appearance of matchstart/matchend in the context
            # (They should be there, if not, None)
            match_start_conc = None
            match_end_conc = None
            for idx, cpos in enumerate(context_token_indices):
                abs_idx = cpos_to_conc_idx.get(cpos, None)
                if cpos == matchstart and match_start_conc is None:
                    match_start_conc = abs_idx
                if cpos == matchend:
                    match_end_conc = abs_idx
            matches_records.append({
                "line_id": line_id,
                "match_start": match_start_conc,
                "match_end": match_end_conc,
                "slot": 0
            })

            meta = {"line_id": line_id}
            for stype in span_types_for_metadata:
                intervals = span_trees[stype][matchstart]
                for interval in intervals:
                    row = interval.data
                    for col in row:
                        if col in {"id", "start", "end"}:
                            continue
                        meta[f"{stype}.{col}"] = row[col]
                    break
            meta["original_match_start"] = matchstart
            meta["original_match_end"] = matchend
            meta["original_context_start"] = contextstart
            meta["original_context_end"] = contextend
            metadata_records.append(meta)

        tokens_df_result = pd.DataFrame(tokens_records)
        matches_df_result = pd.DataFrame(matches_records)
        metadata_df_result = pd.DataFrame(metadata_records)

        return Concordance(
            metadata=metadata_df_result,
            tokens=tokens_df_result,
            matches=matches_df_result
        )



