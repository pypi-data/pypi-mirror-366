import h5py
from silx.io.url import DataUrl

from ewoks3dxrd.tasks.geometry_transformation import GeometryTransformation


GEOMETRY = {
    "chi": 0,
    "distance": 277938.9537523063,
    "fit_tolerance": 0.05,
    "min_bin_prob": 1e-05,
    "no_bins": 10000,
    "o11": 1,
    "o12": 0,
    "o21": 0,
    "o22": -1,
    "omegasign": 1.0,
    "t_x": 0.0,
    "t_y": 0.0,
    "t_z": 0.0,
    "tilt_x": -0.003145870872293617,
    "tilt_y": -0.0019304888034885003,
    "tilt_z": 0.00924114210818807,
    "wavelength": 0.22477970523350738,
    "wedge": 0.10331991684510052,
    "weight_hist_intensities": 0,
    "y_center": 1009.4810919042234,
    "y_size": 47.3,
    "z_center": 1009.4248984777241,
    "z_size": 47.3,
}


def test_execution(nexus_3dxrd_file, tmp_path):
    geom_file = tmp_path / "geometry_closer.par"

    with open(geom_file, "w") as f:
        for key, value in GEOMETRY.items():
            f.write(f"{key} {value}\n")

    inputs = {
        "spatial_corrected_data_url": f"{nexus_3dxrd_file}::/1.1/geometry_updated_peaks",
        "geometry_par_file": "/data/projects/id03_3dxrd/id03_expt/PROCESSED_DATA/geometry_closer.par",
        "overwrite": True,
    }

    task = GeometryTransformation(inputs=inputs)
    task.execute()
    output_url = DataUrl(task.outputs["geometry_updated_data_url"])

    with h5py.File(output_url.file_path(), "r") as h5file:
        process_group = h5file[output_url.data_path()]
        assert isinstance(process_group, h5py.Group)
        assert isinstance(process_group["peaks/ds"], h5py.Dataset)
        for name, dset in process_group["parameters"].items():
            assert dset[()] == GEOMETRY[name]
