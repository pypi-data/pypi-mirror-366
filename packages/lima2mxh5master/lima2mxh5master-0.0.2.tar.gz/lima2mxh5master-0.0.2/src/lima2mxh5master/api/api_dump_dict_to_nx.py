from typing import Union

from esrf_pathlib import Path
from silx.io.dictdump import dicttonx

from lima2mxh5master.core.build_context_from_schema import build_context_from_schema
from lima2mxh5master.core.refactor_external_h5dict import refactor_external_calls
from lima2mxh5master.core.refactor_internal_h5dict import refactor_dynamic_keys
from lima2mxh5master.core.refactor_internal_h5dict import refactor_internal_calls


def dump_dict_to_nx(
    dict_h5: dict,
    path_h5_master_file: Union[Path, str],
    **kwargs,
):
    r"""Generate and save an HDF5 master file from a schema dictionary.

    This function transforms a nested dictionary schema into a valid NeXus-compliant
    HDF5 master file using `silx.io.dictdump.dicttonx`. The dictionary must follow a
    specific structure, including a `registry` (defining external class resources) and a
    `schema` (describing the file layout and logic).

    Extended schema features supported by `lima2mxh5master` include:

    - **Internal logic** via ``>=`` fields and ``${...}`` references to compute values.
    - **External method calls** using `__class__`, `__method__`, and `__kwargs__`.

    For a complete specification and examples, see the :doc:`Schema Guide
    <schema_guide>`.

    Parameters
    ----------
    dict_h5 : dict
        Dictionary containing both the `registry` and `schema` keys:

        - `registry`: defines external class sources and initialization parameters.
        - `schema`: describes the structure and content of the HDF5 file.

    path_h5_master_file : str or pathlib.Path
        Path to the output `.h5` file.

    \*\*kwargs
        Additional runtime parameters used to populate required dynamic fields.

    Examples
    --------
    .. code-block:: python

        from lima2mxh5master import dump_dict_to_nx

        config = {
            "registry": {
                "source_dir": ["/path/to/classes"], "classes": {
                    "MyClass": {
                        "init_parameters": {
                            "foo": "__REQUIRED__"
                        }
                    }
                }
            }, "schema": {
                "field": {
                    "__class__": "MyClass", "__method__": "generate", "__kwargs__": {
                        "param1": 42
                    }
                }, ">=field2":"${field} * 4",
            }
        }

        dump_dict_to_nx(config, "output_master.h5", foo="external-value")

    """

    if "registry" not in dict_h5:
        raise ValueError(
            "The provided dictionary does not contain a 'registry' key. "
            "Please ensure the dictionary is structured correctly."
        )

    registry = dict_h5.get("registry")
    if registry and "source_dir" in registry:
        if isinstance(registry["source_dir"], list):
            list_paths_class = registry["source_dir"]
            class_folder_paths = [Path(p) for p in list_paths_class]
        else:
            raise ValueError("The 'source_dir' key in the registry must be a list.")
    else:
        class_folder_paths = []

    if registry and "classes" in registry:
        registry_classes = registry["classes"]
        if isinstance(registry["classes"], dict):
            registry_classes = registry["classes"]
        else:
            raise ValueError("The 'classes' key in the registry must be a dictionary.")
    else:
        raise ValueError(
            "The provided dictionary does not contain a 'classes' key in the registry. "
            "Please ensure the dictionary is structured correctly."
        )

    if isinstance(path_h5_master_file, str):
        path_h5_master_file = Path(path_h5_master_file)

    if path_h5_master_file.exists():
        path_h5_master_file.unlink()

    if "schema" not in dict_h5:
        raise ValueError(
            "The provided dictionary does not contain a 'schema' key. "
            "Please ensure the dictionary is structured correctly."
        )

    schema_h5 = dict_h5["schema"]
    context = build_context_from_schema(
        schema_h5, registry_classes, class_folder_paths, **kwargs
    )

    # Refactoring Schema for silxdump
    schema_h5 = refactor_external_calls(schema_h5, context)
    schema_h5 = refactor_internal_calls(schema_h5)
    schema_h5 = refactor_dynamic_keys(schema_h5)
    # Saving Master File

    dicttonx(schema_h5, path_h5_master_file, h5path="/", add_nx_class=True)
