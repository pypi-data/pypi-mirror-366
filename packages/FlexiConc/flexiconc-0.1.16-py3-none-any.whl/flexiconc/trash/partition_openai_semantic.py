from pydantic import BaseModel
from openai import OpenAI
from typing import List

# Define the schema for structured outputs using Pydantic
class ClusteringResult(BaseModel):
    cluster_assignments: List[int]
    cluster_labels: List[str]

def partition_openai_semantic(conc, **args):
    """
    Sends a list of lines to OpenAI and requests clustering into `n_partitions` groups with labels,
    using structured outputs for guaranteed JSON schema adherence.

    Args are dynamically validated and extracted from the schema.

    Parameters:
    - conc (Union[Concordance, ConcordanceSubset]): The full concordance or a subset of it.
    - args (dict): Arguments include:
        - openai_api_key (str): The API key for OpenAI.
        - n_partitions (int): The number of partitions/clusters to create. Default is 5.
        - token_attr (str): The token attribute to use for creating line texts. Default is 'word'.
        - model (str): The OpenAI model to use. Default is 'gpt-4o-2024-11-20'.
        - introduction_line (str): Customizable prompt for the clustering task.

    Returns:
    - list: A list of dictionaries, where each dictionary contains:
        - "label": The label of the cluster.
        - "line_ids": A list of line IDs in the cluster.
    """

    # Metadata for the algorithm
    partition_openai_semantic._algorithm_metadata = {
        "name": "Partition with OpenAI",
        "description": "Sends a list of lines to OpenAI and requests clustering into n groups with labels, using structured outputs for guaranteed JSON schema adherence.",
        "algorithm_type": "partitioning",
        "status": "experimental",
        "requires": ["openai>=1.40.0", "pydantic>=1.8.2"],
        "args_schema": {
            "type": "object",
            "properties": {
                "openai_api_key": {
                    "type": "string",
                    "description": "The API key for OpenAI."
                },
                "n_partitions": {
                    "type": "integer",
                    "description": "The number of partitions/clusters to create.",
                    "default": 5,
                    "x-eval": "dict(maximum=node.line_count)"
                },
                "token_attr": {
                    "type": "string",
                    "description": "The token attribute to use for creating line texts.",
                    "default": "word",
                    "x-eval": "dict(enum=list(set(conc.tokens.columns) - {'id_in_line', 'line_id', 'offset'}))"
                },
                "model": {
                    "type": "string",
                    "description": "The OpenAI model to use.",
                    "default": "gpt-4o-2024-11-20"
                },
                "introduction_line": {
                    "type": "string",
                    "description": "Customizable prompt for the clustering task.",
                    "default": (
                        "You are given a list of lines of text. Cluster them into {n_partitions} clusters by "
                        "the pattern in which the node word occurs. Ensure that none of the {n_partitions} clusters is empty."
                    )
                }
            },
            "required": ["openai_api_key"]
        }
    }

    # Extract arguments
    openai_api_key = args["openai_api_key"]
    n_partitions = args.get("n_partitions", 5)
    token_attr = args.get("token_attr", "word")
    model = args.get("model", "gpt-4o-2024-11-20")
    introduction_line = args.get("introduction_line", (
        "You are given a list of lines of text. Cluster them into {n_partitions} clusters by "
        "the pattern in which the node word occurs. Ensure that none of the {n_partitions} clusters is empty."
    ))

    # Get line texts by joining tokens per line
    line_texts = (
        conc.tokens
        .groupby('line_id')[token_attr]
        .apply(lambda x: ' '.join(x))
        .reindex(conc.metadata.index, fill_value='')
        .tolist()
    )

    # Restrict to 60 lines maximum
    if len(line_texts) > 60:
        raise ValueError("Too many lines. Maximum allowed is 60.")

    client = OpenAI(api_key=openai_api_key)

    # Format the introduction line with the number of clusters
    intro = introduction_line.format(n_partitions=n_partitions)

    # Prepare the user prompt
    user_prompt = (
        f"{intro}\n\n"
        "Return ONLY the JSON object that matches the specified schema:\n"
        " - cluster_assignments: array of integers representing cluster index for each line in order\n"
        " - cluster_labels: array of strings representing the label of each cluster\n\n"
        "Lines:\n"
    )
    for i, line in enumerate(line_texts):
        user_prompt += f"{i}: {line}\n"

    user_prompt += (
        "\nYou must respond in valid JSON conforming to the schema. Do not include any extra text."
    )

    # Use structured output parsing
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": "You are a clustering assistant."},
            {"role": "user", "content": user_prompt},
        ],
        response_format=ClusteringResult,  # Produce output conforming to ClusteringResult schema
        temperature=0,
    )

    # Extract parsed result
    if completion.choices[0].message.parsed:
        result = completion.choices[0].message.parsed
        assignments = result.cluster_assignments
        labels = result.cluster_labels
    elif completion.choices[0].message.refusal:
        # Handle refusal
        raise ValueError("The model refused to comply with the request.")
    else:
        # Handle unexpected format
        raise ValueError("No valid structured response returned.")

    result = {"partitions":
        [
            {
                "id": idx,
                "label": labels[cluster_id] if cluster_id < len(labels) else f"Cluster_{cluster_id}",
                "line_ids": conc.metadata.index[[i for i, c in enumerate(assignments) if c == cluster_id]].tolist()
            }
            for idx, cluster_id in enumerate(sorted(set(assignments)))
        ]
    }

    return result
