from ewoks3dxrd.tasks.grid_index_grains import GridIndexGrains

from ..nexus.utils import get_data_url_paths, group_exists


def test_grid_index_grains(tmp_path, nexus_3dxrd_file, id03_inp_config):
    inputs = {
        "indexer_filtered_data_url": f"{nexus_3dxrd_file}::/1.1/intensity_filtered_inner_peaks",
        "grid_index_parameters": {"NPKS": 3},
        "analyse_folder": tmp_path,
        "overwrite": True,
        "grid_step": 20,
        "grid_abs_x_limit": 10,
        "grid_abs_y_limit": 0,
        "grid_abs_z_limit": 0,
        "sample_config": id03_inp_config,
    }

    task = GridIndexGrains(inputs=inputs)
    task.execute()
    nexus_file, nexus_group = get_data_url_paths(
        task.outputs["grid_indexed_grain_data_url"]
    )
    assert group_exists(filename=nexus_file, data_group_path=nexus_group)
