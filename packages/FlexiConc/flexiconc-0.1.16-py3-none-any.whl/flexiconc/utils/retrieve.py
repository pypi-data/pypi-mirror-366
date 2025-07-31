import pandas as pd
from typing import Optional, List

from flexiconc.concordance import AnalysisTreeNode
from flexiconc.visualization.html_visualizer import format_concordance_line
from flexiconc import CONFIG


def retrieve_from_cwb(
        self,
        registry_dir: Optional[str] = None,
        corpus_name: str = "",
        query: str = "",
        tokens_attrs: Optional[List[str]] = None,
        metadata_attrs: Optional[List[str]] = None,
        corpus = None,
        context: int = 20,
) -> None:
    """
    Retrieves a concordance from the CWB (Corpus Workbench), processes the data, and updates the Concordance object.

    Parameters:
    - registry_dir (Optional[str], default=None): The path to the CWB registry directory. If None, it uses the default configuration.
    - corpus_name (str, default="DNOV-CWB"): The name of the corpus in CWB.
    - query (str, default=""): The query string used to retrieve concordance lines.
    - tokens_attrs corpus formats – RC21 can’t solve this, but should raise awareness 
(Optional[List[str]], default=None): A list of positional (token-level) attributes to display. Defaults to all positional attributes.
    - metadata_attrs (Optional[List[str]], default=None): A list of structural (metadata-level) attributes to display. Defaults to all structural attributes.
    - corpus (ccc.Corpus): An already initialized cwb_ccc Corpus object (use this at own risk)
    - context: Number of tokens of left and right context to include (defaults to 20 as in cwb-ccc)

    Updates the following attributes of the Concordance object:
    - self.query: The query string used.
    - self.data: A DataFrame containing the concordance lines.
    - self.tokens: A DataFrame containing token-level information.
    - self.active_node: Set to the root node of the analysis tree.
    - self.labels: An ordered dictionary initialized to empty.
    """

    from ccc import Corpus

    # Set the registry directory from the configuration if not provided
    if registry_dir is None:
        registry_dir = CONFIG.get('Paths', 'CWB_REGISTRY_DIR')

    # Load the corpus based on the provided directory and corpus name
    if not corpus:
        corpus = Corpus(corpus_name=corpus_name, registry_dir=registry_dir)

    # Set default metadata and token-level attributes if not provided
    if metadata_attrs is None:
        metadata_attrs = list(
            corpus.available_attributes().loc[corpus.available_attributes()['type'] == 's-Att', 'attribute'])
    if tokens_attrs is None:
        tokens_attrs = list(
            corpus.available_attributes().loc[corpus.available_attributes()['type'] == 'p-Att', 'attribute'])

    # Execute the query on the corpus
    dump = corpus.query(query, context=context)

    # Convert the results of the query to a dataframe
    df = dump.concordance(p_show=tokens_attrs, s_show=list(metadata_attrs), cut_off=len(dump.df), form="dataframe")

    # Rename metadata columns if provided
    if isinstance(metadata_attrs, dict):
        df.rename(columns=metadata_attrs, inplace=True)

    # Format the dataframe using the `format_concordance_line` function for display
    df["displayString"] = df["dataframe"].apply(format_concordance_line)
    df["displayStringTripartite"] = df["dataframe"].apply(format_concordance_line, args=(True,))

    # Assign a unique ID to each row in the dataframe and set it as index
    # ... but FlexiConc now expects a real column `line_id` with this information
    df["line_id"] = df["id"] = range(len(df))
    df.set_index("id", inplace=True)

    # Extract tokens and associate them with their respective line IDs
    token_dfs = []
    for index, nested_df in df['dataframe'].items():
        # Ensure 'cpos' is a column and not an index
        nested_df = nested_df.reset_index() if 'cpos' in nested_df.index.names else nested_df

        # Calculate 'id_in_line' as the difference between 'cpos' and 'context'
        nested_df = nested_df.assign(line_id=index)
        nested_df['id_in_line'] = nested_df['cpos'] - df.loc[index, 'context']

        token_dfs.append(nested_df)

    tokens = pd.concat(token_dfs).reset_index(drop=True)
    tokens.index.name = 'id'

    # Rename token-level columns if provided
    if isinstance(tokens_attrs, dict):
        df.rename(columns=tokens_attrs, inplace=True)

    # Create the matches DataFrame using the index directly for aggregation
    matches = tokens[tokens['offset'] == 0].groupby('line_id').apply(
        lambda group: pd.Series({
            'match_start': group.index.min(),  # Get the minimum index value for match_start
            'match_end': group.index.max()  # Get the maximum index value for match_end
        })
    ).reset_index()

    # Add 'slot' column to the matches DataFrame and populate it with 0's
    matches['slot'] = 0

    # Remove the 'dataframe' column before assigning metadata
    df.drop(columns=['dataframe'], inplace=True)

    # Update the object's attributes with the resulting data
    self.metadata = df
    self.tokens = tokens
    self.matches = matches
    self.info["query"] = query
    self.root = AnalysisTreeNode(id=0, node_type="subset", parent=None, concordance=self, line_count=len(self.metadata), label="root", selected_lines=list(range(len(self.metadata))))
    self.node_counter = 1


