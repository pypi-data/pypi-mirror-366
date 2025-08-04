import os
import shutil
from pathlib import Path

import pytest
from ewoksorange.canvas.handler import OrangeCanvasHandler
from ewoksorange.tests.conftest import qtapp  # noqa F401

from ..nexus.grains import read_grains_attributes
from ..nexus.utils import get_data_url_paths


@pytest.fixture(scope="session")
def ewoks_orange_canvas(qtapp):  # noqa F811
    with OrangeCanvasHandler() as handler:
        yield handler


@pytest.fixture
def inp_config(tmp_path):
    master_file = "/data/projects/id03_3dxrd/expt/RAW_DATA/FeAu_0p5_tR/FeAu_0p5_tR_ff1/FeAu_0p5_tR_ff1.h5"

    if not os.path.exists(master_file):
        raise FileNotFoundError(
            f"""
            Could not find {master_file}.
            Before running this test, be sure to have a link to /data/projects at /data/:
             - mkdir -p /data/projects/id03_3dxrd
             - ln -s /gpfs/.../data/projects /data
            Sudo rights might be needed.
            """
        )

    return {
        "detector": "frelon3",
        "omega_motor": "diffrz",
        "dty_motor": "diffty",
        "bg_file": None,
        "mask_file": "/data/projects/id03_3dxrd/expt/PROCESSED_DATA/mask.edf",
        "spline_file": "/data/projects/id03_3dxrd/expt/PROCESSED_DATA/frelon36.spline",
        "e2dx_file": None,
        "e2dy_file": None,
        "master_file": master_file,
        "scan_number": 1,
        "analyse_folder": os.path.join(tmp_path, "test_my_task"),
        "stateful_imageD11_file": None,
    }


@pytest.fixture
def id03_inp_config(tmp_path):
    master_file = "/data/projects/id03_3dxrd/id03_expt/RAW_DATA/Al_1050/Al_1050_rot_4/Al_1050_rot_4.h5"

    if not os.path.exists(master_file):
        raise FileNotFoundError(
            f"""
            Could not find {master_file}.
            Before running this test, be sure to have a link to /data/projects at /data/:
             - mkdir -p /data/projects/id03_3dxrd
             - ln -s /gpfs/.../data/projects /data
            Sudo rights might be needed.
            """
        )

    return {
        "detector": "frelon1",
        "omega_motor": "omega",
        "dty_motor": "diffty",
        "bg_file": "/data/projects/id03_3dxrd/id03_expt/PROCESSED_DATA/bkg_avg.edf",
        "mask_file": "/data/projects/id03_3dxrd/id03_expt/PROCESSED_DATA/frelon1_mask_20250122.edf",
        "spline_file": "/data/projects/id03_3dxrd/id03_expt/PROCESSED_DATA/distortion_frelon.spline",
        "e2dx_file": None,
        "e2dy_file": None,
        "master_file": master_file,
        "scan_number": 1,
        "analyse_folder": os.path.join(tmp_path, "test_my_task"),
        "stateful_imageD11_file": None,
    }


@pytest.fixture()
def nexus_3dxrd_file(tmp_path):
    new_filename = tmp_path / "nexus_segment.h5"
    shutil.copy2(
        "/data/projects/id03_3dxrd/ewoks_test_data/nexus_segment.h5",
        new_filename,
    )

    return new_filename


def assert_indexing_results(indexing_task_outputs):
    nexus_file_path, ubi_data_group_path = get_data_url_paths(
        indexing_task_outputs["indexed_grain_data_url"]
    )

    assert Path(nexus_file_path).exists()
    dict_grains = read_grains_attributes(
        filename=nexus_file_path, process_group=ubi_data_group_path
    )
    assert dict_grains["UBI"].shape == (59, 3, 3)


def assert_grain_map_results(grain_map_task_outputs):
    nexus_file_path, ubi_data_group_path = get_data_url_paths(
        grain_map_task_outputs["make_map_data_url"]
    )
    assert Path(nexus_file_path).exists()
    dict_grains = read_grains_attributes(
        filename=nexus_file_path, process_group=ubi_data_group_path
    )
    assert dict_grains["UBI"].shape == (52, 3, 3)
