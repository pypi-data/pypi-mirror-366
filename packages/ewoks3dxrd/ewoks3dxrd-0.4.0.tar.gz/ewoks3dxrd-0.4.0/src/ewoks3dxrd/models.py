import sys
from pathlib import Path
from typing import Literal, Optional, Sequence, Tuple, Union

from ewoks import BaseInputModel

if sys.version_info < (3, 9):
    from typing_extensions import Annotated
else:
    from typing import Annotated

from pydantic import AliasChoices, BaseModel, Field, field_validator

DetectorCorrectionFiles = Union[Tuple[str, str], str]

Translations = Tuple[Tuple[int, int, int], ...]


class SampleConfig(BaseModel):
    omega_motor: Literal["diffrz", "omega"]
    master_file: str
    scan_number: int

    @field_validator("master_file")
    @classmethod
    def path_exists(cls, path: Optional[str]):
        if path is None or not Path(path).exists():
            raise ValueError(f"Supplied path {path} does not exist.")
        return path


class SegmenterFolderConfig(SampleConfig):
    detector: Literal["frelon1", "frelon3"]
    analyse_folder: str


class SegmenterConfig(BaseModel):
    threshold: int
    smooth_sigma: float
    bgc: float
    min_px: int
    offset_threshold: int
    ratio_threshold: int


class SegmenterCorrectionFiles(BaseModel):
    bg_file: Optional[str] = None
    mask_file: Optional[str] = None
    dark_file: Optional[str] = None
    flat_file: Optional[str] = None

    @field_validator("bg_file", "mask_file", "dark_file", "flat_file")
    @classmethod
    def path_exists(cls, path: Optional[str]):
        if path is not None and not Path(path).exists():
            raise ValueError(f"Supplied path {path} does not exist.")
        return path


class UnitCellParameters(BaseModel):
    a: float = Field(validation_alias=AliasChoices("cell__a", "_cell_length_a"))
    b: float = Field(validation_alias=AliasChoices("cell__b", "_cell_length_b"))
    c: float = Field(validation_alias=AliasChoices("cell__b", "_cell_length_b"))
    alpha: float = Field(
        validation_alias=AliasChoices("cell_alpha", "_cell_angle_alpha")
    )
    beta: float = Field(validation_alias=AliasChoices("cell_beta", "_cell_angle_beta"))
    gamma: float = Field(
        validation_alias=AliasChoices("cell_gamma", "_cell_angle_gamma")
    )
    space_group: Union[
        Literal["P", "A", "B", "C", "I", "F", "R"], Annotated[int, Field(ge=1, le=230)]
    ] = Field(
        validation_alias=AliasChoices(
            "cell_lattice_[P,A,B,C,I,F,R]", "_space_group_IT_number"
        )
    )

    @property
    def lattice_parameters(self) -> Tuple[float, float, float, float, float, float]:
        return self.a, self.b, self.c, self.alpha, self.beta, self.gamma


class GridIndexParameters(BaseModel):
    """
    The variable name defined here are following the same as used by the grid_index_parallel module from ImageD11 library.
    https://github.com/FABLE-3DXRD/ImageD11/blob/master/ImageD11/grid_index_parallel.py
    """

    NPKS: int
    DSTOL: float = 0.004
    RING1: Sequence[int] = (1, 0)
    RING2: Sequence[int] = (0,)
    NUL: bool = True
    FITPOS: bool = True
    tolangle: float = 0.50
    toldist: float = 100.0
    # by providing None, here, ImageD11 will use all the available cores from the server/system
    NPROC: Optional[int] = None
    NTHREAD: int = 1
    COSTOL: Optional[float] = None
    OMEGAFLOAT: Optional[float] = None
    TOLSEQ: Tuple[float, ...] = (0.02, 0.015, 0.01)
    SYMMETRY: str = "cubic"


class InputsWithOverwrite(BaseInputModel):
    overwrite: bool = Field(
        default=False, description="Overwrite NXprocess group if it already exists"
    )
