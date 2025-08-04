from ewoks import Task
from pydantic import Field

from ..models import DetectorCorrectionFiles, InputsWithOverwrite
from ..nexus.peaks import read_peaks_attributes, save_nexus_process
from ..nexus.utils import (
    check_throw_write_data_group_url,
    get_data_url_paths,
    get_entry_name,
    group_exists,
)
from ..utils import do_spatial_correction


class Inputs(InputsWithOverwrite):
    segmented_peaks_url: str = Field(
        description="Path to the NXprocess group containing the segmeted peaks"
    )
    correction_files: DetectorCorrectionFiles = Field(
        description="""two corrections are possible:

        - Spline correction: `correction_files` should be a string containing the path to the spline file
        - e2dx,e2dy correction: `correction_files` should be a tuple of 2 strings, the first one being the path to e2dx file, the second the path to the e2dy file
        - any other type will be treated as invalid input""",
        examples=["eiger.spline", ("eiger.e2dx", "eiger.e2dy")],
    )


class DetectorSpatialCorrection(
    Task,
    input_model=Inputs,
    output_names=["spatial_corrected_data_url"],
):
    """
    Does the detector spatial correction on the segmented 3d peaks and saves the corrected 3D column peak file

    Outputs:
    - `spatial_corrected_data_url`: A Nexus file path along with data entry point to `spatial_corrected_peaks` data group
    """

    def run(self):
        inputs = Inputs(**self.get_input_values())

        nexus_file_path, segmented_data_group_path = get_data_url_paths(
            inputs.segmented_peaks_url
        )

        if not group_exists(nexus_file_path, segmented_data_group_path):
            raise FileNotFoundError(
                f""" File or Data Group not Found Error,
                Either it is missing nexus file path: {nexus_file_path} or
                segmented data group path: {segmented_data_group_path}.
                """
            )

        output_entry = get_entry_name(segmented_data_group_path)
        output_process = "spatial_corrected_peaks"
        check_throw_write_data_group_url(
            overwrite=inputs.overwrite,
            filename=nexus_file_path,
            data_group_path=f"{output_entry}/{output_process}",
        )

        segmented_3d_peaks = read_peaks_attributes(
            filename=nexus_file_path,
            process_group=segmented_data_group_path,
        )
        columnfile_3d = do_spatial_correction(
            segmented_3d_peaks, inputs.correction_files
        )

        nxprocess_url = save_nexus_process(
            filename=nexus_file_path,
            entry_name=output_entry,
            process_name=output_process,
            peaks_data={"sc": columnfile_3d["sc"], "fc": columnfile_3d["fc"]},
            config_settings={
                "correction_files": inputs.correction_files,
                "in_peaks_data_from": inputs.segmented_peaks_url,
            },
            pks_axes=("fc", "sc"),
            overwrite=inputs.overwrite,
            ln_pks_from_group_name=segmented_data_group_path,
        )
        self.outputs.spatial_corrected_data_url = nxprocess_url
