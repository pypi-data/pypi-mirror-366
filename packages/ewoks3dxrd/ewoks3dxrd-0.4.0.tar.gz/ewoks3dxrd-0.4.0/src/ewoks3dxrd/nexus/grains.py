from __future__ import annotations

from pathlib import Path
from typing import Any, List, Tuple

import h5py
import numpy as np
from ImageD11 import grain as grainmod
from ImageD11.grain import grain as Grain
from silx.io.utils import h5py_read_dataset

from .parameters import create_parameters_group


def create_nexus_grains_data_group(
    group_path: h5py.Group,
    grains: List[Grain],
) -> str:

    if not grains:
        raise ValueError("Grains list is empty!")

    grain_data_group = group_path.require_group("grains")
    grain_data_group.attrs["NX_class"] = "NXdata"
    num_grains = len(grains)

    ubi_matrices = grain_data_group.create_dataset(
        "UBI", shape=(num_grains, 3, 3), dtype=grains[0].ubi.dtype
    )
    translations = grain_data_group.create_dataset(
        "translation", shape=(num_grains, 3), dtype=grains[0].ubi.dtype
    )
    npks = grain_data_group.create_dataset("npks", shape=(num_grains,), dtype=np.int64)
    nuniq = grain_data_group.create_dataset(
        "nuniq", shape=(num_grains,), dtype=np.int64
    )
    names = grain_data_group.create_dataset(
        "name", shape=(num_grains,), dtype=h5py.string_dtype(encoding="utf-8")
    )
    intensity_infos = grain_data_group.create_dataset(
        "intensity_info", shape=(num_grains,), dtype=h5py.string_dtype(encoding="utf-8")
    )
    mean_intensity = grain_data_group.create_dataset(
        "mean_intensity", shape=(num_grains,), dtype=np.float64
    )

    for i, grain in enumerate(grains):
        ubi_matrices[i] = grain.ubi
        if hasattr(grain, "translation"):
            translations[i] = grain.translation
        if hasattr(grain, "npks"):
            npks[i] = grain.npks
        if hasattr(grain, "nuniq"):
            nuniq[i] = grain.nuniq
        if hasattr(grain, "name"):
            names[i] = grain.name
        if hasattr(grain, "intensity_info"):
            intensity_infos[i] = grain.intensity_info
            if "no peaks" in grain.intensity_info:
                mean_intensity[i] = 0
            else:
                mean_intensity[i] = float(
                    grain.intensity_info.split("mean = ")[1]
                    .split(" , ")[0]
                    .replace("'", "")
                )

    return grain_data_group.name


def save_nexus_grain_process(
    filename: str | Path,
    entry_name: str,
    process_name: str,
    config_settings: dict[str, Any] | dict[str, dict[str, Any]],
    grains: List[Grain],
    overwrite: bool = False,
) -> str:
    with h5py.File(filename, "a") as h5_file:
        entry = h5_file.require_group(entry_name)
        entry.attrs["NX_class"] = "NXentry"
        if process_name in entry:
            if overwrite:
                del entry[process_name]
            else:
                raise FileExistsError(
                    f"""In the nexus process file name {filename}, there is already a
                    nexus process group {process_name} exists.
                    To overwrite provide a overwrite permission.
                    """
                )

        process_group = entry.create_group(process_name)
        process_group.attrs["NX_class"] = "NXprocess"
        create_nexus_grains_data_group(
            group_path=process_group,
            grains=grains,
        )
        create_parameters_group(
            group_path=process_group,
            config_settings=config_settings,
        )
        return f"{filename}::{process_group.name}"


def create_nexus_ubi(
    grains: List[Grain],
    entry_name: str,
    grain_file: str | Path,
    grain_settings: dict[str, Any],
    peaks_path: Tuple[str | Path, str],
):
    """
    Create nexus file with entry_name place the grains (list of UBIs)
    and also link the peaks used to generate these UBIS as external link
    """
    with h5py.File(grain_file, "w") as gf:
        entry = gf.create_group(entry_name)
        entry.attrs["NX_class"] = "NXentry"
        grain_group = entry.create_group("indexed_grains")
        grain_group.attrs["NX_class"] = "NXprocess"
        grain_group["peaks"] = h5py.ExternalLink(peaks_path[0], peaks_path[1])
        ubi_group = grain_group.create_group("UBI")
        ubi_group.attrs["NX_class"] = "NXdata"
        ubi_matrices = ubi_group.create_dataset(
            "UBI", shape=(len(grains), 3, 3), dtype=grains[0].ubi.dtype
        )
        for i, grain in enumerate(grains):
            ubi_matrices[i] = grain.ubi
        create_parameters_group(
            parent_group=grain_group, config_settings=grain_settings
        )


def create_nexus_grains(
    grains: List[Grain],
    entry_name: str,
    grain_file: str | Path,
    grain_settings: dict[str, Any],
    grain_group_name: str,
):
    num_grains = len(grains)
    with h5py.File(grain_file, "a") as gf:
        entry = gf[entry_name]
        grp = entry.create_group(grain_group_name)
        grp.attrs["NX_class"] = "NXprocess"
        grains_gr = grp.create_group("grains")
        grains_gr.attrs["NX_class"] = "NXdata"

        ubi_matrices = grains_gr.create_dataset(
            "UBI", shape=(num_grains, 3, 3), dtype=grains[0].ubi.dtype
        )
        translations = grains_gr.create_dataset(
            "translation", shape=(num_grains, 3), dtype=grains[0].ubi.dtype
        )
        npks = grains_gr.create_dataset("npks", shape=(num_grains,), dtype=np.int64)
        nuniq = grains_gr.create_dataset("nuniq", shape=(num_grains,), dtype=np.int64)
        for i, grain in enumerate(grains):
            ubi_matrices[i] = grain.ubi
            translations[i] = grain.translation
            npks[i] = grain.npks
            nuniq[i] = grain.nuniq

        create_parameters_group(parent_group=grp, config_settings=grain_settings)


def read_grains(
    grain_file_h5: str | Path, entry_name: str, process_group_name: str
) -> List[Grain]:

    grains_list = []
    with h5py.File(grain_file_h5, "r") as gf:
        entry = gf[f"{entry_name}/{process_group_name}/grains"]
        for i in range(entry["translation"][()].shape[0]):
            gr = Grain(ubi=entry["UBI"][i], translation=entry["translation"][i])
            gr.npks = entry["npks"][i]
            gr.nuniq = entry["nuniq"][i]
            gr.name = entry["name"][i]
            gr.intensity_info = h5py_read_dataset(entry["intensity_info"], index=i)
            gr.mean_intensity = entry["mean_intensity"][i]
            grains_list.append(gr)
    return grains_list


def read_grains_attributes(filename: str | Path, process_group: str) -> dict[str, list]:
    with h5py.File(filename, "r") as h5file:
        grain_group = h5file[f"{process_group}/grains"]
        return {name: dataset[()] for name, dataset in grain_group.items()}


def save_indexed_grains_as_ascii(
    grain_file_h5: str | Path,
    process_group_path: str,
    grain_file_ascii: str | Path,
):
    """
    Function to extract grains that generated by Indexing function,
    which is simpler, i.e it only has UBI matrices.
    """
    grains_list = []
    with h5py.File(grain_file_h5, "r") as gf:
        ubi_dataset = gf[f"{process_group_path}/grains/UBI"]
        for ubi_matrix in ubi_dataset:
            grains_list.append(Grain(ubi=ubi_matrix))

    grainmod.write_grain_file(grain_file_ascii, grains_list)