def retrieve_from_clic(
    self,
    query: List[str],
    corpora: str,
    subset: str = "all",
    contextsize: int = 20,
    api_base_url: str = "https://clic-fiction.com/api/concordance",
    # api_base_url: str = "https://clic.bham.ac.uk/api/concordance",
    metadata_attrs: Optional[List[str]] = None,
    tokens_attrs: Optional[List[str]] = None,
) -> None:
    """
    Retrieves a concordance from the CLiC API, processes the data, and updates the Concordance object.

    Parameters:
      - query (List[str]): The query strings used to retrieve concordance lines.
      - corpora (str): The corpus or corpora to search within.
      - subset (str): The subset of the corpora to search ('all', 'quote', 'nonquote', 'shortsus', 'longsus').
      - contextsize (int): The number of context words on each side.
      - api_base_url (str): The base URL of the CLiC API.
      - metadata_attrs (Optional[List[str]]): List of metadata attributes to include.
      - tokens_attrs (Optional[List[str]]): List of token-level attributes to include.

    Updates:
      - self.metadata: DataFrame of structural metadata.
      - self.tokens: DataFrame of token-level information.
      - self.matches: DataFrame of match information.
      - self.info["query"]: Stores the query used.
      - self.root: Initializes the analysis tree with a root node.
    """
    import requests
    import pandas as pd
    import re
    import string

    if metadata_attrs is None:
        metadata_attrs = ['text_id', 'chapter', 'paragraph', 'sentence']
    if tokens_attrs is None:
        tokens_attrs = ['word']

    data = []
    for q in query:
        params = {
            'q': q,
            'corpora': corpora,
            'subset': subset,
            'contextsize': contextsize
        }
        response = requests.get(api_base_url, params=params)
        response.raise_for_status()
        data += response.json().get('data', [])

    if not data:
        raise ValueError(f"No data returned from CLiC API for the provided set of queries.")

    metadata_list = []
    token_entries = []
    matches_list = []
    global_token_id = 0
    token_pattern = re.compile(r'(\w+(?:-\w+)?|[^\w\s]+)')

    for line_id, line_data in enumerate(data):
        left_context = line_data[0]
        node = line_data[1]
        right_context = line_data[2]
        corpus_info = line_data[3]
        structural_info = line_data[4]

        corpus_name = corpus_info[0]
        cpos_start = corpus_info[1]
        cpos_end = corpus_info[2]

        chapter = structural_info[0] if len(structural_info) > 0 else None
        paragraph = structural_info[1] if len(structural_info) > 1 else None
        sentence = structural_info[2] if len(structural_info) > 2 else None

        metadata_entry = {
            'line_id': line_id,
            'text_id': corpus_name,
            'chapter': chapter,
            'paragraph': paragraph,
            'sentence': sentence
        }
        metadata_list.append(metadata_entry)

        id_in_line = 0

        def process_context(context_data, context_type):
            nonlocal id_in_line, global_token_id
            context_items = context_data[:-1]
            offsets_info = context_data[-1]
            context_str = ''.join(context_items)
            split_tokens = token_pattern.findall(context_str)
            tokens_list = [t for t in split_tokens if t.strip() != '' and not re.match(r'\s', t)]
            num_tokens = len(tokens_list)
            if context_type == 'left':
                offsets_list = list(range(-num_tokens, 0))
            elif context_type == 'node':
                offsets_list = [0] * num_tokens
            elif context_type == 'right':
                offsets_list = list(range(1, num_tokens + 1))
            else:
                raise ValueError("Invalid context_type.")
            tokens_result = []
            for tok, off in zip(tokens_list, offsets_list):
                token_entry = {
                    'id': global_token_id,
                    'id_in_line': id_in_line,
                    'line_id': line_id,
                    'offset': off,
                    'word': tok
                }
                tokens_result.append(token_entry)
                id_in_line += 1
                global_token_id += 1
            return tokens_result

        left_tokens = process_context(left_context, 'left')
        node_tokens = process_context(node, 'node')
        right_tokens = process_context(right_context, 'right')

        # If the last token in the node is a punctuation mark (or a combination of punctuation),
        # move it to the right context and adjust offsets and id_in_line accordingly.
        if node_tokens and all(c in string.punctuation for c in node_tokens[-1]['word']):
            punct_token = node_tokens.pop()
            punct_token['offset'] = 1
            for token in right_tokens:
                token['offset'] += 1
                token['id_in_line'] += 1
            punct_token['id_in_line'] = 1
            right_tokens.insert(0, punct_token)

        line_tokens = left_tokens + node_tokens + right_tokens
        token_entries.extend(line_tokens)

        if node_tokens:
            match_start_id = node_tokens[0]['id']
            match_end_id = node_tokens[-1]['id']
        else:
            match_start_id = None
            match_end_id = None

        matches_entry = {
            'line_id': line_id,
            'match_start': match_start_id,
            'match_end': match_end_id,
            'slot': 0
        }
        matches_list.append(matches_entry)

    tokens_df = pd.DataFrame(token_entries)
    tokens_df.set_index('id', inplace=True)
    metadata_df = pd.DataFrame(metadata_list)
    matches_df = pd.DataFrame(matches_list)

    self.metadata = metadata_df
    self.tokens = tokens_df
    self.matches = matches_df
    self.info["query"] = query
    self.root = AnalysisTreeNode(
        id=0,
        node_type="subset",
        parent=None,
        concordance=self,
        line_count=len(self.metadata),
        label="root",
        selected_lines=list(range(len(self.metadata)))
    )
    self.node_counter = 1

