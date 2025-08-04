import h5py
from silx.io.url import DataUrl

from ewoks3dxrd.tasks.filter_by_lattice import FilterByLattice
from ewoks3dxrd.io import save_geometry_and_lattice_file


def test_execution(nexus_3dxrd_file, tmp_path):
    par_file = tmp_path / "Al.par"
    save_geometry_and_lattice_file(
        tmp_path / "Al.par",
        {},
        {
            "lattice_parameters": [4.050, 4.050, 4.050, 90.0, 90.0, 90.0],
            "lattice_space_group": 225,
        },
    )

    inputs = {
        "geometry_updated_data_url": f"{nexus_3dxrd_file}::/1.1/geometry_updated_peaks",
        "lattice_file": str(par_file),
        "reciprocal_dist_tol": 0.025,
    }

    task = FilterByLattice(inputs=inputs)
    task.execute()
    output_url = DataUrl(task.outputs["lattice_filtered_data_url"])

    with h5py.File(output_url.file_path(), "r") as h5file:
        process_group = h5file[output_url.data_path()]
        assert isinstance(process_group, h5py.Group)
        assert isinstance(process_group["peaks/Number_of_pixels"], h5py.Dataset)
