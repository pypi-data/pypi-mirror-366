from __future__ import annotations

from pathlib import Path
from typing import List

from ImageD11.grain import grain as Grain
from ImageD11.grain import read_grain_file
from ImageD11.grid_index_parallel import grid_index_parallel

from .models import GridIndexParameters, Translations
from .nexus.utils import get_data_url_paths, get_entry_name
from .nexus.parameters import find_lattice_nexus_group_url
from .nexus.peaks import save_column_file_as_ascii

from .tmp_files import tmp_lattice_and_geo_file


def run_grid_indexing(
    input_data_url: str,
    grid_index_parameters: GridIndexParameters,
    analyse_folder: str | Path,
    translations: Translations,
) -> List[Grain]:
    nexus_file_path, indexer_filtered_data_url = get_data_url_paths(input_data_url)
    entry_name = get_entry_name(indexer_filtered_data_url)

    analyse_folder = (
        Path(analyse_folder) if analyse_folder else Path(nexus_file_path).parent
    )
    output_file = str(analyse_folder / "grid_indexed_grains.map")
    with tmp_lattice_and_geo_file(
        lat_par_data_url=find_lattice_nexus_group_url(input_data_url),
        geo_par_data_url=f"{nexus_file_path}::{entry_name}/geometry_updated_peaks",
    ) as par_file:
        grid_peaks_path = analyse_folder / "phase_index_filtered_peaks.flt"
        save_column_file_as_ascii(input_data_url, grid_peaks_path)
        grid_index_parallel(
            fltfile=grid_peaks_path,
            parfile=str(par_file),
            tmp=str(par_file.parent),
            gridpars={
                "output_filename": output_file,
                **grid_index_parameters.model_dump(),
            },
            translations=translations,
        )

    return read_grain_file(output_file)
