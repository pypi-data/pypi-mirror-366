from __future__ import annotations
from typing import Any, Optional, Tuple
import numpy as np
import h5py
from pathlib import Path
from ImageD11 import columnfile as PeakColumnFile
from .parameters import create_parameters_group, get_data_url_paths


def create_nexus_peaks_data_group(
    group_path: h5py.Group,
    peaks_data: dict[str, np.ndarray],
    pks_axes: Tuple[str, str],
    signal_name: str,
    scale: str,
    soft_ln_pks_path: Optional[str] = None,
) -> str:

    peak_data_group = group_path.require_group("peaks")
    peak_data_group.attrs["NX_class"] = "NXdata"
    for key, value in peaks_data.items():
        peak_data_group.create_dataset(key, data=value)

    if soft_ln_pks_path:
        soft_ln_pks_group = group_path.file[soft_ln_pks_path]
        if "peaks" in soft_ln_pks_group:
            soft_link_peaks = soft_ln_pks_group["peaks"]
            for key in soft_link_peaks.keys():
                if key not in peak_data_group:
                    peak_data_group[key] = h5py.SoftLink(soft_link_peaks[key].name)

    peak_data_group.attrs["axes"] = pks_axes
    peak_data_group.attrs["signal"] = signal_name

    if scale not in ["log", "linear"]:
        raise ValueError("scale must be 'log' or 'linear'")

    peak_data_group.attrs["scale"] = scale
    return peak_data_group.name


def save_nexus_process(
    filename: str | Path,
    entry_name: str,
    process_name: str,
    peaks_data: dict[str, np.ndarray],
    config_settings: dict[str, Any] | dict[str, dict[str, Any]],
    pks_axes: Tuple[str, str] = ("f_raw", "s_raw"),
    signal_name: str = "Number_of_pixels",
    scale: str = "log",
    overwrite: bool = False,
    ln_pks_from_group_name: Optional[str] = None,
) -> str:

    with h5py.File(filename, "a") as h5_file:
        entry = h5_file.require_group(entry_name)
        entry.attrs["NX_class"] = "NXentry"

        if process_name in entry:
            if overwrite:
                del entry[process_name]
            else:
                raise FileExistsError(
                    f"""IN the nexus process file name {filename}, there is already a
                    nexus process group {process_name} exists.
                    To overwrite provide a overwrite permission.
                    """
                )

        process_group = entry.create_group(process_name)
        process_group.attrs["NX_class"] = "NXprocess"
        create_nexus_peaks_data_group(
            group_path=process_group,
            peaks_data=peaks_data,
            soft_ln_pks_path=ln_pks_from_group_name,
            pks_axes=pks_axes,
            signal_name=signal_name,
            scale=scale,
        )
        create_parameters_group(
            group_path=process_group,
            config_settings=config_settings,
        )
        return f"{filename}::{process_group.name}"


def read_peaks_attributes(
    filename: str | Path, process_group: str
) -> dict[str, np.ndarray]:
    """
    Extract peaks column data stored in {entry_name}/{process_name}/peaks
    Inputs:
        filename: file path to .h5 file
        entry_name: entry point inside .h5 file
        process_name: group name inside the entry point
    """
    with h5py.File(filename, "r") as f:
        peaks_group = f[f"{process_group}/peaks"]
        return {name: dataset[()] for name, dataset in peaks_group.items()}


def save_column_file_as_ascii(input_data_url: str, output_file_name: Path) -> Path:
    cf_file_path, cf_group_path = get_data_url_paths(input_data_url)
    peaks_dict = read_peaks_attributes(
        filename=cf_file_path, process_group=cf_group_path
    )
    cf = PeakColumnFile.colfile_from_dict(peaks_dict)

    cf.writefile(output_file_name)

    return output_file_name
