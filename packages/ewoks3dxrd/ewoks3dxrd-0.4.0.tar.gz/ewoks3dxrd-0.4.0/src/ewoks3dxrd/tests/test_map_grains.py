from ewoks3dxrd.tasks.make_grain_map import MakeGrainMap

from .conftest import assert_grain_map_results


def test_map_grains(tmp_path, nexus_3dxrd_file):
    inputs = {
        "hkl_tols": (0.05, 0.025, 0.01),
        "minpks": 120,
        "folder_file_config": {
            "omega_motor": "diffrz",
            "master_file": "/data/projects/id03_3dxrd/expt/RAW_DATA/FeAu_0p5_tR/FeAu_0p5_tR_ff1/FeAu_0p5_tR_ff1.h5",
            "scan_number": 1,
        },
        "intensity_fine_filtered_data_url": f"{nexus_3dxrd_file}::/1.1/intensity_filtered_inner_peaks",
        "indexed_grain_data_url": f"{nexus_3dxrd_file}::/1.1/indexed_ubi",
        "intensity_filtered_data_url": f"{nexus_3dxrd_file}::/1.1/intensity_filtered_all_peaks",
        "analyse_folder": tmp_path,
        "overwrite": True,
        "lattice_file": "/data/projects/id03_3dxrd/expt/PROCESSED_DATA/Fe.par",
    }

    task = MakeGrainMap(inputs=inputs)
    task.execute()

    assert_grain_map_results(task.outputs)
