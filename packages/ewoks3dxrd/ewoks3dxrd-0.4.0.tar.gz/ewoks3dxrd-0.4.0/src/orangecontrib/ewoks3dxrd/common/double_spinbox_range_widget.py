from silx.gui import qt


class DoubleSpinBoxRangeWidget(qt.QWidget):
    """A widget with two QDoubleSpinBoxes representing a range (min, max) in a single row."""

    def __init__(
        self,
        parent=None,
        minimum=0.0,
        maximum=180.0,
        decimals=2,
        step=0.1,
        default=(0.0, 180.0),
    ):
        super().__init__(parent)
        layout = qt.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._minSpin = qt.QDoubleSpinBox(self)
        self._maxSpin = qt.QDoubleSpinBox(self)

        for spin in (self._minSpin, self._maxSpin):
            spin.setDecimals(decimals)
            spin.setRange(minimum, maximum)
            spin.setSingleStep(step)

        self._minSpin.setValue(default[0])
        self._maxSpin.setValue(default[1])

        layout.addWidget(self._minSpin)
        layout.addWidget(qt.QLabel("to"))
        layout.addWidget(self._maxSpin)

    def getValue(self) -> tuple[float, float]:
        return (self._minSpin.value(), self._maxSpin.value())

    def setValue(self, values: tuple[float, float]):
        self._minSpin.setValue(values[0])
        self._maxSpin.setValue(values[1])
