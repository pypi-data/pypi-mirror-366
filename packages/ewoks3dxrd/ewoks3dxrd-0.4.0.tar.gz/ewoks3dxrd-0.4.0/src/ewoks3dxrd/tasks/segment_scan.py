from pathlib import Path
from typing import Optional

import h5py
from ewokscore import TaskWithProgress
from ImageD11 import frelon_peaksearch

from ..io import extract_sample_info, get_monitor_scale_factor
from ..models import (
    InputsWithOverwrite,
    SegmenterConfig,
    SegmenterCorrectionFiles,
    SegmenterFolderConfig,
)
from ..nexus.peaks import save_nexus_process
from ..nexus.utils import group_exists
from ..tqdm_progress_callback import TqdmProgressCallback


class Inputs(InputsWithOverwrite):
    folder_config: SegmenterFolderConfig
    segmenter_algo_params: SegmenterConfig
    correction_files: SegmenterCorrectionFiles
    monitor_name: Optional[str] = None


class SegmentScan(
    TaskWithProgress,
    input_model=Inputs,
    output_names=["sample_folder_info", "segmented_peaks_url"],
):
    """
    This task segments an entire scan folder,
    merges the peaks, and produces a 3D column file.
    The resulting 3D column peak file is saved.

    Outputs:

    - `sample_folder_info`: A Config information about raw scan sample
    - `segmented_peaks_url`: A Nexus file data url path to `segmented_3d_peaks` data
    """

    def run(self):
        inputs = Inputs(**self.get_input_values())
        seg_folder_config = inputs.folder_config

        detector = seg_folder_config.detector
        omega_motor = seg_folder_config.omega_motor
        master_file = seg_folder_config.master_file
        scan_number = seg_folder_config.scan_number

        _, sample_name, dset_name = extract_sample_info(master_file=master_file)

        masterfile_path = Path(master_file)
        if not masterfile_path.exists():
            raise FileNotFoundError(f"""{masterfile_path} does not exist.""")

        analyse_folder = seg_folder_config.analyse_folder
        output_folder = (
            Path(analyse_folder) / sample_name / f"{sample_name}_{dset_name}"
        )
        output_folder.mkdir(parents=True, exist_ok=True)
        nexus_file_path = output_folder / f"{sample_name}_{dset_name}.h5"
        seg_data_group_path = f"{str(scan_number)}.1/segmented_3d_peaks"
        overwrite = inputs.overwrite
        if not overwrite and group_exists(
            filename=nexus_file_path, data_group_path=seg_data_group_path
        ):
            raise ValueError(
                f"""Data group '{seg_data_group_path}' already exists in {nexus_file_path},
                Set `overwrite` to True if you wish to overwrite the existing data group.
                """
            )

        with h5py.File(masterfile_path, "r") as hin:
            omega_angles = hin[str(scan_number) + ".1"]["measurement"].get(
                omega_motor, None
            )
            omega_array = omega_angles[()]

        segmenter_cfg = inputs.segmenter_algo_params
        correction_files_config = inputs.correction_files
        segmenter_settings = {
            "bgfile": correction_files_config.bg_file,
            "maskfile": correction_files_config.mask_file,
            "darkfile": correction_files_config.dark_file,
            "flatfile": correction_files_config.flat_file,
            "threshold": segmenter_cfg.threshold,
            "smoothsigma": segmenter_cfg.smooth_sigma,
            "bgc": segmenter_cfg.bgc,
            "minpx": segmenter_cfg.min_px,
            "m_offset_thresh": segmenter_cfg.offset_threshold,
            "m_ratio_thresh": segmenter_cfg.ratio_threshold,
        }

        monitor_name = inputs.monitor_name
        scale_factor = (
            None
            if monitor_name is None
            else get_monitor_scale_factor(masterfile_path, scan_number, monitor_name)
        )

        all_frames_2d_peaks_list = frelon_peaksearch.segment_master_file(
            str(masterfile_path),
            str(scan_number) + ".1" + "/measurement/" + detector,
            omega_array,
            segmenter_settings,
            scale_factor=scale_factor,
            tqdm_class=TqdmProgressCallback,
            TaskInstance=self,
        )
        peaks_2d_dict, num_peaks = frelon_peaksearch.peaks_list_to_dict(
            all_frames_2d_peaks_list
        )
        # 3d merge from 2d peaks dict
        peak_3d_dict = frelon_peaksearch.do3dmerge(
            peaks_2d_dict, num_peaks, omega_array
        )

        self.outputs.sample_folder_info = {
            "omega_motor": omega_motor,
            "master_file": master_file,
            "scan_number": scan_number,
        }

        nxprocess_url = save_nexus_process(
            filename=nexus_file_path,
            entry_name=f"{str(scan_number)}.1",
            process_name="segmented_3d_peaks",
            peaks_data=peak_3d_dict,
            config_settings={
                "FolderFileSettings": seg_folder_config.model_dump(),
                "Segmenter_settings": segmenter_settings,
            },
            overwrite=overwrite,
        )
        self.outputs.segmented_peaks_url = nxprocess_url
