import pytest

from ewoks3dxrd.io import read_lattice_cell_data
from ewoks3dxrd.io import get_monitor_scale_factor


@pytest.mark.parametrize("space_group", (229, "I"))
def test_read_lattice_cell_data(tmp_path, space_group):
    par_file = tmp_path / "Fe.par"
    with open(par_file, "w") as f:
        f.write(
            f"""cell__a 2.8694
cell__b 2.8694
cell__c 2.8694
cell_alpha 90.0
cell_beta 90.0
cell_gamma 90.0
cell_lattice_[P,A,B,C,I,F,R] {space_group}
"""
        )

    unit_cell_parameters = read_lattice_cell_data(par_file)

    assert unit_cell_parameters.a == 2.8694
    assert unit_cell_parameters.b == 2.8694
    assert unit_cell_parameters.c == 2.8694
    assert unit_cell_parameters.alpha == 90
    assert unit_cell_parameters.beta == 90
    assert unit_cell_parameters.gamma == 90
    assert unit_cell_parameters.space_group == space_group


def test_get_monitor_scale_factor_id03():
    scale_factor = get_monitor_scale_factor(
        masterfile_path="/data/projects/id03_3dxrd/id03_expt/RAW_DATA/Al_1050/Al_1050_rot_4/Al_1050_rot_4.h5",
        scan_number=1,
        monitor_name="pico4",
    )
    assert scale_factor.shape == (1800,)

    with pytest.raises(KeyError):
        scale_factor = get_monitor_scale_factor(
            masterfile_path="/data/projects/id03_3dxrd/id03_expt/RAW_DATA/Al_1050/Al_1050_rot_4/Al_1050_rot_4.h5",
            scan_number=1,
            monitor_name="not_existing",
        )


def test_get_monitor_scale_factor_id11():
    scale_factor = get_monitor_scale_factor(
        masterfile_path="/data/projects/id03_3dxrd/expt/RAW_DATA/FeAu_0p5_tR/FeAu_0p5_tR_ff1/FeAu_0p5_tR_ff1.h5",
        scan_number=1,
        monitor_name="fpico4",
    )
    assert scale_factor.shape == (1440,)
