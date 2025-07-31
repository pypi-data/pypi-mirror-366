def export_analysis_tree_to_json(self, output_path: str, template: bool = True) -> None:
    """
    Export the analysis tree to a JSON file. If `template` is True, export only the structure and relevant attributes.
    If `template` is False, include the values provided by algorithms and all custom attributes.

    Parameters:
    - output_path (str): The path where the JSON file will be saved.
    - template (bool): If True, export only the structure. If False, include all attributes.
    """

    def node_to_dict(node: AnyNode, template: bool) -> Dict[str, Any]:
        """
        Convert a node and its children to a dictionary format, depending on the template parameter.

        Parameters:
        - node (AnyNode): The node to convert.
        - template (bool): Whether to include values from algorithms or only structure.

        Returns:
        - dict: The dictionary representation of the node.
        """
        node_dict = {
            'id': node.id,
            'type': node.type,
        }

        # For root nodes, include 'function' and 'args' instead of 'algorithms'
        if node.type in ['root', 'query', 'load']:
            node_dict['function'] = getattr(node, 'function', None)
            node_dict['args'] = getattr(node, 'args', {})
        else:
            node_dict['algorithms'] = getattr(node, 'algorithms', {})

        # If not in template mode, add all custom attributes except parent and children
        if not template:
            custom_attributes = {key: value for key, value in node.__dict__.items()
                                 if key not in ['parent', 'children']}
            node_dict.update(custom_attributes)

        # Recursively convert children
        if node.children:
            node_dict['children'] = [node_to_dict(child, template) for child in node.children]

        return node_dict

    # Convert the entire tree to a list of dictionaries starting from the root
    tree_data = [node_to_dict(node, template) for node in self.tree if node.parent is None]

    # Write the tree data to the output JSON file
    with open(output_path, 'w') as f:
        json.dump(tree_data, f, indent=4)


    def combine_order_algorithms(self, order_algorithms: List[Dict[str, Any]], node_id: int) -> Dict[str, Any]:
        """
        Combines and executes multiple 'order' algorithms into a single sorted order using Pandas for vectorized operations.
        Also provides information on how many adjacent line pairs are differentiated by each algorithm, and handles tie ranks correctly.
        If 'rank_keys' are present, it also includes them in the result with their original values.

        Parameters:
        - order_algorithms (List[Dict[str, Any]]): A list of dictionaries specifying the order algorithms to combine.

        Returns:
        - dict: A dictionary containing:
            - "sort_keys": A mapping from line IDs to their final sorted ranks, resolving ties.
            - "differentiation_info": How many pairs were differentiated by each algorithm.
            - "rank_keys": Original rank keys, if any were present in the algorithms.
        """
        if not order_algorithms:
            return {"sort_keys": {}, "differentiation_info": {}, "rank_keys": {}}

        # Initialize a DataFrame to store the sorting keys for each algorithm
        sort_df = pd.DataFrame()
        rank_keys_dict = {}

        # Apply each order algorithm and store the results in the DataFrame using a unique column index
        for algo_idx, algo in enumerate(order_algorithms):
            algo_result = self.apply_algorithm(algo['algorithm_name'], algo['args'], node_id = node_id)

            if 'sort_keys' in algo_result:
                # Use the index `algo_idx` as the column identifier instead of the algorithm name
                sort_df[algo_idx] = pd.Series(algo_result['sort_keys'])
            elif 'rank_keys' in algo_result:
                # Negate the rank keys to treat them as sort keys
                sort_df[algo_idx] = -pd.Series(algo_result['rank_keys'])
                # Store the original rank keys for output
                rank_keys_dict[f"algo_{algo_idx}"] = algo_result['rank_keys']
            else:
                print(f"Order algorithm '{algo['algorithm_name']}' did not return valid sort or rank keys.")
                continue

        # Ensure the DataFrame is filled and aligned (handling any missing line IDs)
        sort_df.fillna(float('inf'), inplace=True)  # Use a large value to handle missing keys

        # Sort the DataFrame based on the columns (now indexed by `algo_idx`), resolving ties by subsequent algorithms
        sort_df = sort_df.sort_values(by=list(sort_df.columns))

        # Initialize rank and assign it to the first row
        sorted_line_ids = sort_df.index.tolist()
        final_sort_keys = {}
        current_rank = 0

        # List to track how many pairs are differentiated by each algorithm
        differentiation_info = [0] * len(order_algorithms)

        # Iterate over sorted line IDs and handle ties
        i = 0
        while i < len(sorted_line_ids):
            start = i
            # Look ahead to see if there are ties (same values across all columns)
            while i < len(sorted_line_ids) - 1 and sort_df.iloc[i].equals(sort_df.iloc[i + 1]):
                i += 1

            # Assign the current rank to all tied rows
            for j in range(start, i + 1):
                final_sort_keys[sorted_line_ids[j]] = current_rank + 1

            # Increment the rank by the number of tied rows
            current_rank += (i - start + 1)

            # Now, check which algorithm differentiates the current group from the previous one
            if start != 0:
                for algo_idx in sort_df.columns:
                    # Compare current row's algorithm result to the previous row's result for the same algorithm
                    if sort_df.iloc[start][algo_idx] != sort_df.iloc[start - 1][algo_idx]:
                        differentiation_info[algo_idx] += 1
                        break  # Stop checking further algorithms once differentiation is found

            # Move to the next group of rows
            i += 1

        # Prepare the final output with sort keys, differentiation info, and rank keys (if any)
        result = {
            "sort_keys": final_sort_keys,
            "differentiation_info": {f"algo_{i}": differentiation_info[i] for i in range(len(differentiation_info))}
        }

        if rank_keys_dict:
            result["rank_keys"] = rank_keys_dict

        return result


    def combine_select_algorithms(self, select_algorithms: List[Dict[str, Any]], node_id: int) -> Dict[str, Dict[int, int]]:
        """
        Combines and executes multiple selection algorithms into a single output by applying logical AND on their selections.

        Parameters:
        - select_algorithms (List[Dict[str, Any]]): A list of dictionaries specifying the selection algorithms to combine.

        Returns:
        - dict: A dictionary containing the combined selection result for each line ID.
        """
        if not select_algorithms:
            return {"selected_lines": {}, "line_count": 0}

        # Initialize selected_lines to None (first algorithm will set it)
        combined_selected_lines = None

        # Apply each selection algorithm
        for algo in select_algorithms:
            algo_result = self.apply_algorithm(algo['algorithm_name'], algo['args'], node_id = node_id)

            if 'selected_lines' not in algo_result:
                print(f"Selection algorithm '{algo['algorithm_name']}' did not return valid selection results.")
                continue

            # If this is the first selection algorithm, initialize combined_selected_lines
            if combined_selected_lines is None:
                combined_selected_lines = algo_result['selected_lines']
            else:
                # Apply logical AND with previous results using list comprehension
                combined_selected_lines = [
                    line_id for line_id in combined_selected_lines if line_id in algo_result['selected_lines']
                ]

        # Calculate the final line count
        final_line_count = len(combined_selected_lines)

        return {"selected_lines": combined_selected_lines, "line_count": final_line_count}


    def combine_partition_algorithms(
            self,
            partition_algorithms: List[Dict[str, Any]],
            node_id: int
    ) -> Dict[str, Dict[int, Union[str, List[int]]]]:
        """
        Combines multiple partition algorithms into a single set of partitions by concatenating the partition labels.

        Parameters:
        - partition_algorithms (List[Dict[str, Any]]): A list of partitioning algorithms and their results to combine.

        Returns:
        - dict: A dictionary where each key is a partition index, and each value is another dictionary with:
            - "label": The combined label of the partitions (from all partition algorithms).
            - "line_ids": A list of line IDs that belong to this combined partition.
        """
        if not partition_algorithms:
            return {"partitions": {}, "partition_count": 0}

        # Initialize a dictionary to store partitions combined from multiple algorithms
        combined_partitions = {}

        # Iterate through each algorithm and get its partitions
        for algo in partition_algorithms:
            algo_result = self.apply_algorithm(algo['algorithm_name'], algo['args'], node_id = node_id)

            if 'partitions' not in algo_result:
                print(f"Partition algorithm '{algo['algorithm_name']}' did not return valid partitions.")
                continue

            partitions = algo_result['partitions']

            # Combine partitions: concatenate labels and merge line_ids
            for partition_index, partition_info in partitions.items():
                label = partition_info['label']
                line_ids = partition_info['line_ids']

                for line_id in line_ids:
                    if line_id not in combined_partitions:
                        combined_partitions[line_id] = {"label": label, "line_ids": [line_id]}
                    else:
                        combined_partitions[line_id]['label'] += "; " + label

        # Transform combined_partitions into a new format: group by the concatenated labels
        final_partitions = {}
        for line_info in combined_partitions.values():
            label = line_info['label']
            if label not in final_partitions:
                final_partitions[label] = []
            final_partitions[label].extend(line_info['line_ids'])

        # Sort partitions by size in descending order
        sorted_partitions = dict(sorted(final_partitions.items(), key=lambda x: len(x[1]), reverse=True))

        # Prepare the final result with partition indices and labels
        result = {
            i: {"label": label, "line_ids": line_ids}
            for i, (label, line_ids) in enumerate(sorted_partitions.items())
        }

        return {"partitions": result, "partition_count": len(result)}


    def view(self, node_id=0, format="df"):
        """
        Returns a concordance view at the given leaf node in the analysis tree.

        Parameters:
        - node_id (int): The ID of the node to start from. Default is 0.
        - format (str): The format to return the data in. Default is "df" for DataFrame.

        Returns:
        - dict: A concordance view at the given leaf node in the analysis tree.
        """
        node = self.tree[node_id]
        if not node.type in ["order", "partition", "cluster"]:
            raise ValueError(f"Node {node_id} is not a leaf node of the tree belonging to one of the following types: 'order', 'partition', 'cluster'.")
        result = {"type": node.type}
        if node.type == "order":
            result["line_ids"] = self._get_ordered_line_ids(node.sort_keys)
        elif node.type == "partition":
            result["order"] = node.order
            result["partitions"] = node.partitions
        elif node.type == "cluster":
            pass #TODO
        if hasattr(node, 'rank_keys'):
            result["rank_keys"] = node.rank_keys
        if hasattr(node, 'marked_spans'):
            result["marked_spans"] = node.marked_spans
        return result

    def find_node_of_type(self, start_node, node_types):
        """
        Find closest parent node of a given type in the analysis tree.

        Parameters:
        - start_node (int): The ID of the node to start the search from.
        - node_type (str): The type of node to search for.

        Returns:
        - int: The ID of the first node of the specified type found in the operations tree.
        """
        current_node = start_node
        while True:
            if self.tree[current_node].type in node_types:
                return current_node
            if self.tree[current_node].parent is None:
                return None
            current_node = self.tree[current_node].parent.id


