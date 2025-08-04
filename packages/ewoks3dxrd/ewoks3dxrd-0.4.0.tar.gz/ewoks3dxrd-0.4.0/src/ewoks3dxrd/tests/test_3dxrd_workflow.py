import os
import sys

if sys.version_info >= (3, 9):
    from importlib.resources import files as resource_files
else:
    from importlib_resources import files as resource_files

from pathlib import Path

import numpy as np
from ewokscore import execute_graph
from silx.io.utils import DataUrl

from orangecontrib.ewoks3dxrd import tutorials

from ..nexus.peaks import read_peaks_attributes
from ..nexus.utils import group_exists
from .conftest import assert_grain_map_results, assert_indexing_results


def test_segmentation_3dpeaks_workflow(inp_config):
    assert os.environ["OMP_NUM_THREADS"] == "1"
    # if you change this config setting or default inp_config,
    # assertion statement assert len(found_peaks[0]) == 76 and
    # and len(peaks_position[0]) == 31682 and
    # assert cf.nrows == 7662 will fail

    # if you change this config setting,
    # assertion statement assert len(found_peaks[0]) == 76 will fail
    segmenter_config = {
        "threshold": 70,
        "smooth_sigma": 1.0,
        "bgc": 0.9,
        "min_px": 3,
        "offset_threshold": 100,
        "ratio_threshold": 150,
    }

    file_cor_config = {
        "bg_file": inp_config.get("bg_file"),
        "mask_file": inp_config.get("mask_file"),
        "flat_file": None,
        "dark_file": None,
    }

    sample_folder_config = {
        "detector": "frelon3",
        "omega_motor": "diffrz",
        "master_file": inp_config["master_file"],
        "scan_number": inp_config["scan_number"],
        "analyse_folder": inp_config.get("analyse_folder"),
    }

    inputs = [
        {
            "name": "folder_config",
            "value": sample_folder_config,
            "id": "segScan",
        },
        {
            "name": "segmenter_algo_params",
            "value": segmenter_config,
            "id": "segScan",
        },
        {
            "name": "correction_files",
            "value": file_cor_config,
            "id": "segScan",
        },
        {
            "name": "correction_files",
            "value": inp_config["spline_file"],
            "id": "DetCor",
        },
        {
            "name": "geometry_par_file",
            "value": "/data/projects/id03_3dxrd/expt/PROCESSED_DATA/geometry_tdxrd.par",
            "id": "GeoUp",
        },
        {
            "name": "lattice_file",
            "value": "/data/projects/id03_3dxrd/expt/PROCESSED_DATA/Fe.par",
            "id": "LatFilt",
        },
        {
            "name": "reciprocal_dist_max",
            "value": 1.01,
            "id": "LatFilt",
        },
        {
            "name": "reciprocal_dist_tol",
            "value": 0.01,
            "id": "LatFilt",
        },
        {
            "name": "process_group_name",
            "value": "inner_rings",
            "id": "LatFilt",
        },
        {
            "name": "lattice_file",
            "value": "/data/projects/id03_3dxrd/expt/PROCESSED_DATA/Fe.par",
            "id": "AllLatFilt",
        },
        {
            "name": "reciprocal_dist_tol",
            "value": 0.01,
            "id": "AllLatFilt",
        },
        {
            "name": "process_group_name",
            "value": "all_rings",
            "id": "AllLatFilt",
        },
        {
            "name": "intensity_frac",
            "value": 0.9837,
            "id": "IntFilt",
        },
        {
            "name": "process_group_name",
            "value": "intensity_inner_rings",
            "id": "IntFilt",
        },
        {
            "name": "intensity_frac",
            "value": 0.9837,
            "id": "AllIntFilt",
        },
        {
            "name": "process_group_name",
            "value": "intensity_all_rings",
            "id": "AllIntFilt",
        },
        {
            "name": "reciprocal_dist_tol",
            "value": 0.05,
            "id": "Indexer",
        },
        {
            "name": "rings",
            "value": (0, 1),
            "id": "Indexer",
        },
        {
            "name": "scoring_rings",
            "value": (0, 1, 2, 3),
            "id": "Indexer",
        },
        {
            "name": "hkl_tols",
            "value": (0.01, 0.02, 0.03, 0.04),
            "id": "Indexer",
        },
        {
            "name": "min_pks_frac",
            "value": (0.9, 0.75),
            "id": "Indexer",
        },
        {
            "name": "cosine_tol",
            "value": np.cos(np.radians(90 - 0.25)),
            "id": "Indexer",
        },
        {
            "name": "max_grains",
            "value": 1000,
            "id": "Indexer",
        },
        {
            "name": "hkl_tols",
            "value": (0.05, 0.025, 0.01),
            "id": "GrainMap",
        },
        {
            "name": "minpks",
            "value": 120,
            "id": "GrainMap",
        },
    ]
    workflow_file = resource_files(tutorials).joinpath("3dxrd_workflow.json")

    outputs = execute_graph(
        str(workflow_file), inputs=inputs, outputs=[{"all": True}], merge_outputs=False
    )
    assert outputs is not None
    detector_spatial_data_path = outputs["DetCor"]["spatial_corrected_data_url"]
    data_url = DataUrl(detector_spatial_data_path)
    nexus_file_path = data_url.file_path()
    detector_spatial_corrected_group = data_url.data_path()
    assert group_exists(nexus_file_path, detector_spatial_corrected_group)
    detector_spatial_peaks = read_peaks_attributes(
        filename=nexus_file_path, process_group=detector_spatial_corrected_group
    )
    peak_x_position = detector_spatial_peaks["f_raw"]
    assert len(peak_x_position) == 31682

    lattice_filtered_data_path = outputs["LatFilt"]["lattice_filtered_data_url"]
    data_url = DataUrl(lattice_filtered_data_path)
    lattice_filtered_data_group = data_url.data_path()
    assert group_exists(nexus_file_path, lattice_filtered_data_group)
    lattice_file = outputs["LatFilt"]["copied_lattice_file"]
    assert Path(lattice_file).exists()

    intensity_filtered_data_path = outputs["IntFilt"]["intensity_filtered_data_url"]
    data_url = DataUrl(intensity_filtered_data_path)
    intensity_filtered_data_group = data_url.data_path()
    assert group_exists(nexus_file_path, intensity_filtered_data_group)
    intensity_peaks = read_peaks_attributes(
        filename=nexus_file_path, process_group=intensity_filtered_data_group
    )
    peaks_n_rows = intensity_peaks["f_raw"]
    assert len(peaks_n_rows) == 7662

    assert_indexing_results(outputs["Indexer"])

    assert_grain_map_results(outputs["GrainMap"])
