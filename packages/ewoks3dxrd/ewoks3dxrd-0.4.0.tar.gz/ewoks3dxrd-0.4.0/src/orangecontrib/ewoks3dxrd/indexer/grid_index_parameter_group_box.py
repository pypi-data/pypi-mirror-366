from __future__ import annotations

from silx.gui import qt

from ewoks3dxrd.models import GridIndexParameters

from ..common.tolerance_selector import ToleranceSelector
from ..common.tuple_input_widget import TupleInputWidget
from .constants import Symmetry


class GridIndexParameterGroupBox(qt.QGroupBox):

    def __init__(self, parent: qt.QWidget | None = None, **kwargs) -> None:
        super().__init__("Grid Index Settings", parent=parent, **kwargs)
        layout = qt.QFormLayout(self)

        self._npks = qt.QSpinBox()
        self._npks.setRange(1, 10000)
        self._npks.setValue(100)
        self._npks.setToolTip("Minimal number of peaks for a grain to be kept")

        self._dstol = qt.QDoubleSpinBox()
        self._dstol.setRange(0.0001, 0.01)
        self._dstol.setSingleStep(0.001)
        self._dstol.setDecimals(4)
        self._dstol.setToolTip(
            "Choose Reciprocal distance tolerance. ex 10e-4 to 10e-3"
        )
        self._dstol.setValue(0.004)

        self._ring1 = TupleInputWidget(placeHolderText="e.g. 1, 0", Type=int)
        self._ring1.setToolTip("Ring 1 indices as comma-separated integers.")

        self._ring2 = TupleInputWidget(placeHolderText="e.g. 0", Type=int)
        self._ring2.setToolTip("Ring 2 indices as comma-separated integers.")

        self._tolangle = qt.QDoubleSpinBox()
        self._tolangle.setRange(0.0001, 10.0)
        self._tolangle.setSingleStep(0.01)
        self._tolangle.setToolTip("Tolerance angle in degrees.")
        self._tolangle.setValue(0.50)
        degSymbol = "\u00b0"
        self._tolangle.setSuffix(f" {degSymbol}")

        self._toldist = qt.QDoubleSpinBox()
        self._toldist.setRange(0.0, 200.0)
        self._toldist.setToolTip(
            "Tolerance Distance, usually in range of 0.5 to 2 times detector pixel width."
        )
        self._toldist.setValue(100.0)
        self._toldist.setSuffix(" µm")

        self._toleranceGroup = ToleranceSelector()

        self._symmetry = qt.QComboBox()
        self._symmetry.addItems([e.value for e in Symmetry])
        self._symmetry.setToolTip("Optional. Symmetry group.")

        layout.addRow("Number of Peaks", self._npks)
        layout.addRow("Reciprocal Tolerance", self._dstol)
        layout.addRow("Ring 1", self._ring1)
        layout.addRow("Ring 2", self._ring2)
        layout.addRow("Tolerance Angle", self._tolangle)
        layout.addRow("Tolerance Distance", self._toldist)
        layout.addRow("Crystal Symmetry", self._symmetry)
        layout.addRow("Tolerance Tuning", self._toleranceGroup)

    def getGridIndexParameters(self) -> GridIndexParameters:
        try:
            self._validate()
            return GridIndexParameters(
                NPKS=self._npks.value(),
                DSTOL=self._dstol.value(),
                RING1=self._ring1.getValue(),
                RING2=self._ring2.getValue(),
                tolangle=self._tolangle.value(),
                toldist=self._toldist.value(),
                TOLSEQ=self._toleranceGroup.getValue(),
                SYMMETRY=self._symmetry.currentText(),
            )
        except Exception as e:
            raise ValueError(e)

    def setGridIndexParameters(self, params: GridIndexParameters):
        self._npks.setValue(params.NPKS)
        self._dstol.setValue(params.DSTOL)
        self._ring1.setValue(params.RING1)
        self._ring2.setValue(params.RING2)
        self._tolangle.setValue(params.tolangle)
        self._toleranceGroup.setValue(params.TOLSEQ)
        self._symmetry.setCurrentText(params.SYMMETRY)

    def _validate(self):
        if not self._ring1.getValue():
            raise ValueError("Ring1 must not be empty")
        if not self._ring2.getValue():
            raise ValueError("Ring2 must not be empty")
