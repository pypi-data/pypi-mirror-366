from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, List, Tuple

import h5py
import numpy as np
from ImageD11.grain import grain as Grain

from .models import SampleConfig, UnitCellParameters


def get_monitor_data(
    masterfile_path: str | Path, scan_number: str | int, monitor_name: str
):
    with h5py.File(masterfile_path, "r") as hin:
        instrument_group_1 = f"{scan_number}.1/instrument"
        if monitor_name in hin[instrument_group_1]:
            monitor_array = hin[instrument_group_1][monitor_name]["data"][:]
            return monitor_array

        instrument_group_2 = f"{scan_number}.2/instrument"
        if monitor_name in hin[instrument_group_2]:
            monitor_async_array = hin[instrument_group_2][monitor_name]["data"][:]
            t_sync_seq = hin[instrument_group_1]["epoch_trig/data"][:]
            t_async_seq = hin[instrument_group_2]["epoch"]["value"][:]
            if t_async_seq.shape[0] > monitor_async_array.shape[0]:
                t_async_seq = (t_async_seq[0:-1] + t_async_seq[1:]) / 2
            else:
                t_async_seq = t_async_seq

            monitor_array = np.interp(t_sync_seq, t_async_seq, monitor_async_array)
            return monitor_array

    raise KeyError(
        f""" Given monitor: {monitor_name} not found in the scan_number '{scan_number}''
                of given master file {masterfile_path}.
        """
    )


def get_monitor_scale_factor(
    masterfile_path: str | Path, scan_number: str | int, monitor_name: str
) -> np.ndarray:
    monitor_array = get_monitor_data(
        masterfile_path=masterfile_path,
        scan_number=scan_number,
        monitor_name=monitor_name,
    )
    return np.mean(monitor_array) / monitor_array


def get_optimal_frame_index(
    masterfile_path: str | Path,
    scan_number: str | int,
    detector: str,
    counter: str = "_roi1",
) -> int:
    with h5py.File(masterfile_path, "r") as h5file:
        detector_ctr = detector + counter
        scan_string = str(scan_number) + ".1"
        frame_idx = np.argmax(h5file[f"{scan_string}/measurement/{detector_ctr}"][:])
        return frame_idx


def get_monitor_scale_factor_for_frame_index(
    masterfile_path: str | Path,
    scan_number: str | int,
    detector: str,
    monitor_name: str,
    frame_idx: int | None,
    counter: str = "_roi1",
) -> float:
    monitor_scale_array = get_monitor_scale_factor(
        masterfile_path=masterfile_path,
        scan_number=scan_number,
        monitor_name=monitor_name,
    )

    if frame_idx is None:
        frame_idx = get_optimal_frame_index(
            masterfile_path=masterfile_path,
            scan_number=scan_number,
            detector=detector,
            counter=counter,
        )
    return monitor_scale_array[frame_idx]


def read_wavelength(geometry_par_file: str | Path) -> float:
    with open(geometry_par_file, "r") as f:
        for line in f:
            if line.startswith("wavelength"):
                try:
                    wavelength = float(line.strip().split()[1])
                    break
                except (IndexError, ValueError):
                    raise ValueError(
                        f"Could not found a valid wavelength field in {geometry_par_file}"
                    )
    return wavelength


def get_omega_slop(filepath: str | Path, scan_number: str | int, omega_motor: str):
    """Gets the mean variation of the omega motor, also called slop."""
    with h5py.File(filepath, "r") as hin:
        omega_angles = hin[f"{scan_number}.1/measurement"].get(omega_motor, None)
        if not isinstance(omega_angles, h5py.Dataset):
            raise TypeError(
                f'Could not find a dataset at {filepath}::{scan_number}.1/measurement/{omega_motor}". Got {omega_angles} instead'
            )
        omega_array = omega_angles[()]

    omegas_sorted = np.sort(omega_array)
    return np.round(np.diff(omegas_sorted).mean(), 3) / 2


def extract_sample_info(master_file: str) -> Tuple[str, str, str]:
    """
    Helper function to extract the dataroot, sample, dset_name, scan no from the
    masterfile path
    """
    path = Path(master_file)
    if len(path.parts) < 4:
        raise ValueError(
            "Expected path structure to be of the for `/dataroot/sample_name/dset_name/master_file.h5`"
        )

    # Extract dset name
    dset_folder_name = path.parent.name
    if "_" not in dset_folder_name:
        raise ValueError(
            f"Invalid dataset name: no underscore found in {dset_folder_name} to separate sample and dataset name.",
        )

    dataroot = path.parent.parent.parent.__str__()
    sample_name = path.parent.parent.name
    dset_name = dset_folder_name[len(sample_name + "_") :]
    return dataroot, sample_name, dset_name


def get_frame_image(
    file_path: str | Path,
    detector: str,
    scan_id: str,
    frame_idx: int | None = None,
    counter: str = "_roi1",
) -> np.ndarray:
    """
    extract a frame image from master file path
    """
    with h5py.File(file_path, "r") as h5file:
        if frame_idx is None:
            frame_idx = get_optimal_frame_index(
                masterfile_path=file_path,
                scan_number=scan_id[:-2],
                detector=detector,
                counter=counter,
            )
        return h5file[f"{scan_id}/measurement/{detector}"][frame_idx]


