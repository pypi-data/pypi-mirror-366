from esrf_pathlib import Path
from lima2mxh5master.api import convert_lima1_to_h5mx
from lima2mxh5master.api import convert_lima2_to_h5mx


def test_convert_lima1_to_h5mx():
    path_scan_run = Path("./tests/test_mxcube_data/")
    name_master = "test_master.h5"

    convert_lima1_to_h5mx(path_scan_run=path_scan_run, name_h5master_file=name_master)

    assert (path_scan_run / name_master).is_file()


def test_convert_lima2_to_h5mx():
    path_nexus_bliss = Path("./tests/test_bliss_data/nexus_bliss_master.h5")
    path_mx_master = Path("./tests/test_master.h5")

    convert_lima2_to_h5mx(
        path_bliss_master_h5=path_nexus_bliss,
        path_mx_master=path_mx_master,
        scan="1.1",
    )

    assert path_mx_master.is_file()
