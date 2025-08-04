from __future__ import annotations
from enum import Enum
from typing import Dict, Optional, Tuple, TypedDict, Union


class OmegaMotor(str, Enum):
    diffrz = "diffrz"
    omega = "omega"


class Detector(str, Enum):
    frelon1 = "frelon1"
    frelon3 = "frelon3"
    eiger = "eiger"


class CorrectionFiles(TypedDict):
    bg_file: Optional[str]
    mask_file: Optional[str]
    dark_file: Optional[str]
    flat_file: Optional[str]


SEGMENTER_DEFAULTS: Dict[str, Union[float, int]] = {
    "threshold": 70,
    "smooth_sigma": 1.0,
    "bgc": 0.9,
    "min_px": 3,
    "offset_threshold": 100,
    "ratio_threshold": 150,
}

DEFAULTS_CORRECTION_MAP: Dict[str, CorrectionFiles] = {
    "diffrz": {
        "bg_file": None,
        "mask_file": "/data/projects/id03_3dxrd/expt/PROCESSED_DATA/mask.edf",
        "dark_file": None,
        "flat_file": None,
    },
    "omega": {
        "bg_file": "/data/projects/id03_3dxrd/id03_expt/PROCESSED_DATA/bkg_avg.edf",
        "mask_file": "/data/projects/id03_3dxrd/id03_expt/PROCESSED_DATA/frelon1_mask_20250122.edf",
        "dark_file": None,
        "flat_file": None,
    },
}

MONITOR_KEYS: Tuple[str, str] = ("pico", "fpico")

SEGMENTER_TOOLTIPS: Dict[str, str] = {
    "bg_file": """
        *Optional: File containing detector background image.
        """,
    "mask_file": """
        *Optional: File describing the detector mask.
        """,
    "flat_file": """
        *Optional: File containing detector sensitivity image.
        """,
    "dark_file": """
        *Optional: File containing detector offset image.
        """,
    "threshold": """
        Minimum pixel intensity (in ADU) to be considered a potential peak.
        \tUsed to eliminate low-signal noise.
        \tTypical range: 50-?
        """,
    "smooth_sigma": """
        Gaussian blur sigma value used for background smoothing.
        \tHigher values result in more smoothing.
        \tTypical range: 0.5-2.0
        """,
    "bgc": """
        Fractional background intensity value (in ADU).
        \tFractional part of background per peak to remove.
        \tTypical range: 0.7-1.0
        """,
    "min_px": """
        Minimum number of connected pixels required to consider a region as a peak.
        \tTypical range: 1-?
        """,
    "offset_threshold": """
        Set intensity to a constant if it is less than this value.
        \tTypical range: 100-?
        \tShould satisfy: offset_threshold < ratio_threshold.
        """,
    "ratio_threshold": """
        Used to filter out peaks with an intensity higher than this value.
        \tTypical range: 150-?
        \tShould satisfy: offset_threshold < ratio_threshold.
        """,
}
