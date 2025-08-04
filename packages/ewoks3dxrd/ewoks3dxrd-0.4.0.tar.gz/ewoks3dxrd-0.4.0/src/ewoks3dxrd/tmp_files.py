from __future__ import annotations
import os
import shutil
import tempfile
from pathlib import Path
from contextlib import contextmanager
from typing import Tuple, Generator
from silx.io.utils import DataUrl

from .nexus.parameters import get_parameters
from .nexus.grains import save_indexed_grains_as_ascii
from .io import (
    load_par_or_cif_file,
    save_geometry_and_lattice_file,
    read_lattice_cell_data,
)


@contextmanager
def tmp_processing_files(
    initial_ubi_file: str | Path, geo_par_file: str | Path, lattice_file: str | Path
) -> Generator[Tuple[str, str], None, None]:
    _, tmp_ubi_file = tempfile.mkstemp()
    _, tmp_par_file = tempfile.mkstemp()

    try:
        shutil.copy2(initial_ubi_file, tmp_ubi_file)

        with open(tmp_par_file, "w") as file:
            geometry_parameters = load_par_or_cif_file(geo_par_file)
            for key, value in geometry_parameters.items():
                file.write(f"{key} {value}\n")

            lattice_parameters = load_par_or_cif_file(lattice_file)
            for key, value in lattice_parameters.items():
                file.write(f"{key} {value}\n")

        yield tmp_ubi_file, tmp_par_file
    finally:
        os.remove(tmp_ubi_file)
        os.remove(tmp_par_file)


@contextmanager
def tmp_grain_processing_files(
    ubi_init_data_url: str, geo_init_data_url: str, lattice_parameter_file: str
) -> Generator[Tuple[str, str], None, None]:
    _, tmp_ubi_file = tempfile.mkstemp()
    _, tmp_par_file = tempfile.mkstemp()

    try:
        ubi_url = DataUrl(ubi_init_data_url)
        save_indexed_grains_as_ascii(
            grain_file_h5=ubi_url.file_path(),
            process_group_path=ubi_url.data_path(),
            grain_file_ascii=tmp_ubi_file,
        )

        geo_url = DataUrl(geo_init_data_url)
        geo_par_dict = get_parameters(
            filename=geo_url.file_path(),
            process_group_name=geo_url.data_path(),
        )
        unit_cell_parameters = read_lattice_cell_data(
            lattice_data_file_path=lattice_parameter_file
        )
        save_geometry_and_lattice_file(
            file_path=tmp_par_file,
            geom_dict=geo_par_dict,
            lattice_dict={
                "lattice_parameters": unit_cell_parameters.lattice_parameters,
                "lattice_space_group": unit_cell_parameters.space_group,
            },
        )

        yield tmp_ubi_file, tmp_par_file
    finally:
        os.remove(tmp_ubi_file)
        os.remove(tmp_par_file)


@contextmanager
def tmp_lattice_and_geo_file(
    lat_par_data_url: str, geo_par_data_url: str
) -> Generator[Path, None, None]:
    with tempfile.TemporaryDirectory() as tmp_dir:
        geo_url = DataUrl(geo_par_data_url)
        geo_par_dict = get_parameters(
            filename=geo_url.file_path(),
            process_group_name=geo_url.data_path(),
        )
        lat_url = DataUrl(lat_par_data_url)
        lat_par_dict = get_parameters(
            filename=lat_url.file_path(),
            process_group_name=lat_url.data_path(),
        )
        tmp_par_file = Path(tmp_dir) / "tmp.par"
        save_geometry_and_lattice_file(
            file_path=tmp_par_file,
            geom_dict=geo_par_dict,
            lattice_dict=lat_par_dict,
        )
        yield tmp_par_file
