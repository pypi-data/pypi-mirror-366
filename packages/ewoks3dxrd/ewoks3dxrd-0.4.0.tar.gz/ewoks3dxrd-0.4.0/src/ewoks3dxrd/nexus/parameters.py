from __future__ import annotations
from typing import Any
import h5py
from pathlib import Path
from typing import Tuple
import numpy as np
from silx.io.utils import h5py_read_dataset
from .utils import get_data_url_paths


def _save_parameters(
    parent_group: h5py.Group,
    config_settings: dict[str, Any],
    group_name: str = "parameters",
):
    """
    Helper function to place the config_settings in 'param_name' group
    in the given `parent_group`
    """
    parameters_group = parent_group.require_group(group_name)
    parameters_group.attrs["NX_class"] = "NXcollection"

    for key, value in config_settings.items():
        if key in parameters_group:
            del parameters_group[key]
        parameters_group.create_dataset(
            key, data=value if value is not None else "None"
        )


def create_parameters_group(
    group_path: h5py.Group,
    config_settings: dict[str, Any] | dict[str, dict[str, Any]],
):
    if isinstance(config_settings, dict) and all(
        isinstance(value, dict) for value in config_settings.values()
    ):
        parameters_group = group_path.require_group("parameters")
        parameters_group.attrs["NX_class"] = "NXcollection"
        for param_name, param_values in config_settings.items():
            _save_parameters(
                parent_group=parameters_group,
                config_settings=param_values,
                group_name=param_name,
            )
    else:
        _save_parameters(parent_group=group_path, config_settings=config_settings)


def get_parameters(filename: str | Path, process_group_name: str) -> dict[str, str]:
    return get_parameter(f"{filename}::{process_group_name}", key=None)


def get_parameter(data_url_as_str: str, key: str | None, sub_folder="parameters"):
    file_path, data_path = get_data_url_paths(data_url_as_str)

    with h5py.File(file_path, "r") as h5file:
        parameters: h5py.Group = h5file[f"{data_path}/{sub_folder}"]
        if key is None:
            return {k: h5py_read_dataset(dset=v) for k, v in parameters.items()}

        if key not in parameters:
            return None

        return h5py_read_dataset(h5file[f"{data_path}/{sub_folder}/{key}"])


def find_parameter(data_url_as_str: str, key: str):
    value = get_parameter(data_url_as_str, key=key)
    if value is not None:
        return value

    data_from = get_parameter(data_url_as_str, key="data_from")
    if data_from is None:
        raise KeyError(f"Could not find {key} nor 'data_from' in {data_url_as_str}")

    data_from_value = find_parameter(data_from, key=key)
    if data_from_value is None:
        raise KeyError(f"Could not find {key} in {data_from}/parameters.")

    return data_from_value


def read_nx_collection_parameters(
    filename: str | Path, process_group_name: str, sub_folder: str
) -> dict:
    return get_parameter(
        data_url_as_str=f"{filename}::{process_group_name}",
        key=None,
        sub_folder=sub_folder,
    )


def get_omega_array(
    filename: str | Path, entry_name: str, process_group_name: str
) -> np.ndarray:
    with h5py.File(filename, "r") as f:
        entry = f[f"{entry_name}/{process_group_name}"]
        folder_grp = entry["parameters/FolderFileSettings"]
        masterfile = h5py_read_dataset(dset=folder_grp["masterfile"])
        scan_number = h5py_read_dataset(dset=folder_grp["scan_number"])
        omegamotor = h5py_read_dataset(dset=folder_grp["omegamotor"])
        with h5py.File(masterfile, "r") as hin:
            omega_angles = hin[f"{scan_number}.1/measurement"][omegamotor]
            return h5py_read_dataset(dset=omega_angles)


def find_lattice_parameters(data_url_as_str: str) -> Tuple[np.ndarray, int]:
    lattice_params = find_parameter(data_url_as_str, key="lattice_parameters")
    symmetry = find_parameter(data_url_as_str, key="lattice_space_group")

    return lattice_params, int(symmetry)


def find_wavelength(data_url_as_str: str) -> float:
    return np.float64(find_parameter(data_url_as_str, key="wavelength"))


def find_reciprocal_distance_tolerance(data_url_as_str: str) -> float:
    return np.float64(find_parameter(data_url_as_str, key="dstol"))


def find_lattice_nexus_group_url(data_url_as_str: str):
    file_path, data_path = get_data_url_paths(data_url_as_str)
    with h5py.File(file_path, "r") as f:
        par_grp = f[f"{data_path}/parameters"]
        if "lattice_name" in par_grp:
            return f"{file_path}::{data_path}"
        elif "data_from" in par_grp:
            return find_lattice_nexus_group_url(
                h5py_read_dataset(dset=par_grp["data_from"])
            )
        else:
            raise FileNotFoundError(
                """Could not find phase nexus data group in the given data_url path.
                """
            )


def get_lattice_parameters(
    filename: str | Path, entry_name: str, process_group_name: str
) -> Tuple[np.ndarray, int]:
    return find_lattice_parameters(f"{filename}::/{entry_name}/{process_group_name}")


def get_wavelength(
    filename: str | Path, entry_name: str, process_group_name: str
) -> float:
    return find_wavelength(f"{filename}::/{entry_name}/{process_group_name}")
