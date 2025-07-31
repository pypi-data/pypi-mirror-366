from esrf_pathlib import Path

from ..profiles import loader
from .api_dump_dict_to_nx import dump_dict_to_nx


def convert_lima2_to_h5mx(path_bliss_master_h5: Path, path_mx_master: Path, scan: str):
    schema = loader.load_profile("lima2_to_h5mx")

    dump_dict_to_nx(
        schema,
        path_mx_master,
        path_bliss_master_h5=path_bliss_master_h5,
        scan_index=scan,
    )
