from ewoks import Task
from pydantic import Field

from ..filtering import filter_by_intensity
from ..models import InputsWithOverwrite
from ..nexus.peaks import read_peaks_attributes, save_nexus_process
from ..nexus.utils import (
    check_throw_write_data_group_url,
    get_data_url_paths,
    get_entry_name,
)


class Inputs(InputsWithOverwrite):
    lattice_filtered_data_url: str = Field(
        description="Path to the NXprocess group containing the peaks corrected for geometry and detector"
    )
    intensity_frac: float = Field(
        ge=0,
        le=1,
        description="Filter peaks whose intensity is below this value",
    )
    process_group_name: str = Field(
        default="intensity_filtered_peaks",
        description="NXprocess group name where to save the filtered peaks",
    )


class FilterByIntensity(
    Task, input_model=Inputs, output_names=["intensity_filtered_data_url"]
):
    """
    Does the Intensity based peaks filter,
        computes intensity metric based on sum_intensity, ds (reciprocal distance) columns from the input file
        normalize with the maximum value of intensity metric,
        only keeps the rows whose value is above the given input 'intensity_frac'
        and save them in .h5 format.

    Outputs:

    - `intensity_filtered_data_url` (str): Data path to the intensity filtered 'NxProcess group data' peaks
    """

    def run(self):
        inputs = Inputs(**self.get_input_values())
        nexus_file_path, lattice_filtered_data_group_path = get_data_url_paths(
            inputs.lattice_filtered_data_url
        )

        entry_name = get_entry_name(lattice_filtered_data_group_path)

        check_throw_write_data_group_url(
            inputs.overwrite,
            nexus_file_path,
            f"{entry_name}/{inputs.process_group_name}",
        )

        filtered_3d_peaks_dict = filter_by_intensity(
            peaks=read_peaks_attributes(
                filename=nexus_file_path, process_group=lattice_filtered_data_group_path
            ),
            intensity_frac=inputs.intensity_frac,
        )

        nxprocess_url = save_nexus_process(
            filename=nexus_file_path,
            entry_name=entry_name,
            process_name=inputs.process_group_name,
            peaks_data=filtered_3d_peaks_dict,
            config_settings={
                "intensity_frac": inputs.intensity_frac,
                "data_from": f"{nexus_file_path}::{lattice_filtered_data_group_path}",
            },
            pks_axes=("ds", "eta"),
            overwrite=inputs.overwrite,
        )
        self.outputs.intensity_filtered_data_url = nxprocess_url
