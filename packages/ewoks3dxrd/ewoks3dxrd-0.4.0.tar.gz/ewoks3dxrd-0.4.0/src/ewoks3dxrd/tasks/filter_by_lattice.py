from pathlib import Path
from typing import Optional

from ewokscore import Task
from pydantic import Field

from ..filtering import filter_by_phase
from ..io import copy_par_file
from ..models import InputsWithOverwrite
from ..nexus.peaks import read_peaks_attributes, save_nexus_process
from ..nexus.utils import (
    check_throw_write_data_group_url,
    get_data_url_paths,
    get_entry_name,
    group_exists,
)


class Inputs(InputsWithOverwrite):
    geometry_updated_data_url: str = Field(
        description="Path to the NXprocess group containing containing the geometry-transformed peaks"
    )
    lattice_file: str = Field(
        description="Path to the `.par` file containing lattice parameters and space group information."
    )
    reciprocal_dist_tol: float = Field(
        description="Tolerance for peak inclusion near lattice rings"
    )
    reciprocal_dist_max: Optional[float] = Field(
        default=None,
        description="Maximum reciprocal distance for filtering. If None or not provided, the maximum value in the `ds` column from input file will be used.",
    )
    process_group_name: str = Field(
        default="lattice_filtered_peaks",
        description="NXprocess group name where to save the filtered peaks",
    )


class FilterByLattice(
    Task,
    input_model=Inputs,
    output_names=["lattice_filtered_data_url", "copied_lattice_file", "ds_tol"],
):
    """
    Performs Lattice/Phase-based filtering on a geometry-transformed 3D peaks file.

    This process applies filtering based on 'reciprocal distance' and 'lattice' rings ds criteria
    to extract relevant peaks.

    ### Steps:
    1. **Initial Filtering:**
        - Copies the input geometry-transformed 3D peaks file.
        - Reads the `ds` column and removes rows where `ds` exceeds the specified `reciprocal_dist_max` value.

    2. **Lattice-Based Filtering:**
        - Computes ideal lattice ring `ds` values (reciprocal distances from the origin).
        - Further filters peaks based on these values, using the tolerance defined by `reciprocal_dist_tol`.

    3. **File Storage:**
        - Saves the lattice-filtered 3D peaks file as
            `{Lattice_name}_{reciprocal_dist_max_tag}_filtered_3d_peaks.h5,flt`
            in the parent directory of the input file ('geometry_trans_3d_peaks_file').

    Additionally, if the specified `lattice_file` is not present in the sample analysis path,
    it is copied to `"par_folder/{lattice_file}"`.

    ### Outputs
    - `lattice_filtered_data_url` (str): Data path to the lattice filtered 'NxProcess group data' peaks
    - `copied_lattice_file` (str): Path to the copied lattice parameter file stored within the analysis folder.
    - `ds_tol` (float): Forwarding the value of `reciprocal_dist_tol` for the future tasks
    """

    def run(self):
        inputs = Inputs(**self.get_input_values())

        nexus_file_path, geometry_updated_data_group_path = get_data_url_paths(
            inputs.geometry_updated_data_url
        )
        if not group_exists(nexus_file_path, geometry_updated_data_group_path):
            raise FileNotFoundError(
                f""" File or Data Group not Found Error,
                Either it is missing nexus file path: {nexus_file_path} or
                geometry updated data group path: {geometry_updated_data_group_path}.
                """
            )

        entry_name = get_entry_name(geometry_updated_data_group_path)
        check_throw_write_data_group_url(
            inputs.overwrite,
            nexus_file_path,
            f"{entry_name}/{inputs.process_group_name}",
        )

        lattice_file = copy_par_file(inputs.lattice_file, Path(nexus_file_path).parent)

        peaks = read_peaks_attributes(
            filename=nexus_file_path,
            process_group=geometry_updated_data_group_path,
        )

        ds_tol = inputs.reciprocal_dist_tol
        ds_max = inputs.reciprocal_dist_max
        filtered_peaks_cf, unit_cell_parameters = filter_by_phase(
            peaks,
            lattice_file=lattice_file,
            ds_tol=ds_tol,
            ds_max=ds_max,
        )

        nxprocess_url = save_nexus_process(
            filename=nexus_file_path,
            entry_name=entry_name,
            process_name=inputs.process_group_name,
            peaks_data=filtered_peaks_cf,
            config_settings={
                "lattice_name": lattice_file.stem,
                "lattice_parameters": unit_cell_parameters.lattice_parameters,
                "lattice_space_group": unit_cell_parameters.space_group,
                "dsmax": ds_max if ds_max is None else "None",
                "dstol": ds_tol,
                "data_from": f"{nexus_file_path}::{geometry_updated_data_group_path}",
            },
            pks_axes=("ds", "eta"),
            overwrite=inputs.overwrite,
        )

        self.outputs.lattice_filtered_data_url = nxprocess_url
        self.outputs.copied_lattice_file = str(lattice_file)
        self.outputs.ds_tol = ds_tol
