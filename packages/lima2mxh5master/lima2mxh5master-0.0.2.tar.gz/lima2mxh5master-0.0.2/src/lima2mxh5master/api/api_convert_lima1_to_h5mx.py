from typing import Union

from esrf_pathlib import Path

from ..profiles import loader
from .api_dump_dict_to_nx import dump_dict_to_nx


def convert_lima1_to_h5mx(
    path_scan_run: Union[Path, str],
    name_h5master_file: str,
):
    """Create a NeXus master HDF5 file for a given MX scan run.

    This function validates the input paths, loads a JSON schema file (either
    user-provided or predefined), and generates the master HDF5 file by invoking
    `dump_dict_to_nx`. The default schema loads a custom class to compute necessary
    metadata define in :doc:`Custom Class <lima2mxh5master.profiles.lima1_to_h5mx>`.

    Parameters
    ----------
    path_scan_run : Union[Path, str]
        Path to the directory containing the MX scan run data. Must contain a valid
        `metadata.json` file.

    name_h5master_file : str
        Name of the output master HDF5 file to be created within the scan run directory.


    Example
    -------
    .. code-block:: python

        create_mx_master_h5(
            path_scan_run="/data/mx_scan_001", name_h5master_file="mx_master.h5",
            path_schema="custom_schema.json"
        )

    """

    if isinstance(path_scan_run, str):
        path_scan_run = Path(path_scan_run)

    if not path_scan_run.exists():
        raise FileNotFoundError(f"Scan Run directory not found: {path_scan_run}")

    path_metadata_json = path_scan_run / "metadata.json"
    if not path_metadata_json.exists():
        raise FileNotFoundError(f"metadata.json not found: {path_metadata_json}")

    path_h5_master_file = path_scan_run / name_h5master_file

    schema = loader.load_profile("lima1_to_h5mx")

    dump_dict_to_nx(schema, path_h5_master_file, filepath_metadata=path_metadata_json)