def find_omega_slop(cfg: SampleConfig):
    """Finds the mean variation of the omega motor, also called slop, in the scan file."""
    master_file = Path(cfg.master_file)
    if not master_file.exists():
        raise FileNotFoundError(
            f"""Could not find HDF5 master file at {master_file}."""
        )

    return get_omega_slop(
        filepath=master_file, scan_number=cfg.scan_number, omega_motor=cfg.omega_motor
    )


def copy_par_file(original_par_file: str, dest_folder: Path) -> Path:
    par_file = Path(original_par_file)

    if not par_file.exists():
        raise FileNotFoundError(f"Provided file '{par_file}' does not exist.")

    if par_file.suffix != ".par":
        raise ValueError(f"Provided file '{par_file}' is not a .par file")

    output_file = Path(dest_folder) / "par_folder" / par_file.name
    output_file.parent.mkdir(exist_ok=True)
    shutil.copy2(par_file, output_file)

    return output_file


def load_par_or_cif_file(filepath: str | Path) -> dict:
    """
    Read .par or .cif file, and return each line as key, value pair
    """

    read_parameters = {}
    with open(filepath, "r") as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) != 2:
                continue
            key, value = parts
            read_parameters[key] = value

    return read_parameters


def save_par_file(filepath: str | Path, parameters: dict, mode="w"):
    """
    Saves a .par or .cif file
    """
    with open(filepath, mode) as f:
        for key, value in parameters.items():
            f.write(f"{key} {value}\n")


def read_lattice_cell_data(lattice_data_file_path: str | Path) -> UnitCellParameters:
    """
    Reads lattice cell data from a file and extracts the lattice parameters and space group.
    """
    return UnitCellParameters(**load_par_or_cif_file(lattice_data_file_path))


def save_geometry_and_lattice_file(
    file_path: str | Path, geom_dict: dict[str, Any], lattice_dict: dict[str, Any]
):
    with open(file_path, "w") as f:
        lattice_params = lattice_dict.get("lattice_parameters", [])
        if len(lattice_params) != 6:
            raise ValueError(
                f"Expected a list of 6 lattice params. Got {lattice_params}"
            )
        f.write(f"cell__a {lattice_params[0]}\n")
        f.write(f"cell__b {lattice_params[1]}\n")
        f.write(f"cell__c {lattice_params[2]}\n")
        f.write(f"cell_alpha {lattice_params[3]}\n")
        f.write(f"cell_beta {lattice_params[4]}\n")
        f.write(f"cell_gamma {lattice_params[5]}\n")

        if "lattice_space_group" in lattice_dict:
            f.write(
                f"cell_lattice_[P,A,B,C,I,F,R] {lattice_dict['lattice_space_group']}\n"
            )

    save_par_file(file_path, geom_dict, mode="a")


def save_grains_to_nexus(
    nexus_filename: str | Path,
    geometry_par_path: str | Path,
    lattice_file: str | Path,
    lattice_name: str,
    grains: List[Grain],
) -> None:
    """
    Save grain information (UBI matrices, lattice parameters) and
    the experiment geometry into a NeXus file.

    Parameters:
    - nexus_filename: Output NeXus file path
    - geometry_par_path: Path to the geometry_tdxrd.par file
    - lattice_file: Path to lattice parameters file
    - lattice_name: Name of the lattice type
    - grains (list of grain instances): List of grain objects with:
        - grain.ubi: (3,3) array
    """

    unit_cell_parameters = read_lattice_cell_data(lattice_data_file_path=lattice_file)
    lattice_parameters, space_group = (
        unit_cell_parameters.lattice_parameters,
        unit_cell_parameters.space_group,
    )

    with open(geometry_par_path, "r") as f:
        geometry_lines = [line.strip() for line in f]
    geometry_par = "\n".join(geometry_lines)

    num_grains = len(grains)
    ubi_matrices = np.zeros((num_grains, 3, 3), dtype=grains[0].ubi.dtype)
    translations = np.full((num_grains, 3), fill_value=np.nan)

    for i, grain in enumerate(grains):
        ubi_matrices[i] = grain.ubi
        if grain.translation is not None:
            translations[i] = grain.translation

    with h5py.File(nexus_filename, "w") as f:
        entry = f.create_group("entry")
        entry.attrs["NX_class"] = "NXentry"
        index_grains = entry.create_group("indexed_grains")
        index_grains.attrs["NX_class"] = "NXprocess"
        parameters_group = index_grains.create_group("parameters")
        parameters_group.attrs["NX_class"] = "NXcollection"
        parameters_group.create_dataset("geometry_par", data=geometry_par)
        parameters_group.create_dataset("lattice_name", data=lattice_name)
        parameters_group.create_dataset(
            "lattice_parameters", data=np.array(lattice_parameters)
        )
        if isinstance(space_group, int):
            parameters_group.create_dataset("space_group_number", data=space_group)
        else:
            parameters_group.create_dataset("space_group_symbol", data=space_group)

        grains_group = index_grains.create_group("grains")
        grains_group.attrs["NX_class"] = "NXdata"
        grains_group.create_dataset("UBI", data=ubi_matrices)
        grains_group.create_dataset("translation", data=translations)
