import os
import sys

if sys.version_info >= (3, 9):
    from importlib.resources import files as resource_files
else:
    from importlib_resources import files as resource_files

from pathlib import Path

from ewokscore import execute_graph
from silx.io.utils import DataUrl

from orangecontrib.ewoks3dxrd import tutorials

from ..nexus.grains import read_grains_attributes
from ..nexus.peaks import read_peaks_attributes
from ..nexus.utils import get_data_url_paths, group_exists


def test_segmentation_3dpeaks_id03_workflow(id03_inp_config):
    assert os.environ["OMP_NUM_THREADS"] == "1"
    segmenter_config = {
        "threshold": 70,
        "smooth_sigma": 1.0,
        "bgc": 0.9,
        "min_px": 3,
        "offset_threshold": 100,
        "ratio_threshold": 150,
    }

    file_cor_config = {
        "bg_file": id03_inp_config.get("bg_file"),
        "mask_file": id03_inp_config.get("mask_file"),
        "flat_file": None,
        "dark_file": None,
    }
    sample_folder_config = {
        "detector": id03_inp_config.get("detector"),
        "omega_motor": id03_inp_config.get("omega_motor"),
        "master_file": id03_inp_config["master_file"],
        "scan_number": id03_inp_config["scan_number"],
        "analyse_folder": id03_inp_config.get("analyse_folder"),
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
            "value": id03_inp_config["spline_file"],
            "id": "DetCor",
        },
        {
            "name": "geometry_par_file",
            "value": "/data/projects/id03_3dxrd/id03_expt/PROCESSED_DATA/geometry_closer.par",
            "id": "GeoUp",
        },
        {
            "name": "lattice_file",
            "value": "/data/projects/id03_3dxrd/id03_expt/PROCESSED_DATA/Al.par",
            "id": "LatFilt",
        },
        {
            "name": "reciprocal_dist_max",
            "value": 0.737,
            "id": "LatFilt",
        },
        {
            "name": "reciprocal_dist_tol",
            "value": 0.025,
            "id": "LatFilt",
        },
        {
            "name": "process_group_name",
            "value": "inner_rings",
            "id": "LatFilt",
        },
        {
            "name": "intensity_frac",
            "value": 0.999,
            "id": "IntFilt",
        },
        {
            "name": "process_group_name",
            "value": "intensity_inner_rings",
            "id": "IntFilt",
        },
        {
            "name": "lattice_file",
            "value": "/data/projects/id03_3dxrd/id03_expt/PROCESSED_DATA/Al.par",
            "id": "AllLatFilt",
        },
        {
            "name": "reciprocal_dist_tol",
            "value": 0.025,
            "id": "AllLatFilt",
        },
        {
            "name": "process_group_name",
            "value": "all_rings",
            "id": "AllLatFilt",
        },
        {
            "name": "intensity_frac",
            "value": 0.999,
            "id": "AllIntFilt",
        },
        {
            "name": "process_group_name",
            "value": "intensity_all_rings",
            "id": "AllIntFilt",
        },
        {
            "name": "rings",
            "value": (0, 1, 2),
            "id": "IndexerFilt",
        },
        {
            "name": "process_group_name",
            "value": "inner_rings_indexer_filter",
            "id": "IndexerFilt",
        },
        {"name": "grid_index_parameters", "value": {"NPKS": 44}, "id": "GridIndex"},
        {
            "name": "minpks",
            "value": 0,
            "id": "GrainMap",
        },
        {
            "name": "hkl_tols",
            "value": (0.01,),
            "id": "GrainMap",
        },
    ]
    workflow_file = resource_files(tutorials).joinpath("id03_3dxrd_workflow.json")

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
    assert len(peak_x_position) == 30281

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
    intensity_filtered_peaks = read_peaks_attributes(
        filename=nexus_file_path, process_group=intensity_filtered_data_group
    )
    peak_x_position = intensity_filtered_peaks["f_raw"]
    assert len(peak_x_position) == 18794

    lattice_filtered_data_path = outputs["AllLatFilt"]["lattice_filtered_data_url"]
    data_url = DataUrl(lattice_filtered_data_path)
    lattice_filtered_data_group = data_url.data_path()
    assert group_exists(nexus_file_path, lattice_filtered_data_group)
    lattice_file = outputs["LatFilt"]["copied_lattice_file"]
    assert Path(lattice_file).exists()
    intensity_filtered_data_path = outputs["AllIntFilt"]["intensity_filtered_data_url"]
    data_url = DataUrl(intensity_filtered_data_path)
    intensity_filtered_data_group = data_url.data_path()
    assert group_exists(nexus_file_path, intensity_filtered_data_group)
    intensity_filtered_peaks = read_peaks_attributes(
        filename=nexus_file_path, process_group=intensity_filtered_data_group
    )
    peak_x_position = intensity_filtered_peaks["f_raw"]
    assert len(peak_x_position) == 27304

    indexer_filtered_data_path = outputs["IndexerFilt"]["indexer_filtered_data_url"]
    data_url = DataUrl(indexer_filtered_data_path)
    inner_rings_indexer_filter_data_group = data_url.data_path()
    assert group_exists(nexus_file_path, inner_rings_indexer_filter_data_group)
    index_filtered_peaks = read_peaks_attributes(
        filename=nexus_file_path, process_group=inner_rings_indexer_filter_data_group
    )
    peak_x_position = index_filtered_peaks["f_raw"]
    assert len(peak_x_position) == 18794

    grid_index_data_path = outputs["GridIndex"]["grid_indexed_grain_data_url"]
    data_url = DataUrl(grid_index_data_path)
    grid_index_grains = data_url.data_path()
    assert group_exists(nexus_file_path, grid_index_grains)

    nexus_file_path, ubi_data_group_path = get_data_url_paths(
        outputs["GrainMap"]["make_map_data_url"]
    )
    assert Path(nexus_file_path).exists()
    dict_grains = read_grains_attributes(
        filename=nexus_file_path, process_group=ubi_data_group_path
    )
    assert dict_grains["UBI"].shape == (45, 3, 3)
