import re

from asteval import Interpreter

# Marker for calculated fields
CALCULATED_PREFIX = ">="


def get_value_by_path(root_dict: dict, path_str: str) -> dict:
    """Retrieve a nested value from a dictionary using a string path.

    Parameters
    ----------
    root_dict : dict
        The root dictionary from which the value will be retrieved.
    path_str : str
        A string representing the path to the desired value (e.g., "/a/b/c").

    Returns
    -------
    dict
        The value located at the specified path within the dictionary.

    """
    parts = path_str.strip("@/>").split("/")
    current = root_dict
    for part in parts:
        current = current[part]
    return current


def get_parent_and_key(root_dict: dict, path_str: str) -> tuple:
    """Extract the parent dictionary and the final key from a path.

    Parameters
    ----------
    root_dict : dict
        The root dictionary containing nested structures.
    path_str : str
        A string path pointing to a nested key (e.g., "a/b/c").

    Returns
    -------
    tuple
        A tuple containing:

        - parent : dict
            The parent dictionary that contains the final key.

        - key : str
            The key corresponding to the last segment in the path.

    """
    parts = path_str.strip("@/>").split("/")
    parent_path_parts = parts[:-1]
    key = parts[-1]

    parent = root_dict
    for part in parent_path_parts:
        parent = parent[part]
    return parent, key


def evaluate_path(
    result_path_str: str, root_dict: dict, evaluated_cache: dict, in_progress: list
) -> dict:
    """Recursively evaluate a value at a path that may reference expressions.

    Parameters
    ----------
    result_path_str : str
        The path to evaluate (e.g., "a/b/c"), which may refer to a computed value.
    root_dict : dict
        The dictionary containing all nested values and expressions.
    evaluated_cache : dict
        A cache to store evaluated paths to avoid redundant computation.
    in_progress : list
        A list of currently-evaluating paths to detect circular dependencies.

    Returns
    -------
    dict
        The evaluated value at the given path.

    Raises
    ------
    ValueError
        If a circular dependency is detected or if expression evaluation fails.

    """
    result_path_str = result_path_str.strip("@/>")

    if result_path_str in evaluated_cache:
        return evaluated_cache[result_path_str]

    if result_path_str in in_progress:
        raise ValueError(f"Circular dependency detected at '{result_path_str}'")

    in_progress.append(result_path_str)

    try:
        parent, key = get_parent_and_key(root_dict, result_path_str)
        expression_key = CALCULATED_PREFIX + key

        if expression_key in parent:
            expression_str = parent[expression_key]

            aeval = Interpreter()
            temp_var_idx = 0

            def path_replacer(match):
                nonlocal temp_var_idx
                sub_path_expr = match.group(1).strip("@/>")

                sub_path_parts = sub_path_expr.split("/")
                last_part = sub_path_parts[-1]

                if last_part.startswith(CALCULATED_PREFIX):
                    result_key_part = last_part[len(CALCULATED_PREFIX) :]
                    sub_path_result = "/".join(sub_path_parts[:-1] + [result_key_part])
                else:
                    sub_path_result = sub_path_expr

                data = evaluate_path(
                    sub_path_result, root_dict, evaluated_cache, in_progress
                )
                temp_var_name = f"__data_{temp_var_idx}__"
                temp_var_idx += 1
                aeval.symtable[temp_var_name] = data
                return temp_var_name

            substituted_expression = re.sub(
                r"\$\{([^{}]+)\}", path_replacer, expression_str
            )

            result = aeval.eval(substituted_expression)

            if aeval.error:
                raise ValueError(
                    f"Error evaluating expression at '{result_path_str}' (from key "
                    f"'{expression_key}'): {aeval.error[0]}"
                )
            parent[key] = result
            del parent[expression_key]

            evaluated_cache[result_path_str] = result

        else:
            result = get_value_by_path(root_dict, result_path_str)
            if result_path_str not in evaluated_cache:
                evaluated_cache[result_path_str] = result
    finally:
        in_progress.remove(result_path_str)

    return evaluated_cache[result_path_str]


def find_expression_result_paths(dictionary: dict, current_path: str = "") -> list:
    """Find all paths in the dictionary where expression results should be computed.

    Parameters
    ----------
    dictionary : dict
        The nested dictionary to search.
    current_path : str, optional
        The path prefix for recursion (used internally).

    Returns
    -------
    list
        A list of result paths corresponding to discovered expression keys.

    """
    paths_to_evaluate = []
    for key, value in list(dictionary.items()):
        full_path = f"{current_path}/{key}" if current_path else key
        if isinstance(value, dict):
            paths_to_evaluate.extend(find_expression_result_paths(value, full_path))
        elif key.startswith(CALCULATED_PREFIX):
            result_key = key[len(CALCULATED_PREFIX) :]
            result_path = f"{current_path}/{result_key}" if current_path else result_key
            paths_to_evaluate.append(result_path)
    return paths_to_evaluate


def refactor_internal_calls(dictionary: dict) -> dict:
    """Evaluate all expressions in the dictionary and replace them with computed values.

    Parameters
    ----------
    dictionary : dict
        The input dictionary potentially containing expression-based entries.

    Returns
    -------
    dict
        The updated dictionary with expressions evaluated and replaced.

    """
    root_dict = dictionary
    evaluated_cache: dict = {}
    in_progress: list = []

    paths_to_evaluate = find_expression_result_paths(dictionary)

    for result_path in paths_to_evaluate:
        if result_path not in evaluated_cache:
            evaluate_path(result_path, root_dict, evaluated_cache, in_progress)

    return dictionary


def refactor_dynamic_keys(dictionary: dict):
    """Look for h5 dynamic fields to replace the key and the value with the correct
    value

    Parameters
    ----------
    dictionary : dict
        The input dictionary potentially containing dynamic key

    Returns
    -------
    dict
        The updated dictionary with key and field evaluated

    Example
    -------
    .. code-block:: json

        "__dynamic_entry__" :{
            ">=__key_from__": "'pilatus_fw_version' if 'PILATUS' in ${/entry/instrument/
            detector/description} else 'eiger_fw_version'",
            "__value_from__": "MISSING"
        }

    """

    if isinstance(dictionary, dict):
        for key in list(dictionary.keys()):
            if key == "__dynamic_entry__":
                entry_data = dictionary[key]

                new_key = entry_data.get("__key_from__")
                new_value = entry_data.get("__value_from__")

                if new_key:
                    dictionary[new_key] = new_value
                del dictionary[key]
            else:
                refactor_dynamic_keys(dictionary[key])

    elif isinstance(dictionary, list):
        for item in dictionary:
            refactor_dynamic_keys(item)

    return dictionary
