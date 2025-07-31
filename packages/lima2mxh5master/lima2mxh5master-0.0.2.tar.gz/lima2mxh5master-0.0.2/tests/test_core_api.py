import json
from typing import cast

import h5py
import numpy as np
from esrf_pathlib import Path
from lima2mxh5master.api import dump_dict_to_nx
from silx.io import h5py_utils


def test_dump_dict_to_nx(tmp_path: Path):
    """Test the `dump_dict_to_nx` function with multiple JSON schema files.

    This test: - Loads JSON metadata files from the `tests/test_schemas/` directory. -
    Injects a source directory for custom classes used during instantiation. - Checks if
    the `inputs` field is marked as "__REQUIRED__" to provide test inputs accordingly. -
    Writes to a temporary HDF5 master file. - Verifies that the file was created. -
    Asserts that specific datasets ("x", "y", "z") exist in the output HDF5 file and
    contain the expected data.
        All resulting h5 master files should have (x=1, y="string", z=[1,1,1])

    Parameters
    ----------
    tmp_path : esrf_pathlib.Path
        Temporary path provided by pytest for creating test files.

    Raises
    ------
    AssertionError
        If the generated HDF5 file is missing expected datasets or the dataset values do
        not match the expected output.

    """

    path_dir_schema = Path("./tests/test_schemas/")
    json_files = list(path_dir_schema.glob("*.json"))
    path_h5_master_file = Path(tmp_path) / "master.h5"

    for json_file in json_files:
        with json_file.open("r", encoding="utf-8") as f:
            dict_to_test = json.load(f)

        if path_h5_master_file.exists():
            path_h5_master_file.unlink()

        path_to_custom_class = Path(__file__).resolve().parent / "test_custom_class"
        dict_to_test["registry"]["source_dir"] = [path_to_custom_class]

        parameter = (
            dict_to_test.get("registry", {}).get("classes", {}).get("ClassTest1", {})
        )

        if parameter.get("inputs") == "__REQUIRED__":
            # Testing dynamic custom class initialization
            # schema_test8.json
            dump_dict_to_nx(
                dict_to_test,
                path_h5_master_file,
                inputs=[1, "string", [1, 1, 1]],
            )
        else:
            dump_dict_to_nx(dict_to_test, path_h5_master_file)

        assert path_h5_master_file.is_file()

        with h5py_utils.File(str(path_h5_master_file), "r") as h5:
            x = cast(h5py.Dataset, h5["x"])
            y = cast(h5py.Dataset, h5["y"])
            z = cast(h5py.Dataset, h5["z"])

            assert x[()] == 1
            assert y[()].decode("utf-8") == "string"
            assert np.array_equal(z[()], np.ones(3))
