import copy
from typing import Any
from typing import List
from typing import Tuple

import h5py
import numpy as np
from esrf_pathlib import Path
from silx.io.dictdump import h5todict


class GenerateDataFieldFromNexusWritter:
    def __init__(
        self,
        path_bliss_master_h5: Path,
        scan_index: str,
        h5_group_name: str,
    ):
        self.path_bliss_master_h5 = path_bliss_master_h5.resolve()
        self.scan_index = scan_index
        self.h5_group_name = h5_group_name

    def generate_dict_data_links(self):
        """Generates a dictionary for an NXdata group with external links.

        This method resolves the final data sources and constructs a dictionary
        that can be dumped to an HDF5 file to create an NXdata group. The
        dictionary includes attributes and external links to the raw data files.

        Returns
        -------
        dict
            A dictionary representing the NXdata group structure.

        """

        data_dict = {}
        data_dict["@NX_class"] = "NXdata"
        data_dict["@signal"] = "data_000000"
        name_dataset_entry = ">data_000000"

        nexus_filename = self.path_bliss_master_h5.name
        detector_name = self._get_detector_name()
        path_vds = f"{self.scan_index}/{self.h5_group_name}/{detector_name}"
        str_link = f"{nexus_filename}::{path_vds}"

        data_dict[name_dataset_entry] = str_link

        return data_dict

    def _get_detector_name(self):
        """Finds the detector name from a group with a single softlink.

        Args
        ----
        h5_group_name : str
            The name of the parent group (e.g., 'measurement').

        Returns
        -------
        str
            The key name, which is assumed to be the detector name.

        """
        with h5py.File(self.path_bliss_master_h5, "r") as f:
            url_measurement_grp = f"{self.scan_index}/{self.h5_group_name}"
            measurement_grp = f[url_measurement_grp]
            assert isinstance(measurement_grp, h5py.Group)
            keys = list(measurement_grp.keys())

            if len(keys) != 1:
                raise ValueError(f"Expected exactly one key, found {len(keys)}")
            return keys[0]


