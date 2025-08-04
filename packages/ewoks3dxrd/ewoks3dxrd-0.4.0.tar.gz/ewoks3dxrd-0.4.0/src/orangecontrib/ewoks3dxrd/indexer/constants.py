from __future__ import annotations

from enum import Enum


class Symmetry(str, Enum):
    cubic = "cubic"
    hexagonal = "hexagonal"
    trigonal = "trigonal"
    rhombohedralP = "rhombohedralP"
    trigonalP = "trigonalP"
    tetragonal = "tetragonal"
    orthorhombic = "orthorhombic"
    monoclinic_c = "monoclinic_c"
    monoclinic_a = "monoclinic_a"
    monoclinic_b = "monoclinic_b"
    triclinic = "triclinic"
