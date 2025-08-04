from __future__ import annotations

from typing import Tuple

from silx.gui import qt

from ..common.double_spinbox_range_widget import DoubleSpinBoxRangeWidget
from ..common.tolerance_selector import ToleranceSelector
from ..indexer.constants import Symmetry


class GrainMapParameterGroupBox(qt.QGroupBox):
    def __init__(self, parent: qt.QWidget | None = None, **kwargs) -> None:
        super().__init__("Refinement Settings", parent=parent, **kwargs)
        layout = qt.QFormLayout(self)

        self._minpks = qt.QSpinBox()
        self._minpks.setRange(0, 10000)
        self._minpks.setValue(1)
        self._minpks.setToolTip(
            "Minimal number of peaks for the grain to be kept after iterative refinement."
        )

        self._intensityTwoThetaRange = DoubleSpinBoxRangeWidget(default=(0.0, 180.0))
        self._intensityTwoThetaRange.setToolTip(
            "Range of two theta to use when refining. Only peaks in this range will be selected"
        )

        self._symmetry = qt.QComboBox()
        self._symmetry.addItems([e.value for e in Symmetry])
        self._symmetry.setToolTip("Lattice symmetry used to further refine grains")
        self._toleranceSelector = ToleranceSelector()

        layout.addRow("Min Peaks for each grain", self._minpks)
        layout.addRow("2θ range", self._intensityTwoThetaRange)
        layout.addRow("Crystal Symmetry", self._symmetry)
        layout.addRow("Tolerance Level", self._toleranceSelector)

    def getSymmetry(self) -> str:
        return self._symmetry.currentText()

    def getTwoThetaRange(self) -> tuple[float, float]:
        return self._intensityTwoThetaRange.getValue()

    def getMinPeaks(self) -> int:
        return self._minpks.value()

    def getTolerances(self) -> Tuple[float, ...]:
        return self._toleranceSelector.getValue()

    def setSymmetry(self, value: str):
        return self._symmetry.setCurrentText(value)

    def setTwoThetaRange(self, value: tuple[float, float]):
        return self._intensityTwoThetaRange.setValue(value)

    def setMinPeaks(self, value: int):
        return self._minpks.setValue(value)

    def setTolerances(self, value: Tuple[float, ...]):
        return self._toleranceSelector.setValue(value)
