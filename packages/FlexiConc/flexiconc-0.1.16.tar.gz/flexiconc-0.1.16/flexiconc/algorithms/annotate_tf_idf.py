from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

def annotate_tf_idf(conc, **args) -> pd.Series:
    """
    Annotates a concordance with TF-IDF vectors computed for each line based on tokens in a specified window.

    Args are dynamically validated and extracted from the schema.

    Parameters:
    - conc (Union[Concordance, ConcordanceSubset]): The full concordance or a subset of it.
    - args (dict): Arguments include:
        - tokens_attribute (str): The token attribute to use for creating line texts. Default is 'word'.
        - exclude_values_attribute (str, optional): The attribute to filter out specific values.
        - exclude_values_list (list, optional): The list of values to exclude.
        - window_start (int): The lower bound of the token window (inclusive). Default is -5.
        - window_end (int): The upper bound of the token window (inclusive). Default is 5.
        - include_node (bool): Whether to include the node token (offset 0). Default is True.

    Returns:
    - pd.Series: A Pandas Series indexed by concordance line IDs, containing the TF-IDF vectors for each line.
    """

    # Metadata for the algorithm
    annotate_tf_idf._algorithm_metadata = {
        "name": "Annotate with TF-IDF",
        "description": "Computes TF-IDF vectors for each line based on tokens in a specified window.",
        "algorithm_type": "annotation",
        "scope": "line",
        "requires": ["scikit_learn>=1.3.0"],
        "args_schema": {
            "type": "object",
            "properties": {
                "tokens_attribute": {
                    "type": "string",
                    "description": "The token attribute to use for creating line texts.",
                    "default": "word",
                    "x-eval": "dict(enum=list(set(conc.tokens.columns) - {'id_in_line', 'line_id', 'offset'}))"
                },
                "exclude_values_attribute": {
                    "type": ["string"],
                    "description": "The attribute to filter out specific values."
                },
                "exclude_values_list": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The list of values to exclude."
                },
                "window_start": {
                    "type": "integer",
                    "description": "The lower bound of the token window (inclusive).",
                    "default": -5,
                    "x-eval": "dict(minimum=min(conc.tokens['offset']))"
                },
                "window_end": {
                    "type": "integer",
                    "description": "The upper bound of the token window (inclusive).",
                    "default": 5,
                    "x-eval": "dict(maximum=max(conc.tokens['offset']))"
                },
                "include_node": {
                    "type": "boolean",
                    "description": "Whether to include the node token (offset 0).",
                    "default": True
                }
            },
            "required": []
        }
    }

    # Extract arguments
    tokens_attribute = args.get("tokens_attribute", "word")
    exclude_values_attribute = args.get("exclude_values_attribute", None)
    exclude_values_list = args.get("exclude_values_list", None)
    window_start = args.get("window_start", -5)
    window_end = args.get("window_end", 5)
    include_node = args.get("include_node", True)

    # Extract lines
    subset_tokens = conc.tokens[
        (conc.tokens['offset'] >= window_start) & (conc.tokens['offset'] <= window_end)
    ]
    if not include_node:
        subset_tokens = subset_tokens[subset_tokens['offset'] != 0]
    if exclude_values_attribute and exclude_values_list:
        subset_tokens = subset_tokens[~subset_tokens[exclude_values_attribute].isin(exclude_values_list)]

    # Group tokens by line_id
    lines = subset_tokens.groupby('line_id')[tokens_attribute].apply(lambda x: ' '.join(x))
    line_ids = lines.index.tolist()

    # Compute TF-IDF vectors
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(lines)

    # Convert the sparse matrix to a list of dense vectors
    tf_idf_vectors = [X[i].toarray()[0] for i in range(X.shape[0])]

    # Create a Pandas Series indexed by line IDs
    tf_idf_series = pd.Series(data=tf_idf_vectors, index=line_ids, name="data")

    return tf_idf_series