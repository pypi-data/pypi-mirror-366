import h5py
import pytest
from silx.io.url import DataUrl

from ewoks3dxrd.tasks.filter_by_intensity import FilterByIntensity


def test_execution(nexus_3dxrd_file):
    inputs = {
        "lattice_filtered_data_url": f"{nexus_3dxrd_file}::/1.1/phase_filtered_inner_peaks",
        "intensity_frac": 0.8,
    }

    task = FilterByIntensity(inputs=inputs)
    task.execute()
    output_url = DataUrl(task.outputs["intensity_filtered_data_url"])

    with h5py.File(output_url.file_path(), "r") as h5file:
        process_group = h5file[output_url.data_path()]
        assert isinstance(process_group, h5py.Group)
        assert isinstance(process_group["peaks/Number_of_pixels"], h5py.Dataset)


def test_wrong_intensity_frac(nexus_3dxrd_file):
    inputs = {
        "lattice_filtered_data_url": f"{nexus_3dxrd_file}::/1.1/phase_filtered_inner_peaks",
        "intensity_frac": 5,
    }

    task = FilterByIntensity(inputs=inputs)
    with pytest.raises(RuntimeError) as e:
        task.execute()
    original_exc = e.value.__cause__
    assert "Input should be less than or equal to 1" in str(original_exc)
