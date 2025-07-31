from typing import Any
from typing import Union

from lima2mxh5master.core.pydantic_models import InstanceMethodCall


def _resolve_path(parent_path, key) -> str:
    """Constructs an HDF5-style path by appending a key to a parent path.

    Parameters
    ----------
    parent_path : str
        The base path. If None or "/", the key becomes the root.
    key : str
        The child key to append.

    Returns
    -------
    str
        The combined hierarchical path.
    """
    if not parent_path or parent_path == "/":
        return f"/{key}"
    return f"{parent_path}/{key}"


def execute_instance_method(data_item: dict, context: dict) -> Any:
    """Executes a method on a target instance retrieved from the provided context.

    This function validates the input data, retrieves the target instance from
    the context using the specified key, and invokes the specified method on
    the instance with the provided arguments and keyword arguments.

    Parameters
    ----------
    call_spec : dict
        A dictionary describing the method call.
    context : dict
        A dictionary mapping instance keys to live Python objects.

    Returns
    -------
    Any
        The value returned by the executed method.

    Example
    -------
    .. code-block:: json

        {
            "__class__": "BeamlineSetup",
            "__method__": "get_wavelength",
            "__args__": [],
            "__kwargs__": {"unit": "angstrom"}
        }

    """

    call_info = InstanceMethodCall.model_validate(data_item)
    class_name = call_info.class_name
    method_name = call_info.method_name
    args = call_info.args
    kwargs = call_info.kwargs

    target_instance = context.get(class_name)
    if target_instance is None:
        raise ValueError(f"Instance '{class_name}' not found in the provided context.")

    method_to_call = getattr(target_instance, method_name)

    if not callable(method_to_call):
        raise TypeError(
            f"Attribute '{method_name}' on instance '{class_name}' is not callable."
        )

    result = method_to_call(*args, **kwargs)
    return result


def refactor_external_calls(
    data_item: Union[dict, list], context: dict, current_hdf5_path: str = "/"
) -> Any:
    """
    Recursively processes a nested hdf5 structure (dictionary or list) to handle
    external calls,executing instance methods and updates the structure accordingly.

    Parameters
    ----------
    item : dict | list
        The template structure to process.
    context : dict
        A dictionary of live helper instances available for method calls.
    current_hdf5_path : str, optional
        The current path in the structure.

    Returns
    -------
    Any
        The processed structure with all method calls resolved.

    Example
    -------
    .. code-block:: json

        {
            "entry": {
                "instrument": {
                    "beam": {
                        "incident_wavelength": {
                            "__class__": "BeamlineSetup",
                            "__method__": "get_wavelength"
                        }
                    },
                    "detector": {
                        "description": "EIGER 2X 9M"
                    }
                }
            }
        }

    """

    if isinstance(data_item, dict):
        # Check for a method call block
        if "__class__" in data_item and "__method__" in data_item:
            if "__kwargs__" in data_item:
                data_item["__kwargs__"] = refactor_external_calls(
                    data_item["__kwargs__"], context, current_hdf5_path
                )
            if "__args__" in data_item:
                data_item["__args__"] = refactor_external_calls(
                    data_item["__args__"], context, current_hdf5_path
                )

            return execute_instance_method(data_item, context)

        processed_dict = {}
        for key, value in data_item.items():
            if key.startswith("@"):
                processed_dict[key] = value
            else:
                child_hdf5_path = _resolve_path(current_hdf5_path, key)
                processed_value = refactor_external_calls(
                    value, context, child_hdf5_path
                )
                if processed_value is not None:
                    processed_dict[key] = processed_value
        return processed_dict if processed_dict else None

    elif isinstance(data_item, list):
        processed_list = [
            refactor_external_calls(elem, context, f"{current_hdf5_path}[{i}]")
            for i, elem in enumerate(data_item)
        ]
        return [item for item in processed_list if item is not None]
    else:
        return data_item
