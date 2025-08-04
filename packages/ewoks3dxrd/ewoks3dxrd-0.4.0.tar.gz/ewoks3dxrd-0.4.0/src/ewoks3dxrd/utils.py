from __future__ import annotations

from pathlib import Path
from typing import Tuple, Optional
import numpy as np
import random
from ImageD11 import blobcorrector
from ImageD11 import columnfile as PeakColumnFile
from ImageD11.columnfile import columnfile as ColumnFile
from ImageD11.refinegrains import refinegrains as RefineGrains

from .models import DetectorCorrectionFiles


def do_spatial_correction(
    peak_3d_dict: dict, correction_files: DetectorCorrectionFiles
) -> ColumnFile:
    peak_3d_dict["spot3d_id"] = np.arange(len(peak_3d_dict["s_raw"]))
    raw_columnfile_3d = PeakColumnFile.colfile_from_dict(peak_3d_dict)

    if isinstance(correction_files, str):
        spline_file = correction_files
        return blobcorrector.correct_cf_with_spline(raw_columnfile_3d, spline_file)

    if isinstance(correction_files, tuple) and len(correction_files) == 2:
        e2dx_file, e2dy_file = correction_files
        return blobcorrector.correct_cf_with_dxdyfiles(
            raw_columnfile_3d, e2dx_file, e2dy_file
        )

    raise ValueError(
        f"Detector Spatial correction cannot be performed unless a spline file or a couple of e2dx, ed2dy files is provided. Got {correction_files}."
    )


def refine_grains(
    tolerance: float,
    intensity_tth_range: Tuple[float, float],
    omega_slop: float,
    symmetry: str,
    parameter_file: str | Path,
    filtered_peaks_file: str | Path,
    ubi_file: str | Path,
) -> RefineGrains:
    refined_grains = RefineGrains(
        tolerance=tolerance,
        intensity_tth_range=intensity_tth_range,
        OmSlop=omega_slop,
    )
    refined_grains.loadparameters(str(parameter_file))
    refined_grains.loadfiltered(str(filtered_peaks_file))
    refined_grains.readubis(str(ubi_file))
    refined_grains.makeuniq(symmetry)
    refined_grains.generate_grains()
    refined_grains.refinepositions()

    return refined_grains


def generate_translations(
    max_x: int, max_y: int, max_z: int, step: int, seed: Optional[int] = None
) -> Tuple[Tuple[int, int, int], ...]:
    translations = [
        (t_x, t_y, t_z)
        for t_x in range(-max_x, max_x + 1, step)
        for t_y in range(-max_y, max_y + 1, step)
        for t_z in range(-max_z, max_z + 1, step)
    ]

    if seed is None:
        return tuple(translations)
    else:
        rnd = random.Random(seed)
        rnd.shuffle(translations)
        return tuple(translations)


def update_geometry(peaks: dict, geometry_file: Path) -> Tuple[dict, dict]:
    cf = PeakColumnFile.colfile_from_dict(peaks)
    # The following code derives from `update_colfile_pars`:
    # https://github.com/FABLE-3DXRD/ImageD11/blob/a27e67ffbd8471a7eb036ce7661d006027739cb6/ImageD11/sinograms/dataset.py#L870
    cf.parameters.loadparameters(filename=str(geometry_file))
    # updateGeometry() adds various geometry parameters from the geometry .par file into the column file
    cf.updateGeometry()

    return {
        key: cf[key] for key in ("ds", "eta", "gx", "gy", "gz", "tth", "xl", "yl", "zl")
    }, cf.parameters.parameters
