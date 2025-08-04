from __future__ import annotations
from typing import Sequence, Tuple
from ImageD11 import columnfile as PeakColumnFile
from ImageD11.unitcell import unitcell as UnitCell
from pathlib import Path
from .models import UnitCellParameters
from ImageD11.peakselect import (
    sorted_peak_intensity_mask_and_cumsum,
    filter_peaks_by_phase,
)
from .io import read_lattice_cell_data
import numpy as np
from ImageD11.indexing import indexer_from_colfile_and_ucell


def filter_by_intensity(peaks: dict, intensity_frac: float) -> dict:
    cf = PeakColumnFile.colfile_from_dict(peaks)
    mask, _ = sorted_peak_intensity_mask_and_cumsum(colf=cf, frac=intensity_frac)
    cf.filter(mask)

    return {key: cf[key] for key in cf.keys()}


def filter_by_phase(
    peaks: dict,
    lattice_file: Path,
    ds_tol: float,
    ds_max: float | None = None,
) -> Tuple[dict, UnitCellParameters]:
    raw_cf = PeakColumnFile.colfile_from_dict(peaks)

    unit_cell_parameters = read_lattice_cell_data(lattice_file)
    unit_cell = UnitCell(
        lattice_parameters=unit_cell_parameters.lattice_parameters,
        symmetry=unit_cell_parameters.space_group,
    )
    unit_cell.makerings(limit=raw_cf.ds.max())

    if ds_max is None:
        ds_max = raw_cf.ds.max()
    cf = raw_cf.copyrows(raw_cf.ds <= ds_max)
    filtered_cf = filter_peaks_by_phase(
        cf=cf,
        dstol=ds_tol,
        dsmax=ds_max,
        cell=unit_cell,
    )

    return {key: filtered_cf[key] for key in filtered_cf.keys()}, unit_cell_parameters


def filter_with_indexer(
    peak_3d_dict: dict,
    unit_cell: UnitCell,
    wavelength: float,
    phase_ds_tolerance: float,
    rings: Sequence[int],
) -> dict:
    """Using indexer and sequence of Ring indices, filter the given 3d peaks"""
    peaks_cf = PeakColumnFile.colfile_from_dict(peak_3d_dict)
    indexer = indexer_from_colfile_and_ucell(
        colfile=peaks_cf,
        ucell=unit_cell,
        wavelength=wavelength,
        ds_tol=phase_ds_tolerance,
    )
    indexer.assigntorings()

    mask = np.zeros(peaks_cf.nrows, dtype=bool)
    for ring in rings:
        mask |= indexer.ra == ring
    peaks_cf.filter(mask)

    return {key: peaks_cf[key] for key in peaks_cf.keys()}
