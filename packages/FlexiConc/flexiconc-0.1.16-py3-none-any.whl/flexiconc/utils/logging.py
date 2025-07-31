import inspect
from typing import Any,  Dict, List, Optional, Tuple
from anytree import AnyNode

def get_function_info(skip_vars: List[str] = ['self']) -> Tuple[str, Dict[str, Any]]:
    """
    Retrieve the name of the current function and its local variables.

    Args:
        skip_vars (List[str]): Variable names to be excluded from the result. Defaults to ['self'].

    Returns:
        Tuple[str, Dict[str, Any]]: A tuple containing the function name (str) and a dictionary of local variables (dict).
    """
    frame = inspect.currentframe().f_back  # Get the frame of the caller function
    function_name = frame.f_code.co_name  # Get the name of the function
    args_info = inspect.getargvalues(frame)  # Get the arguments of the caller function

    # Remove specified variables from the dictionary
    args_dict = {arg: args_info.locals[arg] for arg in args_info.args if arg not in skip_vars}

    return function_name, args_dict


from anytree import AnyNode
from typing import Dict, Any, Optional

def add_to_tree(
    self,
    type: str,
    function_name: str,
    args_dict: Optional[Dict[str, Any]] = None,
    values: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Add a new node to the operations tree.

    Parameters:
        self: Concordance object.
        type (str): Type of the operation (e.g., query, select, partition).
        function_name (str): Name of the function.
        args_dict (Optional[Dict[str, Any]], optional): Arguments of the function. Defaults to None.
        values (Optional[Dict[str, Any]], optional): Additional attributes to be stored in the node. Defaults to None.

    Updates:
        - self.tree: Adds a new node to the tree with the specified type, function name, and additional values.
        - self.active_node: Sets the active node to the newly added node.
        - self.tree[active_node].function: Sets the function name of the newly added node.
        - self.tree[active_node].args: Sets the arguments of the newly added node.
        - Additional attributes are set for the newly added node based on the 'values' parameter.

    Returns:
        bool: True if the node was successfully added to the tree, False otherwise.
    """
    try:
        if len(self.tree) == 0:
            # Create the root node
            root_node = AnyNode(id=0, type=type, function=function_name, args=args_dict)
            self.tree.append(root_node)
        else:
            # Find the parent node based on the specified types (e.g., query, select, etc.)
            parent_node = self.tree[self.find_node_of_type(self.active_node, ["query", "populate", "select", "partition"])]

            # Create the new node and attach it to the parent node
            new_node = AnyNode(
                id=len(self.tree),
                type=type,
                parent=parent_node,
                function=function_name,
                args=args_dict
            )
            self.tree.append(new_node)

        # Set the newly created node as the active node
        self.active_node = len(self.tree) - 1

        # Set additional attributes if provided
        if values:
            for key, value in values.items():
                setattr(self.tree[self.active_node], key, value)

        return True  # Return True if the function executes successfully

    except Exception as e:
        # Handle exceptions if any occur
        print(f"An error occurred while adding to the tree: {e}")
        return False  # Return False if there was an error
