def select_set_operation(conc, **args):
    """
    Performs a set operation (union, intersection, difference, disjunctive union, complement)
    on the sets of lines from specified nodes in the analysis tree.

    Args are dynamically validated and extracted from the schema.

    Parameters:
    - conc (Union[Concordance, ConcordanceSubset]): The concordance or subset of data.
    - args (dict): Arguments include:
        - operation_type (str): Type of set operation ('union', 'intersection', 'difference',
                                'disjunctive union', 'complement').
        - nodes (list): A list of nodes to retrieve selected lines from.

    Returns:
    - dict: A dictionary containing:
        - "selected_lines": A sorted list of line IDs resulting from the set operation.
        - "line_count": The total number of selected lines.
    """

    # Metadata for the algorithm
    select_set_operation._algorithm_metadata = {
        "name": "Set Operation",
        "description": (
            "Performs set operations (union, intersection, difference, disjunctive union, complement) "
            "on selected lines from specified nodes in the analysis tree."
        ),
        "algorithm_type": "selecting",
        "status": "experimental",
        "args_schema": {
            "type": "object",
            "properties": {
                "operation_type": {
                    "type": "string",
                    "enum": ["union", "intersection", "difference", "disjunctive union", "complement"],
                    "description": (
                        "The type of set operation to perform: 'union', 'intersection', 'difference', "
                        "'disjunctive union', or 'complement'."
                    )
                },
                "nodes": {
                    "type": "array",
                    "items": {},
                    "description": "A list of nodes to retrieve selected lines from."
                }
            },
            "required": ["operation_type", "nodes"]
        }
    }

    # Extract arguments
    operation_type = args["operation_type"]
    nodes = args["nodes"]
    active_node = conc.active_node

    # Ensure active_node is in the list of nodes
    if active_node not in nodes:
        raise ValueError("The active_node must be included in the list of nodes.")

    # Ensure operation_type is valid
    valid_operations = {"union", "intersection", "difference", "disjunctive union", "complement"}
    if operation_type not in valid_operations:
        raise ValueError(f"Invalid operation_type '{operation_type}'. Must be one of {valid_operations}.")

    # Ensure correct number of nodes for specific operations
    if operation_type in {"difference", "disjunctive union"} and len(nodes) != 2:
        raise ValueError(f"Operation '{operation_type}' requires exactly two nodes.")
    if operation_type == "complement" and len(nodes) != 1:
        raise ValueError("Operation 'complement' requires exactly one node.")

    # Retrieve sets of selected lines from the specified nodes
    line_sets = []
    for node in nodes:
        if hasattr(node, "selected_lines"):
            line_set = set(node.selected_lines)
        else:
            # If no 'selected_lines' attribute is found, default to all lines
            line_set = set(conc.metadata.index.tolist())
        line_sets.append(line_set)

    # Perform the specified set operation
    if operation_type == "union":
        result_set = set.union(*line_sets)
    elif operation_type == "intersection":
        result_set = set.intersection(*line_sets)
    elif operation_type == "difference":
        result_set = line_sets[0] - line_sets[1]
    elif operation_type == "disjunctive union":
        result_set = (line_sets[0] | line_sets[1]) - (line_sets[0] & line_sets[1])
    elif operation_type == "complement":
        all_lines = set(conc.metadata.index.tolist())
        result_set = all_lines - line_sets[0]
    else:
        raise ValueError(f"Unsupported operation_type '{operation_type}'.")

    # Convert the result set to a sorted list
    selected_lines = sorted(result_set)

    # Return the result
    return {
        "selected_lines": selected_lines
    }
