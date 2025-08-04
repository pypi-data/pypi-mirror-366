import h5py
from silx.io.url import DataUrl

from ewoks3dxrd.tasks.filter_by_index import FilterByIndexer


def test_execution(nexus_3dxrd_file):
    inputs = {
        "intensity_filtered_data_url": f"{nexus_3dxrd_file}::/1.1/intensity_filtered_inner_peaks",
        "rings": (0, 1),
        "ds_tol": 0.01,
        "wavelength": 0.28457,
        "lattice_file": "/data/projects/id03_3dxrd/expt/PROCESSED_DATA/Fe.par",
    }

    task = FilterByIndexer(inputs=inputs)
    task.execute()
    output_url = DataUrl(task.outputs["indexer_filtered_data_url"])

    with h5py.File(output_url.file_path(), "r") as h5file:
        process_group = h5file[output_url.data_path()]
        assert isinstance(process_group, h5py.Group)
        assert isinstance(process_group["peaks/Number_of_pixels"], h5py.Dataset)