class GenerateDataFieldFromRawData:
    """A utility class to generate HDF5 data link structures.

    This class is designed to traverse HDF5 files, resolving external links,
    soft links, and virtual datasets (VDS) to find the ultimate raw data
    sources. It then generates a dictionary representing an NXdata group
    with external links pointing to these final data sources.

    Attributes
    ----------
    path_bliss_master_h5 : Path
        The absolute path to the source BLISS master HDF5 file.
    path_mx_master_h5 : Path
        The absolute path to the destination NeXus master HDF5 file.
    scan_index : str
        The scan identifier within the BLISS HDF5 file (e.g., '1.1').
    h5_group_name : str
        The name of the HDF5 group containing the data (e.g., 'measurement').

    """

    def __init__(
        self,
        path_bliss_master_h5: Path,
        path_mx_master_h5: Path,
        scan_index: str,
        h5_group_name: str,
    ):
        self.path_bliss_master_h5 = path_bliss_master_h5.resolve()
        self.path_mx_master_h5 = path_mx_master_h5.resolve(strict=False)
        self.scan_index = scan_index
        self.h5_group_name = h5_group_name

    def get_data_path(self):
        """Constructs the internal HDF5 path to the detector data group.

        It assumes the specified 'measurement' group contains a single soft link
        pointing to the actual detector data.

        Returns
        -------
        str
            The full internal HDF5 path to the detector data group.

        Raises
        ------
        ValueError
            If the target group does not contain exactly one key (link).

        """

        with h5py.File(self.path_bliss_master_h5, "r") as f:
            url_measurement_grp = f"{self.scan_index}/{self.h5_group_name}"
            measurement_grp = f[url_measurement_grp]
            assert isinstance(measurement_grp, h5py.Group)

            keys = list(measurement_grp.keys())
            if len(keys) != 1:
                raise ValueError(f"Expected exactly one key, found {len(keys)}")
            key_detector = keys[0]
        return f"/{self.scan_index}/{self.h5_group_name}/{key_detector}"

    def generate_dict_data_links(self):
        """Generates a dictionary for an NXdata group with external links.

        This method resolves the final data sources and constructs a dictionary
        that can be dumped to an HDF5 file to create an NXdata group. The
        dictionary includes attributes and external links to the raw data files.

        Returns
        -------
        dict
            A dictionary representing the NXdata group structure.

        """
        data_dict = {}
        data_dict["@NX_class"] = "NXdata"
        data_dict["@signal"] = "data_000000"
        list_vds_info = (
            GenerateDataFieldFromRawData.get_relative_paths_to_final_sources(
                self.path_bliss_master_h5, self.get_data_path()
            )
        )
        for i, (path_vds, path_data) in enumerate(list_vds_info):
            name_dataset_entry = f">data_{i:06d}"
            str_link = f"{path_vds}::{path_data}"
            data_dict[name_dataset_entry] = str_link

        return data_dict

    @staticmethod
    def _resolve_recursive(
        current_h5_path: Path, current_dataset_path: str, path_segments: List[str]
    ) -> List[Tuple[str, str]]:
        """A recursive helper function to traverse HDF5 links.

        This function follows a chain of HDF5 links (External, Soft) until it
        reaches a virtual or real dataset. For a virtual dataset, it extracts
        all its source files and paths. It accumulates relative path segments
        during traversal.

        Args
        ----
        current_h5_path : Path
            The path to the HDF5 file currently being examined.
        current_dataset_path : str
            The internal path to the dataset or link within the current file.
        path_segments : List[str]
            A list of relative directory parts accumulated so far.

        Returns
        -------
        List[Tuple[str, str]]
            A list of (file_path, dataset_path) tuples for final data sources.

        """
        if not current_h5_path.exists():
            raise Exception(f"Error: File not found at '{current_h5_path}'")

        with h5py.File(current_h5_path, "r") as f:
            link_object = f.get(current_dataset_path, getlink=True)

            if isinstance(link_object, h5py.ExternalLink):
                relative_link_path = Path(link_object.filename)
                print(f"Found ExternalLink: '{relative_link_path}'")

                dir_part = str(relative_link_path.parent)
                if dir_part and dir_part != ".":
                    path_segments.append(dir_part)

                next_h5_path = (current_h5_path.parent / relative_link_path).resolve()
                next_dataset_path = link_object.path
                print(f"  -> Following link to file: {next_h5_path}")
                print(f"  -> New dataset path: {next_dataset_path}\n")

                return GenerateDataFieldFromRawData._resolve_recursive(
                    next_h5_path, next_dataset_path, path_segments
                )

            elif isinstance(link_object, h5py.SoftLink):
                next_dataset_path = link_object.path
                print(f"Found SoftLink (internal) pointing to: '{next_dataset_path}'")
                print("  -> Following link within the same file.\n")
                return GenerateDataFieldFromRawData._resolve_recursive(
                    current_h5_path, next_dataset_path, path_segments
                )

            dataset_object = f[current_dataset_path]
            if isinstance(dataset_object, h5py.Dataset):
                if dataset_object.is_virtual:
                    print(f"Found Virtual Dataset: '{current_dataset_path}'")
                    vds_sources = dataset_object.virtual_sources()
                    if not vds_sources:
                        print("Error: VDS has no sources.")
                        return []

                base_relative_path = Path(*path_segments)
                final_results = []

                print(f"  -> VDS is composed of {len(vds_sources)} source(s).")
                for i, source in enumerate(vds_sources):
                    final_source_filename = Path(source.file_name)
                    internal_dataset_path = source.dset_name
                    full_relative_path = base_relative_path / final_source_filename

                    final_results.append(
                        (str(full_relative_path), internal_dataset_path)
                    )
                    print(
                        f"  -> Resolved source {i + 1}: File '{full_relative_path}',"
                        f" Dataset '{internal_dataset_path}'"
                    )

                return final_results

            else:
                print("Reached a standard dataset. Traversal complete.")
                relative_file_path = Path(*path_segments) / current_h5_path.name
                return [(str(relative_file_path), current_dataset_path)]

    @staticmethod
    def get_relative_paths_to_final_sources(
        initial_h5_path: Path, dataset_path: str
    ) -> List[Tuple[str, str]]:
        """Finds the relative paths from a master file to all raw data sources.

        This method recursively traverses HDF5 external/internal links and
        virtual datasets to find the final data locations. It calculates the
        full relative path from the initial HDF5 file's directory to each
        source file.

        Args
        ----
        initial_h5_path : Path
            The file path to the starting HDF5 file (e.g., 'master.h5').
        dataset_path : str
            The internal HDF5 path to the starting dataset or link.

        Returns
        -------
        List[Tuple[str, str]]
            A list of tuples, where each tuple is (file_path, dataset_path).
            Example: [('raw_data/d1.h5', '/entry/data'), ('raw_data/d2.h5', '/entry/
            data')]

        Raises
        ------
        Exception
            If any file is not found or a path cannot be resolved.

        """
        try:
            current_h5_path = Path(initial_h5_path).resolve()
            print(f"Starting traversal from: {current_h5_path}")
            print(f"Initial dataset path: {dataset_path}\n")

            return GenerateDataFieldFromRawData._resolve_recursive(
                current_h5_path, dataset_path, []
            )

        except (FileNotFoundError, KeyError) as e:
            raise Exception(f"An error occurred during traversal: {e}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {e}")


