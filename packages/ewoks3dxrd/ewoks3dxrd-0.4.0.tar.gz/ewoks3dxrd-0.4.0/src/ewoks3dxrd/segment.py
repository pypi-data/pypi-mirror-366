from __future__ import annotations
import numpy as np
from ImageD11 import frelon_peaksearch


def segment_frame(
    raw_image: np.ndarray, params: dict, scale_factor: float | None = None
) -> tuple[np.ndarray, np.ndarray]:
    image_worker = frelon_peaksearch.worker(
        bgfile=params["correction_files"]["bg_file"],
        maskfile=params["correction_files"]["mask_file"],
        darkfile=params["correction_files"]["dark_file"],
        flatfile=params["correction_files"]["flat_file"],
        threshold=params["segmenter_config"]["threshold"],
        smoothsigma=params["segmenter_config"]["smooth_sigma"],
        bgc=params["segmenter_config"]["bgc"],
        minpx=params["segmenter_config"]["min_px"],
        m_offset_thresh=params["segmenter_config"]["offset_threshold"],
        m_ratio_thresh=params["segmenter_config"]["ratio_threshold"],
    )
    goodpeaks = image_worker.peaksearch(
        img=raw_image, omega=0, scale_factor=scale_factor
    )
    # 23 and 24 are the columns for fast_column index and slow column index
    peak_positions = goodpeaks[:, 23:25].T
    return image_worker.smoothed, peak_positions