import time

def retrieve_from_cwb_with_timing(
        self,
        registry_dir=None,
        corpus_name="",
        query="",
        tokens_attrs=None,
        metadata_attrs=None,
        corpus=None,
        context=20,
):
    from ccc import Corpus

    times = {}
    start = time.perf_counter()

    if registry_dir is None:
        registry_dir = CONFIG.get('Paths', 'CWB_REGISTRY_DIR')
    times['config'] = time.perf_counter() - start

    start = time.perf_counter()
    if not corpus:
        corpus = Corpus(corpus_name=corpus_name, registry_dir=registry_dir)
    times['corpus_load'] = time.perf_counter() - start

    start = time.perf_counter()
    if metadata_attrs is None:
        metadata_attrs = list(
            corpus.available_attributes().loc[corpus.available_attributes()['type'] == 's-Att', 'attribute'])
    if tokens_attrs is None:
        tokens_attrs = list(
            corpus.available_attributes().loc[corpus.available_attributes()['type'] == 'p-Att', 'attribute'])
    times['attr_load'] = time.perf_counter() - start

    start = time.perf_counter()
    dump = corpus.query(query, context=context)
    times['query'] = time.perf_counter() - start
    print(times['query'])

    start = time.perf_counter()
    df = dump.concordance(p_show=tokens_attrs, s_show=list(metadata_attrs), cut_off=len(dump.df), form="dataframe")
    times['concordance_generation'] = time.perf_counter() - start
    print(times['concordance_generation'])

    start = time.perf_counter()
    df["displayString"] = df["dataframe"].apply(format_concordance_line)
    df["displayStringTripartite"] = df["dataframe"].apply(format_concordance_line, args=(True,))
    df["line_id"] = df["id"] = range(len(df))
    df.set_index("id", inplace=True)
    times['generating_strings'] = time.perf_counter() - start
    print(times['generating_strings'])

    start = time.perf_counter()

    context_map = df['context'].to_dict()  # Much faster to look up in a dict than Series

    records = []
    for index, nested_df in df['dataframe'].items():
        df_flat = nested_df.reset_index()
        ctx = context_map[index]
        df_flat['line_id'] = index
        df_flat['id_in_line'] = df_flat['cpos'] - ctx
        records.append(df_flat)

    tokens = pd.concat(records, ignore_index=True)
    tokens.index.name = 'id'

    times['unnesting_dataframes'] = time.perf_counter() - start
    print(times['unnesting_dataframes'])


    start = time.perf_counter()
    matches = tokens[tokens['offset'] == 0].groupby('line_id').apply(
        lambda group: pd.Series({
            'match_start': group.index.min(),
            'match_end': group.index.max()
        })
    ).reset_index()
    matches['slot'] = 0
    df.drop(columns=['dataframe'], inplace=True)
    times['matches_processing'] = time.perf_counter() - start

    start = time.perf_counter()
    self.metadata = df
    self.tokens = tokens
    self.matches = matches
    self.info["query"] = query
    self.root = AnalysisTreeNode(id=0, node_type="subset", parent=None, concordance=self,
                                  line_count=len(self.metadata), label="root",
                                  selected_lines=list(range(len(self.metadata))))
    self.node_counter = 1
    times['finalize'] = time.perf_counter() - start

    print("Benchmarking results (seconds):")
    for k, v in times.items():
        print(f"{k}: {v:.4f}")


