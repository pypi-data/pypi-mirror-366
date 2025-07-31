import operator

def select_by_sort(conc, **args):
    """
    Selects lines based on sort keys obtained from the active_node's ordering_result['sort_keys'],
    using a comparison operator and a specified value.

    Args are dynamically validated and extracted from the schema.

    Parameters:
        conc (Union[Concordance, ConcordanceSubset]): The concordance or subset of data.
        args (dict): Arguments include:
            - comparison_operator (str): The comparison operator ('==', '<=', '>=', '<', '>'). Default is "==".
            - value (number): The value to compare the sort keys against. Default is 0.

    Returns:
        dict: A dictionary containing:
            - "selected_lines": A sorted list of selected line IDs.
            - "line_count": The total number of selected lines.
    """
    # Metadata for the algorithm
    select_by_sort._algorithm_metadata = {
        "name": "Select by Sort Keys",
        "description": (
            "Selects lines based on sort keys obtained from the active node's ordering_result['sort_keys'], "
            "using a comparison operator and a specified value."
        ),
        "algorithm_type": "selecting",
        "status": "experimental",
        "args_schema": {
            "type": "object",
            "properties": {
                "comparison_operator": {
                    "type": "string",
                    "enum": ["==", "<=", ">=", "<", ">"],
                    "description": "The comparison operator to use for sort keys.",
                    "default": "=="
                },
                "value": {
                    "type": "number",
                    "description": "The value to compare the sort keys against.",
                    "default": 0
                }
            },
            "required": []
        }
    }

    active_node = conc.active_node
    comparison_operator = args.get("comparison_operator", "==")
    value = args.get("value", 0)

    if not hasattr(active_node, "ordering_result") or "sort_keys" not in active_node.ordering_result:
        raise ValueError("The active_node does not contain an ordering_result with 'sort_keys'.")

    sort_keys = active_node.ordering_result["sort_keys"]

    ops = {
        "==": operator.eq,
        "<=": operator.le,
        ">=": operator.ge,
        "<": operator.lt,
        ">": operator.gt
    }
    comp_func = ops[comparison_operator]
    selected_lines = [line_id for line_id, sort_value in sort_keys.items() if comp_func(sort_value, value)]

    return {
        "selected_lines": sorted(selected_lines)
    }
