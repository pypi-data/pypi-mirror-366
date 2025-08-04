from pathlib import Path

from ewokscore import Task
from pydantic import Field

from ..io import copy_par_file
from ..models import InputsWithOverwrite
from ..nexus.peaks import read_peaks_attributes, save_nexus_process
from ..nexus.utils import (
    check_throw_write_data_group_url,
    get_data_url_paths,
    get_entry_name,
)
from ..utils import update_geometry


class Inputs(InputsWithOverwrite):
    spatial_corrected_data_url: str = Field(
        description="Path to the NXprocess group containing the detector spatial corrected 3D peaks"
    )
    geometry_par_file: str = Field(
        description="Path to the `.par` file containing geometry parameters"
    )


class GeometryTransformation(
    Task,
    input_model=Inputs,
    output_names=["geometry_updated_data_url", "wavelength"],
):
    """
    This task performs the following operations:
    1. Gathers geometry information from the `geometry_tdxrd.par` file.
    2. Copy the geometry file in the directory structure:
            `analysis_folder / dset_name / (dset_name + sample_name)`.
            i.e the parent folder of 'detector_spatial_corrected_3d_peaks_file'
    3. Applies the geometry correction to the 3D peaks column file using
        the `ImageD11` dataset class.
    4. Save the geometry corrected 3d peaks columnfile (output: `geometry_updated_3d_peaks_file`)
    """

    def run(self):
        inputs = Inputs(**self.get_input_values())
        nexus_file_path, spatial_corrected_data_group_path = get_data_url_paths(
            inputs.spatial_corrected_data_url
        )

        entry_name = get_entry_name(spatial_corrected_data_group_path)
        geo_updated_data_group = f"{entry_name}/geometry_updated_peaks"
        check_throw_write_data_group_url(
            inputs.overwrite, nexus_file_path, geo_updated_data_group
        )

        sp_corrected_3d_peaks = read_peaks_attributes(
            filename=nexus_file_path,
            process_group=spatial_corrected_data_group_path,
        )
        geometry_file = copy_par_file(
            inputs.geometry_par_file, Path(nexus_file_path).parent
        )
        peaks_data, geom_parameters = update_geometry(
            sp_corrected_3d_peaks, geometry_file
        )

        nxprocess_url = save_nexus_process(
            filename=nexus_file_path,
            entry_name=entry_name,
            process_name="geometry_updated_peaks",
            peaks_data=peaks_data,
            config_settings=geom_parameters,
            pks_axes=("ds", "eta"),
            overwrite=inputs.overwrite,
            ln_pks_from_group_name=spatial_corrected_data_group_path,
        )
        self.outputs.geometry_updated_data_url = nxprocess_url
        self.outputs.wavelength = geom_parameters["wavelength"]
