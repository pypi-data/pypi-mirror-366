from __future__ import annotations

from typing import Any, Optional, Sequence

from ewokscore import Task
from ImageD11 import columnfile as PeakColumnFile
from ImageD11 import indexing
from ImageD11.unitcell import unitcell as UnitCell
from pydantic import Field

from ..io import read_lattice_cell_data
from ..models import InputsWithOverwrite
from ..nexus.grains import save_nexus_grain_process
from ..nexus.peaks import read_peaks_attributes
from ..nexus.utils import (
    check_throw_write_data_group_url,
    get_data_url_paths,
    get_entry_name,
)


class Inputs(InputsWithOverwrite):
    intensity_filtered_data_url: str = Field(
        description="Path to NXprocess group containing the intensity filtered peaks"
    )
    rings: Sequence[int] = Field(
        description="Indices of rings used for generating UBI. Two are usually enough, three in some rare cases.",
        examples=[(0, 1)],
    )
    scoring_rings: Sequence[int] = Field(
        description="Indices of the rings used for scoring. These must contain the indices used for indexing.",
        examples=[(0, 1, 2)],
    )
    max_grains: Optional[int] = Field(
        default=None, description="Limits the number of found grains."
    )
    reciprocal_dist_tol: Optional[float] = Field(
        default=None, description="Reciprocal distance tolerance value."
    )
    hkl_tols: Optional[Sequence[float]] = Field(
        default=None,
        description="Miller indices tolerances.",
        examples=[(0.01, 0.02, 0.03, 0.04)],
    )
    min_pks_frac: Optional[Sequence[float]] = Field(
        default=None, description="Minimal peaks fraction to iterate over."
    )
    cosine_tol: Optional[float] = Field(
        default=None,
        description="tolerance value used in the Indexer convergence scheme for finding pairs of peaks to make an orientation",
    )
    lattice_file: str = Field(
        description="Path to the file (`.par` or `.cif`) containing lattice parameters and space group information forwarded by lattice filter task"
    )
    wavelength: float = Field(
        description="wavelength used in the geometry transformation task",
    )

    def imageD11_indexing_parameters(self) -> dict[str, Any]:
        indexing_params: dict[str, Any] = {
            "wavelength": self.wavelength,
        }

        if self.max_grains:
            indexing_params["max_grains"] = self.max_grains
        if self.reciprocal_dist_tol:
            indexing_params["dstol"] = self.reciprocal_dist_tol
        if self.hkl_tols:
            indexing_params["hkl_tols"] = self.hkl_tols
        if self.min_pks_frac:
            indexing_params["fracs"] = self.min_pks_frac
        if self.cosine_tol:
            indexing_params["cosine_tol"] = self.cosine_tol

        return indexing_params


class IndexGrains(Task, input_model=Inputs, output_names=["indexed_grain_data_url"]):
    """
    From 3D peaks, finds grains' UBI  matrices and stores them in both ASCII format and NeXus (.h5) format.

    Outputs:

    - `indexed_grain_data_url` (str): Data path to 'NxProcess group data' Grains that stores generated UBI
    """

    def run(self):
        inputs = Inputs(**self.get_input_values())
        nexus_file_path, intensity_filtered_data_group_path = get_data_url_paths(
            inputs.intensity_filtered_data_url
        )

        if len(inputs.rings) < 2:
            raise ValueError(
                f"Indexing needs at least two ring indices in `rings`. Got {inputs.rings}"
            )

        entry_name = get_entry_name(intensity_filtered_data_group_path)
        indexed_ubi_data_group = f"{entry_name}/indexed_grains"
        check_throw_write_data_group_url(
            overwrite=inputs.overwrite,
            filename=nexus_file_path,
            data_group_path=indexed_ubi_data_group,
        )

        intensity_filtered_peaks = read_peaks_attributes(
            filename=nexus_file_path, process_group=intensity_filtered_data_group_path
        )
        cf = PeakColumnFile.colfile_from_dict(intensity_filtered_peaks)

        lattice_parameter = read_lattice_cell_data(inputs.lattice_file)
        unit_cell = UnitCell(
            lattice_parameters=lattice_parameter.lattice_parameters,
            symmetry=str(lattice_parameter.space_group),
        )

        unit_cell.makerings(limit=cf.ds.max())

        indexing_params = inputs.imageD11_indexing_parameters()

        grains, _ = indexing.do_index(
            cf=cf,
            forgen=inputs.rings,
            foridx=inputs.scoring_rings,
            unitcell=unit_cell,
            **indexing_params,
        )

        ubi_grains_group_name = save_nexus_grain_process(
            filename=nexus_file_path,
            entry_name=entry_name,
            process_name="indexed_grains",
            config_settings={
                **indexing_params,
                "data_from": inputs.intensity_filtered_data_url,
                "lattice_parameters": lattice_parameter.lattice_parameters,
                "lattice_space_group": lattice_parameter.space_group,
                "idx_for_gen": inputs.rings,
                "idx_for_score": inputs.scoring_rings,
            },
            grains=grains,
            overwrite=inputs.overwrite,
        )
        self.outputs.indexed_grain_data_url = ubi_grains_group_name