def retrieve_from_sketchengine(
    self,
    query: str,
    corpus: str = "preloaded/bnc2",
    kwicleftctx: str = "100#",  # contrary to the API documentation, this is the number of non-space characters to the left of the node and should be entered as a string ending in #
    kwicrightctx: str = "100#",  # same
    structs: str = "s",
    api_username: str = "anonymous",
    api_key: str = "",
    fetch_metadata: bool = False,
) -> None:
    """Retrieve a concordance from SketchEngine
    """

    import requests
    import pandas as pd
    import re
    import json
    from collections import defaultdict

    # ------------------------------------------------------------------
    #  helpers
    # ------------------------------------------------------------------
    def decode_escaped(text):
        if not isinstance(text, str):
            return text
        return text  # previously attempted unicode-escape decoding – not needed any more

    def parse_attr_string(attr_str, attrs):
        fields = decode_escaped(attr_str).strip("/").split("/")
        if len(attrs) - 1 != len(fields):  # "word" is not part of attr string
            fields = [""] * (len(attrs) - 1)
        return dict(zip(attrs[1:], fields))

    # ------------------------------------------------------------------
    #  API request – get attributes and concordance lines
    # ------------------------------------------------------------------
    base_url = "https://api.sketchengine.eu"
    auth = (api_username, api_key)

    info = requests.get(
        f"{base_url}/search/corp_info",
        params={"corpname": corpus, "format": "json"},
        auth=auth,
    ).json()
    attrs = ["word"] + [attr["name"] for attr in info["attributes"] if attr["name"] != "word"]

    metadata_attr_set: set[str] = set()
    docstructure = info.get("docstructure")
    if docstructure:
        for struct in info.get("structures", []):
            if struct.get("name") == docstructure:
                # every attribute of the docstructure becomes
                #   <docstructure>.<attr>
                for attr in struct.get("attributes", []):
                    metadata_attr_set.add(f"{docstructure}.{attr['name']}")
                break
    metadata_attr_list = sorted(a for a in metadata_attr_set if a)
    refs_param = ",".join(f"={a}" for a in metadata_attr_list)

    page_size, fromp, all_lines = 1000, 1, []
    while True:
        response = requests.get(
            f"{base_url}/search/concordance",
            params={
                "corpname": corpus,
                "q": f"q{query}",
                "format": "json",
                "attrs": ",".join(attrs),
                "ctxattrs": ",".join(attrs),
                "pagesize": page_size,
                "kwicleftctx": kwicleftctx,
                "kwicrightctx": kwicrightctx,
                "fromp": fromp,
                "refs": refs_param,
                "structs": structs,
            },
            auth=auth,
        ).json()
        lines = response.get("Lines", [])
        if not lines:
            break
        all_lines.extend(lines)
        fromp += 1

    # ------------------------------------------------------------------
    #  set‑up for structure tracking
    # ------------------------------------------------------------------
    struct_names = [s.strip() for s in structs.split(",") if s.strip()]
    # Map struct → regex that signals *any* boundary of that struct
    struct_re = {
        s: re.compile(rf"</?{re.escape(s)}(?=[ >])|</?{re.escape(s)}>?") for s in struct_names
    }

    # kwic_struct_vals[struct][line_id]  →  set(counter values occurring in KWIC)
    kwic_struct_vals = {s: defaultdict(set) for s in struct_names}

    tokens, matches_rows, metadata_rows = [], [], []
    global_token_index = 0

    # ------------------------------------------------------------------
    #  token collector (captures counters & KWIC info) -------------------
    # ------------------------------------------------------------------
    def collect_tokens(toklist, line_id, id_in_line, is_kwic, counters):
        nonlocal global_token_index
        result = []
        for tok in toklist:
            # 1️⃣  structural boundary → update counters, skip row
            if "strc" in tok:
                strc_text = tok["strc"]
                for s, pat in struct_re.items():
                    if pat.search(strc_text):
                        counters[s] += 1
                continue

            # 2️⃣  ordinary token → build dataframe row
            if "str" not in tok:
                continue
            raw = decode_escaped(tok["str"])
            m = re.match(r"^(\s*)(\S.*?)$", raw)
            space_before, word = (m.group(1), m.group(2)) if m else ("", raw.strip())
            attr_values = parse_attr_string(tok.get("attr", ""), attrs)

            row = {
                "id": global_token_index,
                "line_id": line_id,
                "id_in_line": id_in_line,
                "word": word,
                "space_before": space_before,
                "is_kwic": int(is_kwic),
                **attr_values,
            }
            # attach current counter snapshot
            for s in struct_names:
                row[f"{s}_num"] = counters[s]
                if is_kwic:
                    kwic_struct_vals[s][line_id].add(counters[s])

            result.append(row)
            global_token_index += 1
            id_in_line += 1
        return result, id_in_line

    # ------------------------------------------------------------------
    #  main loop over concordance lines ---------------------------------
    # ------------------------------------------------------------------
    for line_id, line in enumerate(all_lines):
        counters = {s: 0 for s in struct_names}
        id_in_line = 0

        left_tokens, id_in_line = collect_tokens(line.get("Left", []), line_id, id_in_line, False, counters)
        kwic_tokens, id_in_line = collect_tokens(line.get("Kwic", []), line_id, id_in_line, True, counters)
        right_tokens, _ = collect_tokens(line.get("Right", []), line_id, id_in_line, False, counters)

        tokens.extend(left_tokens + kwic_tokens + right_tokens)

        # record match span (ids refer to global_token_index values assigned above)
        matches_rows.append(
            {
                "line_id": line_id,
                "match_start": kwic_tokens[0]["id"],
                "match_end": kwic_tokens[-1]["id"],
                "slot": 0,
            }
        )

        # metadata for the line
        meta = {"line_id": line_id}
        if "Refs" in line:
            meta.update(dict(zip(metadata_attr_list, line["Refs"])))
        metadata_rows.append(meta)

    # ------------------------------------------------------------------
    #  build dataframes --------------------------------------------------
    # ------------------------------------------------------------------
    tokens_df = pd.DataFrame(tokens).set_index("id")
    matches_df = pd.DataFrame(matches_rows)
    metadata_df = pd.DataFrame(metadata_rows)

    # Compute offset column (slot is always 0 here)
    matches_slot = matches_df[matches_df['slot'] == 0].groupby('line_id').first().reset_index()
    tokens_df = tokens_df.reset_index()

    # Merge to attach match_start and match_end
    tokens_df = tokens_df.merge(matches_slot[['line_id', 'match_start', 'match_end']], on='line_id', how='left')

    # Compute offset
    tokens_df['offset'] = tokens_df.apply(
        lambda row: 0 if pd.isnull(row['match_start']) or pd.isnull(row['match_end'])
        else (row['id'] - row['match_start'] if row['id'] < row['match_start']
              else row['id'] - row['match_end'] if row['id'] > row['match_end']
        else 0),
        axis=1
    )

    # Drop match_start/match_end
    tokens_df.drop(columns=['match_start', 'match_end'], inplace=True)

    # Set index again
    tokens_df = tokens_df.set_index('id')

    # indicator columns same_<struct>
    for s in struct_names:
        col_num = f"{s}_num"
        same_col = f"same_{s}"
        def same_func(row, struct=s, num_col=col_num):
            return int(row[num_col] in kwic_struct_vals[struct][row["line_id"]])
        tokens_df[same_col] = tokens_df.apply(same_func, axis=1)
        tokens_df.drop(columns=[col_num], inplace=True)

    # clean‑up helper columns
    tokens_df.drop(columns=["is_kwic"], inplace=True)

    # ------------------------------------------------------------------
    #  METADATA CLEAN-UP  · convert numeric-looking metadata columns
    # ------------------------------------------------------------------
    for col in metadata_df.columns:
        if metadata_df[col].dtype == object:
            # try to convert – NaNs mark cells that were not numeric
            num = pd.to_numeric(metadata_df[col], errors="coerce")

            # decide whether conversion "makes sense"
            valid = num.notna().sum()
            if valid == 0:  # nothing parsed
                continue
            if valid == len(metadata_df):  # every row numeric
                metadata_df[col] = num
            else:
                # mixed column → convert if ≥95 % rows numeric
                if valid / len(metadata_df) >= 0.95:
                    metadata_df[col] = num
                # else: leave as object/string

    # ------------------------------------------------------------------
    #  attach to Concordance instance -----------------------------------
    # ------------------------------------------------------------------
    self.metadata = metadata_df
    self.tokens = tokens_df
    self.matches = matches_df
    self.info["query"] = query
    self.root = AnalysisTreeNode(
        id=0,
        node_type="subset",
        parent=None,
        concordance=self,
        label="root",
        selected_lines=list(range(len(metadata_df))),
        line_count=len(metadata_df),
    )
    self.node_counter = 1
