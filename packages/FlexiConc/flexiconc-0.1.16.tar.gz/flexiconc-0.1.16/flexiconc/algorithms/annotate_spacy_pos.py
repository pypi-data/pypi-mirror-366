import spacy
import pandas as pd


def annotate_spacy_pos(conc, **args):
    """
    Annotates tokens with spaCy part-of-speech (POS) tags or related attributes.
    This algorithm uses spaCy to determine the tag information for each token in the specified token attribute.
    The spacy_attributes argument is always treated as a list: even if a single attribute is desired,
    it should be provided as a one-element list. The algorithm returns a DataFrame with each column corresponding
    to one of the requested attributes. The scope for this annotation is "token".

    Parameters:
        conc (Concordance or ConcordanceSubset): The concordance data.
        args (dict): A dictionary of arguments with the following keys:
            - spacy_model (str): The spaCy model to use for POS tagging. Default is "en_core_web_sm".
            - tokens_attribute (str): The token attribute to use for POS tagging. Default is "word".
            - spacy_attributes (list of str): A list of spaCy token attributes to retrieve.
              Allowed values are "pos_", "tag_", "morph", "dep_", "ent_type_". Default is ["pos_"].

    Returns:
        pd.DataFrame: A DataFrame indexed by token IDs with one column per requested attribute.
    """
    # Metadata for the algorithm
    annotate_spacy_pos._algorithm_metadata = {
        "name": "Annotate with spaCy POS tags",
        "description": (
            "Annotates tokens with spaCy part-of-speech tags or related tag information using a specified spaCy model. "
            "The spacy_attributes parameter is always a list, so multiple annotations can be retrieved simultaneously."
        ),
        "algorithm_type": "annotation",
        "scope": "token",
        "requires": ["spacy>=3.8.4"],
        "args_schema": {
            "type": "object",
            "properties": {
                "spacy_model": {
                    "type": "string",
                    "description": "The spaCy model to use for POS tagging.",
                    "default": "en_core_web_sm"
                },
                "tokens_attribute": {
                    "type": "string",
                    "description": "The token attribute to use for POS tagging.",
                    "default": "word",
                    "x-eval": "dict(enum=list(set(conc.tokens.columns) - {'id_in_line', 'line_id', 'offset'}))"
                },
                "spacy_attributes": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["lemma_", "pos_", "tag_", "morph", "dep_", "ent_type_"]
                    },
                    "description": "A list of spaCy token attributes to retrieve for annotation.",
                    "default": ["pos_"]
                }
            },
            "required": ["spacy_model", "spacy_attributes"]
        }
    }

    # Extract arguments
    spacy_model = args.get("spacy_model", "en_core_web_sm")
    tokens_attribute = args.get("tokens_attribute", "word")
    spacy_attributes = args.get("spacy_attributes", ["pos_"])
    # Ensure spacy_attributes is a list.
    if not isinstance(spacy_attributes, list):
        spacy_attributes = [spacy_attributes]

    # Load the spaCy model.
    nlp = spacy.load(spacy_model)

    # Get the token values as strings from the specified token attribute.
    tokens_series = conc.tokens[tokens_attribute].astype(str)

    # Process tokens in batches.
    docs = list(nlp.pipe(tokens_series, batch_size=100))

    # Build results for each requested attribute.
    results = {attr: [] for attr in spacy_attributes}
    for doc in docs:
        if doc:
            for attr in spacy_attributes:
                results[attr].append(getattr(doc[0], attr))
        else:
            for attr in spacy_attributes:
                results[attr].append("")

    return pd.DataFrame(results, index=tokens_series.index)
