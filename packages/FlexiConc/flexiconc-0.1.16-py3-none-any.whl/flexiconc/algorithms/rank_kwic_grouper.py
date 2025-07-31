from flexiconc.utils.cqp_tools import match_token_df
import pandas as pd

def rank_kwic_grouper(conc, **args):
    """
    Ranks lines based on the count of search terms within a specified token attribute
    and returns token spans for matching tokens.

    Args are dynamically validated and extracted from the schema.

    Parameters:
        conc (Union[Concordance, ConcordanceSubset]): The full concordance or a subset of it.
        args (dict): Arguments defined in the schema.
            - search_terms (list): A list of terms to search for within the tokens.
            - tokens_attribute (str): The token attribute to search within (default: 'word').
            - mode (str): literal matching, regex matching, or CQP-based matching. Possible values: 'literal', 'regex', and 'cqp'. Default is 'literal'.
            - case_sensitive (bool): If True, perform case-sensitive matching. Default is False.
            - include_node (bool): If True, include node-level tokens in the search. Default is False.
            - window_start (int): The lower bound of the window (offset range). Default is -inf.
            - window_end (int): The upper bound of the window (offset range). Default is inf.
            - count_types (bool): If True, count unique types within each line; otherwise, count all matches.

    Returns:
        dict: Contains:
            - "rank_keys": A mapping from line IDs to ranking values.
            - "token_spans": A DataFrame with columns:
                line_id, start_id_in_line, end_id_in_line, category, weight.
    """
    # Metadata for the algorithm
    rank_kwic_grouper._algorithm_metadata = {
        "name": "KWIC Grouper Ranker",
        "description": "Ranks lines based on the count of search terms in a specified token attribute within a window.",
        "algorithm_type": "ranking",
        "args_schema": {
            "type": "object",
            "properties": {
                "search_terms": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "A list of terms to search for within the tokens."
                },
                "tokens_attribute": {
                    "type": "string",
                    "description": "The token attribute to search within (e.g., 'word').",
                    "default": "word",
                    "x-eval": "dict(enum=list(set(conc.tokens.columns) - {'id_in_line', 'line_id', 'offset'}))"
                },
                "mode": {
                    "type": "string",
                    "enum": ["literal", "regex", "cqp"],
                    "description": "Matching strategy for search_terms",
                    "default": "literal"
                },
                "case_sensitive": {
                    "type": "boolean",
                    "description": "If True, the search is case-sensitive.",
                    "default": False
                },
                "include_node": {
                    "type": "boolean",
                    "description": "If True, include node-level tokens in the search.",
                    "default": False
                },
                "window_start": {
                    "type": "integer",
                    "description": "The lower bound of the window (offset range).",
                    "x-eval": "dict(minimum=min(conc.tokens['offset']))"
                },
                "window_end": {
                    "type": "integer",
                    "description": "The upper bound of the window (offset range).",
                    "x-eval": "dict(maximum=max(conc.tokens['offset']))"
                },
                "count_types": {
                    "type": "boolean",
                    "description": "If True, count unique types within each line; otherwise, count all matches.",
                    "default": True
                }
            },
            "required": ["search_terms"]
        }
    }

    # Extract arguments and ensure search_terms is a list.
    search_terms = args.get("search_terms")
    if not isinstance(search_terms, list):
        search_terms = [search_terms]
    tokens_attribute = args.get("tokens_attribute", "word")
    mode  = args.get("mode", "literal").lower()
    if mode not in {"literal", "regex", "cqp"}:
        raise ValueError("mode must be one of 'literal', 'regex', 'cqp'")
    case_sensitive = args.get("case_sensitive", False)
    include_node = args.get("include_node", False)
    window_start = args.get("window_start", float('-inf'))
    window_end = args.get("window_end", float('inf'))
    count_types = args.get("count_types", True)

    # Step 1: Filter tokens based on the specified window.
    filtered_tokens = conc.tokens[
        (conc.tokens["offset"] >= window_start) & (conc.tokens["offset"] <= window_end)
        ]

    # Step 2: Prepare the column to check against the search terms.
    values_to_check = filtered_tokens[tokens_attribute].astype(str)

    # Step 3: Build the matching condition.
    if mode == "literal":
        # ---- exact string match ---------------------------------------
        if not case_sensitive:
            search_terms = [s.lower() for s in search_terms]
            values_to_check = values_to_check.str.lower()
        match_condition = values_to_check.isin(search_terms)

    elif mode == "regex":
        # ---- full-token PCRE match ------------------------------------
        import re
        # join individual patterns, keep capture-groups intact
        pattern = "|".join(f"(?:{p})" for p in search_terms)
        pattern = rf"\A(?:{pattern})\Z"  # ← anchor to whole token
        flags = 0 if case_sensitive else re.IGNORECASE
        match_condition = values_to_check.str.contains(
            pattern, regex=True, flags=flags, na=False
        )

    elif mode == "cqp":
        # ---- single-token CQP expression(s) ---------------------------
        from flexiconc.utils.cqp_tools import match_token_df, parse_cqp
        mask = pd.Series(False, index=values_to_check.index)
        for expr in search_terms:
            mask |= match_token_df(conc.tokens, parse_cqp(expr)[0]['pattern']['token'], as_mask=True)[values_to_check.index]
        match_condition = mask

    # Step 4: Exclude node-level tokens if required.
    if not include_node:
        match_condition &= (filtered_tokens["offset"] != 0)

    # Step 5: Filter tokens with the matching condition.
    matching_tokens = filtered_tokens[match_condition].copy()

    # Step 6: Build token_spans DataFrame BEFORE removing duplicates.
    token_spans = matching_tokens.reset_index(drop=True)
    # For each token, define a span that is one token long:
    token_spans["start_id_in_line"] = token_spans["id_in_line"]
    token_spans["end_id_in_line"] = token_spans["id_in_line"]
    token_spans["category"] = "A"
    token_spans["weight"] = 1
    token_spans = token_spans[["line_id", "start_id_in_line", "end_id_in_line", "category", "weight"]]

    # Add tokens_attribute and corresponding values list for each token span.
    token_spans["tokens_attribute"] = tokens_attribute
    token_spans["values"] = token_spans.apply(
        lambda row: conc.tokens[
            (conc.tokens["line_id"] == row["line_id"]) &
            (conc.tokens["id_in_line"] >= row["start_id_in_line"]) &
            (conc.tokens["id_in_line"] <= row["end_id_in_line"])
        ][tokens_attribute].tolist(),
        axis=1
    )
    token_spans = token_spans[["line_id", "start_id_in_line", "end_id_in_line", "category", "weight", "tokens_attribute", "values"]]

    # Step 7: If count_types is True, remove duplicate types within each line, accounting for case sensitivity
    if count_types:
        if not case_sensitive:
            matching_tokens[tokens_attribute] = matching_tokens[tokens_attribute].str.lower()
        # Remove duplicates based on line_id and the token attribute
        matching_tokens = matching_tokens.drop_duplicates(subset=['line_id', tokens_attribute])

    # Step 8: Group the (now deduplicated) tokens by line_id and count the occurrences within each line
    line_counts = matching_tokens.groupby('line_id').size().reindex(conc.metadata.index, fill_value=0)
    rank_keys = line_counts.to_dict()

    return {"rank_keys": rank_keys, "token_spans": token_spans}

