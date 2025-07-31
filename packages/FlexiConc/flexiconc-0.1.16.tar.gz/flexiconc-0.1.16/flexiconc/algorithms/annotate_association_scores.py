import numpy as np
import pandas as pd


def annotate_association_scores(conc, **args) -> dict:
    """
    Computes token–level association scores (currently, local mutual information) from two
    pre-existing FlexiConc frequency lists:

        local-MI = O * log(O / E)

    where O is the observed frequency in the concordance and E = (rel_f in the *reference* list) × N with N being the total number of tokens in the target list.

    The function returns a *resource dictionary*::

        {
            "type": "scores",
            "df":   <pandas.DataFrame>,
            "info": <args-dict>
        }
    """

    # ------------------------------------------------------------------ metadata
    annotate_association_scores._algorithm_metadata = {
        "name": "Annotate Association Scores",
        "description": (
            "Computes association scores from two "
            "frequency lists (concordance and whole corpus)."
        ),
        "algorithm_type": "annotation",
        "scope": "type",
        "args_schema": {
            "type": "object",
            "properties": {
                "corpus_frequency_list": {
                    "type": "string",
                    "description": "Name of the *corpus* frequency list "
                                   "registered in `conc.resources`.",
                    "x-eval": (
                        "dict(enum=conc.resources.list('frequency_list'))"
                    ),
                },
                "concordance_frequency_list": {
                    "type": "string",
                    "description": "Name of the *concordance* frequency list "
                                   "registered in `conc.resources`.",
                    "x-eval": (
                        "dict(enum=conc.resources.list('frequency_list'))"
                    ),
                },
                "token_attribute": {
                    "type": "string",
                    "description": "Token attribute column common to both lists.",
               },
                "ignore_case": {
                    "type": "boolean",
                    "description": "Lowercase all string tokens before matching",
                    "default": True
                }
            },
            "required": ["corpus_frequency_list", "concordance_frequency_list"],
        },
    }

    corpus_freq_name          = args["corpus_frequency_list"]
    concordance_freq_name     = args["concordance_frequency_list"]
    token_attr                = args.get("token_attribute", "word")
    ignore_case               = args.get("ignore_case", True)

    corpus_freq_df = conc.resources.get_frequency_list(corpus_freq_name,
                                         frequency_columns=("rel_f",),
                                         token_attribute_columns=(token_attr,),
                                         ignore_case=ignore_case)
    concordance_freq_df = conc.resources.get_frequency_list(concordance_freq_name,
                                         frequency_columns=("f",),
                                         token_attribute_columns=(token_attr,),
                                         ignore_case=ignore_case                   )

    N = conc.resources.get_frequency_list_info(concordance_freq_name)["sample_size"]

    merged = concordance_freq_df.merge(corpus_freq_df, how="left", on=token_attr, suffixes=("_concordance", "_corpus"))
    merged["rel_f"] = merged["rel_f"].fillna(0.0)
    merged["E"] = merged["rel_f"] * N
    merged["O"] = merged["f"]

    with np.errstate(divide="ignore", invalid="ignore"):
        O = merged["O"]
        E = merged["E"]

        # compute all simple association scores from Evert (2007) as well as log-transformed local MI

        merged["MI"] = np.log2(np.where((O > 0) & (E > 0), O / E, 1.0))
        merged["MI3"] = np.log2(np.where((O > 0) & (E > 0), O**3 / E, 1.0))
        merged["local_MI"] = O * merged["MI"]
        merged["log_local_MI"] = np.sign(merged["local_MI"]) * np.log1p(np.abs(merged["local_MI"]))
        merged["z_score"] = (O - E) / np.sqrt(E)
        merged["t_score"] = (O - E) / np.sqrt(O)
        merged["simple_ll"] = 2 * (O * np.log(np.where((O > 0) & (E > 0), O / E, 1.0)) - (O - E))

    merged.loc[:, ["MI", "MI3", "local_MI", "log_local_MI", "z_score", "t_score", "simple_ll"]] = (
        merged[["MI", "MI3", "local_MI", "log_local_MI", "z_score", "t_score", "simple_ll"]].fillna(0.0)
    )

    out_cols = [token_attr, "MI", "MI3", "local_MI", "log_local_MI", "z_score", "t_score", "simple_ll", "O", "E"]
    df_scores = merged[out_cols].sort_values("log_local_MI", ascending=False).reset_index(drop=True)

    resource_dict = {
        "type": "scores",
        "df": df_scores,
        "info": {
            **args,
            "corpus_size": conc.resources.get_frequency_list_info(corpus_freq_name)["sample_size"],
            "concordance_token_count": N,
        },
    }
    return resource_dict