import pandas as pd

def partition_transfer(conc, **args) -> dict:
    """
    Transfers a partition structure from a source node to the active node's subset.

    This algorithm takes the grouping_result from a source node (passed via the "source_node" argument)
    and applies it to the active node's selected lines (contained in the conc object). It does so by
    intersecting each partition's "line_ids" with the active node's line IDs. Optionally, if a partition
    contains "prototypes" or "info", those are filtered or passed through accordingly. Partitions that
    become empty after the transfer are omitted.

    Parameters:
        conc (ConcordanceSubset): The active node's subset containing the selected lines.
        args (dict): A dictionary with the following key:
            - source_node (AnalysisTreeNode): The node from which to retrieve the partition structure.
              Its grouping_result should be a dictionary with a key "partitions" that holds a list of
              partition dictionaries. Each partition dictionary must include:
                - "id": An identifier.
                - "label": A label for the partition.
                - "line_ids": A list of line IDs.
              Optionally, a partition may include:
                - "prototypes": A list of prototypical line IDs.
                - "info": Additional information (as a dictionary).

    Returns:
        dict: A new partition structure in the format:
              {
                  "partitions": [
                      {
                          "id": <new_id>,
                          "label": <partition label>,
                          "line_ids": [<filtered line IDs>],
                          "prototypes": [<filtered prototypes>]  (optional),
                          "info": <info dictionary>               (optional)
                      },
                      ...
                  ]
              }
    """
    # Metadata for the algorithm
    partition_transfer._algorithm_metadata = {
        "name": "Partition Transfer",
        "description": (
            "Transfers a partition structure from a source node to the active node's subset by intersecting the "
            "source partitions' line IDs with the active node's selected lines. Prototypes and additional info are "
            "filtered accordingly."
        ),
        "algorithm_type": "partitioning",
        "status": "experimental",
        "scope": "subset",
        "args_schema": {
            "type": "object",
            "properties": {
                "source_node": {
                    "description": (
                        "The node from which to retrieve the partition structure. Its grouping_result must contain a "
                        "key 'partitions' that is a list of partition dictionaries. Each partition should have 'id', "
                        "'label', and 'line_ids', and may optionally include 'prototypes' and 'info'."
                    )
                }
            },
            "required": ["source_node"]
        }
    }

    source_node = args["source_node"]

    if not hasattr(source_node, "grouping_result") or "partitions" not in source_node.grouping_result:
        raise ValueError("The source node does not have a valid grouping_result with partitions.")

    source_partitions = source_node.grouping_result

    # Active node's selected lines (from conc.metadata index)
    active_lines = set(conc.metadata.index.tolist())

    new_partitions = []

    for partition in source_partitions.get("partitions", []):
        source_line_ids = set(partition.get("line_ids", []))
        filtered_line_ids = sorted(active_lines.intersection(source_line_ids))

        if not filtered_line_ids:
            continue

        new_partition = {
            "id": partition.get("id", max([p.get("id", 0) for p in new_partitions], default=0) + 1),
            "label": partition.get("label", ""),
            "line_ids": filtered_line_ids
        }

        if "prototypes" in partition:
            source_prototypes = set(partition.get("prototypes", []))
            filtered_prototypes = sorted(source_prototypes.intersection(set(filtered_line_ids)))
            if filtered_prototypes:
                new_partition["prototypes"] = filtered_prototypes

        if "info" in partition:
            new_partition["info"] = partition["info"]

        new_partitions.append(new_partition)

    return {"partitions": new_partitions}

