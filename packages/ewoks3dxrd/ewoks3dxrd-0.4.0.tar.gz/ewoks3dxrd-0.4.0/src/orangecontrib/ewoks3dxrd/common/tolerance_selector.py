from __future__ import annotations

from typing import Tuple

from silx.gui import qt

TOLERANCE_PRESETS: dict[str, Tuple[float, ...]] = {
    "Fast": (0.02,),
    "Moderate": (0.02, 0.015, 0.01),
    "Fine": (0.02, 0.015, 0.0125, 0.01, 0.007),
}


class ToleranceSelector(qt.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = qt.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._radioFast = qt.QRadioButton("Fast")
        self._radioModerate = qt.QRadioButton("Moderate")
        self._radioFine = qt.QRadioButton("Fine")
        self._radioModerate.setChecked(True)

        layout.addWidget(self._radioFast)
        layout.addWidget(self._radioModerate)
        layout.addWidget(self._radioFine)

    def getValue(self) -> Tuple[float, ...]:
        if self._radioFast.isChecked():
            return TOLERANCE_PRESETS["Fast"]
        elif self._radioModerate.isChecked():
            return TOLERANCE_PRESETS["Moderate"]
        elif self._radioFine.isChecked():
            return TOLERANCE_PRESETS["Fine"]
        else:
            raise ValueError("No tolerance preset selected")

    def setValue(self, value: Tuple[float, ...]):
        if value == TOLERANCE_PRESETS["Fine"]:
            self._radioFine.setChecked(True)
        if value == TOLERANCE_PRESETS["Moderate"]:
            self._radioModerate.setChecked(True)
        else:
            self._radioFast.setChecked(True)
            self._radioFast.setChecked(True)
            self._radioFast.setChecked(True)
            self._radioFast.setChecked(True)
