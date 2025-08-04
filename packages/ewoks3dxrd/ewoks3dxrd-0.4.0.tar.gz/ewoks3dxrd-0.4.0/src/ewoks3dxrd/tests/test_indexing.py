from ewoks3dxrd.tasks.index_grains import IndexGrains

from .conftest import assert_indexing_results


def test_indexing(nexus_3dxrd_file):
    filepath = f"{nexus_3dxrd_file}::/1.1/intensity_filtered_inner_peaks"

    inputs = {
        "intensity_filtered_data_url": filepath,
        "reciprocal_dist_tol": 0.05,
        "rings": (0, 1),
        "scoring_rings": (0, 1, 2, 3),
        "hkl_tols": (0.01, 0.02, 0.03, 0.04),
        "min_pks_frac": (0.9, 0.75),
        "overwrite": True,
        "wavelength": 0.28457,
        "lattice_file": "/data/projects/id03_3dxrd/expt/PROCESSED_DATA/Fe.par",
    }

    task = IndexGrains(inputs=inputs)
    task.execute()

    assert_indexing_results(task.outputs)
