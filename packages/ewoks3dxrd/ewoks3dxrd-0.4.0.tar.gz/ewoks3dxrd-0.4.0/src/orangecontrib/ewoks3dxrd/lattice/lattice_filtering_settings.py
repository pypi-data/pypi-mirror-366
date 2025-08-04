from __future__ import annotations

from typing import Any

from silx.gui import qt

from .lattice_parameters import LatticeParameters


class LatticeFilteringSettings(qt.QWidget):
    sigPlotLatticeRings = qt.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Lattice Config")
        self.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)
        layout = qt.QVBoxLayout()
        self._latticeParGroup = LatticeParameters(parent=self)
        layout.addWidget(self._latticeParGroup)
        self._latticeParGroup.sigLatticeParamsChanged.connect(
            self.sigPlotLatticeRings.emit
        )

        setupGroup = qt.QGroupBox("Tolerance Settings", parent=self)
        setupLayout = qt.QFormLayout(setupGroup)
        self._reciprocalDistTol = qt.QDoubleSpinBox()
        self._reciprocalDistTol.setRange(0.0001, 1)
        self._reciprocalDistTol.setValue(0.005)
        self._reciprocalDistTol.setDecimals(4)
        setupLayout.addRow("Reciprocal Distance Tolerance:", self._reciprocalDistTol)

        self._reciprocalDistMaxCheckbox = qt.QCheckBox("Max Reciprocal Distance")
        self._reciprocalDistMaxCheckbox.setChecked(False)
        self._reciprocalDistMax = qt.QDoubleSpinBox()
        self._reciprocalDistMax.setRange(0.0001, 2)
        self._reciprocalDistMax.setValue(2)
        self._reciprocalDistMax.setDecimals(4)
        self._reciprocalDistMax.setEnabled(False)
        setupLayout.addRow(self._reciprocalDistMaxCheckbox, self._reciprocalDistMax)

        layout.addWidget(setupGroup)
        self.setLayout(layout)
        self._reciprocalDistMaxCheckbox.toggled.connect(
            self._reciprocalDistMax.setEnabled
        )

    def getLatticeParameters(self) -> dict[str, Any]:
        return self._latticeParGroup.getLatticeParameters()

    def setLatticeFile(self, value: str):
        return self._latticeParGroup.setFile(value)

    def getReciprocalDistTol(self) -> float:
        return self._reciprocalDistTol.value()

    def setReciprocalDistTol(self, value: float):
        self._reciprocalDistTol.setValue(value)

    def getReciprocalDistMax(self) -> float | None:
        return (
            self._reciprocalDistMax.value()
            if self._reciprocalDistMaxCheckbox.isChecked()
            else None
        )

    def setReciprocalDistMax(self, value: float | None):
        if value is None:
            self._reciprocalDistMax.clear()
            self._reciprocalDistMaxCheckbox.setChecked(False)
        else:
            self._reciprocalDistMax.setValue(value)
            self._reciprocalDistMaxCheckbox.setChecked(True)
