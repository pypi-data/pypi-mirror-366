from pathlib import Path
from typing import Optional, Union

import numpy as np
from ewokscore import Task
from pydantic import Field

from ..indexing import run_grid_indexing
from ..io import find_omega_slop
from ..models import GridIndexParameters, InputsWithOverwrite, SampleConfig
from ..nexus.grains import save_nexus_grain_process
from ..nexus.parameters import read_nx_collection_parameters
from ..nexus.utils import (
    check_throw_write_data_group_url,
    get_data_url_paths,
    get_entry_name,
)
from ..utils import generate_translations


class Inputs(InputsWithOverwrite):
    indexer_filtered_data_url: str = Field(
        description="Path to NXprocess group containing the filtered (be it by index, lattice or intensity) peaks"
    )
    grid_index_parameters: GridIndexParameters = Field(
        description="""dict of following parameters:
        - `NPKS`       (int)           : number of peaks
        - `DSTOL`      (float)         :  reciprocal distance tolerance
        - `RING1`      (Sequence[int]) : default (1, 0)
        - `RING2`      (Sequence[int]) : default (0,)
        - `NUL`        (bool)          : default True
        - `FITPOS`     (bool)          : default True
        - `tolangle`   (float)         : default 0.50
        - `toldist`    (float)         : default 100.0
        - `NPROC`      (int)           : default None, but ImageD11 will set it to maximum available cores on the server
        - `NTHREAD`    (int)           : default 1
        - `COSTOL`     (float)         : default None (from model) if default provided then here will set it to np.cos(np.radians(90 - 2 * omega_slop))
        - `OMEGAFLOAT` (float)         : default None (from model) if default provided then here will set it to omega_slop
            Note: omega_slop is related to wobble of the instrument,
        - `TOLSEQ` (Tuple[float, ...]) : default (0.02, 0.015, 0.01)
        - `SYMMETRY` (str)             : default cubic"""
    )
    analyse_folder: Union[str, Path, None] = None
    grid_abs_x_limit: int = Field(
        default=600,
        description="X limit of the 3D space to search translation positions of grains.",
    )
    grid_abs_y_limit: int = Field(
        default=600,
        description="Y limit of the 3D space to search translation positions of grains.",
    )
    grid_abs_z_limit: int = Field(
        default=200,
        description="Z limit of the 3D space to search translation positions of grains.",
    )
    grid_step: int = Field(
        default=100,
        description="Step size of the 3D space to search translation positions of grains.",
    )
    seed: Optional[int] = Field(
        default=42,
        description="Seed for translation shuffling. Pass `None` to disable translation shuffling",
    )
    sample_config: Optional[SampleConfig] = Field(
        default=None,
        description="Override the sample config. If not provided, it will be retrieved from the segmentation step",
    )


class GridIndexGrains(
    Task,
    input_model=Inputs,
    output_names=["grid_indexed_grain_data_url"],
):
    """
    From 3D peaks, finds grains' UBI  matrices and stores them in NeXus (.h5) format.

    ```{warning}
    This task is still experimental and may break or change without notice.
    ```

    Outputs:
    - `grid_indexed_grain_data_url` (str): Data path to 'NxProcess group data' grains that stores generated UBI

    """

    def run(self):
        inputs = Inputs(**self.get_input_values())
        nexus_file_path, indexer_filtered_data_group_path = get_data_url_paths(
            inputs.indexer_filtered_data_url
        )

        entry_name = get_entry_name(indexer_filtered_data_group_path)
        grid_indexed_ubi_data_group = f"{entry_name}/grid_indexed_grains"
        check_throw_write_data_group_url(
            overwrite=inputs.overwrite,
            filename=nexus_file_path,
            data_group_path=grid_indexed_ubi_data_group,
        )

        filename, process_group_name = get_data_url_paths(
            f"{nexus_file_path}::{entry_name}/segmented_3d_peaks"
        )
        sample_config = inputs.sample_config
        if sample_config is None:
            sample_config = SampleConfig(
                **read_nx_collection_parameters(
                    filename=filename,
                    process_group_name=process_group_name,
                    sub_folder="parameters/FolderFileSettings",
                )
            )

        omega_slop = find_omega_slop(sample_config)

        grid_index_parameters = inputs.grid_index_parameters
        if grid_index_parameters.COSTOL is None:
            grid_index_parameters.COSTOL = np.cos(np.radians(90 - 2 * omega_slop))
        if grid_index_parameters.OMEGAFLOAT is None:
            grid_index_parameters.OMEGAFLOAT = omega_slop

        analyse_folder = (
            Path(inputs.analyse_folder)
            if inputs.analyse_folder
            else Path(nexus_file_path).parent
        )

        grid_indexed_grains = run_grid_indexing(
            input_data_url=inputs.indexer_filtered_data_url,
            grid_index_parameters=grid_index_parameters,
            analyse_folder=analyse_folder,
            translations=generate_translations(
                max_x=inputs.grid_abs_x_limit,
                max_y=inputs.grid_abs_y_limit,
                max_z=inputs.grid_abs_z_limit,
                step=inputs.grid_step,
                seed=inputs.seed,
            ),
        )

        ubi_grains_group_name = save_nexus_grain_process(
            filename=nexus_file_path,
            entry_name=entry_name,
            process_name="grid_indexed_grains",
            config_settings={
                **grid_index_parameters.model_dump(exclude_none=True),
                "data_from": self.inputs.indexer_filtered_data_url,
                "grid_abs_x_limit": inputs.grid_abs_x_limit,
                "grid_abs_y_limit": inputs.grid_abs_y_limit,
                "grid_abs_z_limit": inputs.grid_abs_z_limit,
                "grid_step": inputs.grid_step,
            },
            grains=grid_indexed_grains,
            overwrite=inputs.overwrite,
        )
        self.outputs.grid_indexed_grain_data_url = ubi_grains_group_name