class H5MetadataHandler:
    """A handler for reading and accessing metadata from a BLISS HDF5 file.

    This class uses `silx.io.h5todict` to load a scan group from an HDF5
    file into a Python dictionary. It provides convenient methods to access
    nested values, attributes, and perform simple computations on the metadata.
    A special placeholder, `$DETECTOR$`, can be used in key paths to dynamically
    insert the detector name.

    Attributes
    ----------
    path_bliss_master_h5 : Path
        The path to the source BLISS HDF5 file.
    scan_index : str
        The scan identifier (e.g., '1.1') to access within the HDF5 file.
    h5_group_name : str
        The name of the measurement group (e.g., 'measurement').
    detector_name : str
        The name of the detector, extracted from the measurement group link.
    _bliss_metadata : dict
        The cached dictionary of metadata loaded from the HDF5 file.

    """

    def __init__(self, path_bliss_master_h5: Path, scan_index: str, h5_group_name: str):
        self.path_bliss_master_h5 = path_bliss_master_h5
        self.scan_index = scan_index
        self.h5_group_name = h5_group_name
        self.detector_name = self._get_softlink_key_name(self.h5_group_name)
        self._bliss_metadata = self._get_metadata_from_h5()

    def get_metadata_value(self, key_path: str) -> Any:
        """Retrieves a metadata value using a slash-separated key path.

        Args
        ----
        key_path : str
            A path-like string (e.g., 'instrument/monochromator/energy').
            The placeholder '$DETECTOR$' is replaced with the actual detector name.

        Returns
        -------
        Any
            The metadata value, deep-copied to prevent mutation of the cache.

        Raises
        ------
        ValueError
            If a key is accessed on a non-dictionary intermediate value.
        KeyError
            If a key does not exist in the path.

        """
        value = self._bliss_metadata
        for key in key_path.split("/"):
            if key == "$DETECTOR$":
                key = self.detector_name

            if isinstance(value, dict):
                value = value[key]
            else:
                raise ValueError(
                    f"Cannot access key '{key}' in non-dictionary: {value}"
                )
        return copy.deepcopy(value)

    def get_attributes_value(self, key_path: str, attribute: str) -> Any:
        """Retrieves an attribute from a specific dataset in the metadata.

        Args
        ----
        key_path : str
            A path-like string to the dataset (e.g., 'instrument/beam/size').
        attribute : str
            The name of the attribute to retrieve.

        Returns
        -------
        Any
            The attribute value.

        """
        value = self._bliss_metadata
        list_keys_path = key_path.split("/")
        final_key = (list_keys_path[-1], attribute)

        for i, key in enumerate(list_keys_path):
            if key == "$DETECTOR$":
                key = self.detector_name
            if i == len(list_keys_path) - 1:
                value = value[final_key]
            else:
                if isinstance(value, dict):
                    value = value[key]
                else:
                    raise ValueError(
                        f"Cannot access key '{key}' in non-dictionary: {value}"
                    )
        return copy.deepcopy(value)

    def get_link_metadata(self, key_path: str):
        """Creates an HDF5 external link string for a given metadata field.

        Checks if the path exists in the HDF5 file before creating the link.

        Args
        ----
        key_path : str
            The internal HDF5 path to the target dataset.

        Returns
        -------
        str
            The formatted external link string or "Not Found" if the path is invalid.

        """

        key_path = key_path.replace("$DETECTOR$", self.detector_name)
        h5_fields_path = f"{self.scan_index}/{key_path}"
        if self.h5_field_path_exist(h5_fields_path):
            return f"{self.path_bliss_master_h5.name}::{h5_fields_path}"
        else:
            return "Not Found"

    def h5_field_path_exist(self, field_path):
        """Checks if a given path exists within the HDF5 file.

        Args
        ----
        field_path : str
            The full internal path to check (e.g., '1.1/measurement/eiger').

        Returns
        -------
        bool
            True if the path exists, False otherwise.

        """
        with h5py.File(self.path_bliss_master_h5, "r") as f:
            if field_path in f:
                return True
            else:
                return False

    def compute_acquisition_time(self) -> str:
        """Calculates the average acquisition time.

        Retrieves the start and end times from metadata, computes the midpoint,
        and returns it as an ISO 8601 formatted string.

        Returns
        -------
        str
            The average acquisition time in ISO 8601 format.

        """

        from datetime import datetime

        start_date = self.get_metadata_value("start_time")
        end_date = self.get_metadata_value("end_time")

        start = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S.%f%z")
        end = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S.%f%z")

        avg_timestamp = (start.timestamp() + end.timestamp()) / 2
        avg_datetime = datetime.fromtimestamp(avg_timestamp)

        return avg_datetime.isoformat(timespec="milliseconds")

    def get_threshold_energy(self, key_path):
        """Retrieves the active threshold energy from a list.

        Assumes the data at `key_path` is a list of [energy, is_active] pairs
        and returns the energy of the first active entry.

        Args
        ----
        key_path : str
            The key path to the threshold energy data.

        Returns
        -------
        float
            The active threshold energy, or 0 if none is found.

        """
        array_threshold_energy = self.get_metadata_value(key_path)
        for thresh in array_threshold_energy:
            if thresh[1]:
                return thresh[0]
        return 0

    def __getitem__(self, key_path: str) -> Any:
        """Provides dictionary-like access to metadata values.

        Args
        ----
        key_path : str
            A path-like string (e.g., 'instrument/monochromator/energy').

        Returns
        -------
        Any
            The corresponding metadata value.

        """
        return self.get_metadata_value(key_path)

    def _get_softlink_key_name(self, h5_group_name: str):
        """Finds the detector name from a group with a single softlink.

        Args
        ----
        h5_group_name : str
            The name of the parent group (e.g., 'measurement').

        Returns
        -------
        str
            The key name, which is assumed to be the detector name.

        """
        with h5py.File(self.path_bliss_master_h5, "r") as f:
            url_measurement_grp = f"{self.scan_index}/{h5_group_name}"
            measurement_grp = f[url_measurement_grp]
            assert isinstance(measurement_grp, h5py.Group)
            keys = list(measurement_grp.keys())

            if len(keys) != 1:
                raise ValueError(f"Expected exactly one key, found {len(keys)}")
            return keys[0]

    def _get_metadata_from_h5(self) -> dict:
        """Loads metadata from the HDF5 file into a cleaned dictionary.

        Returns
        -------
        dict
            The processed metadata dictionary for the specified scan.

        """
        h5_meta = h5todict(
            h5file=self.path_bliss_master_h5,
            asarray=True,
            dereference_links=False,
            include_attributes=True,
        )[self.scan_index]
        h5_meta = self._convert_dict_arrays_to_scalars(h5_meta)
        return h5_meta

    def _convert_dict_arrays_to_scalars(self, d: dict) -> dict:
        """Recursively converts single-element numpy arrays to Python scalars.

        Args
        ----
        d : Any
            The dictionary, list, or value to process.

        Returns
        -------
        Any
            The processed item with single-element arrays converted.

        """
        if isinstance(d, dict):
            return {k: self._convert_dict_arrays_to_scalars(v) for k, v in d.items()}
        elif isinstance(d, np.ndarray):
            if d.size == 1:
                return d.item()  # returns scalar, including string scalars
            else:
                return d.tolist()
        else:
            return d
