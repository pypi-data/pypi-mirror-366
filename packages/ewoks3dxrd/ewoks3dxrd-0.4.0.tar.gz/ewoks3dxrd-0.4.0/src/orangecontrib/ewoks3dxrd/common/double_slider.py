from typing import Optional
from silx.gui import qt


class QDoubleSlider(qt.QSlider):
    floatValueChanged = qt.Signal(float)

    def __init__(
        self, orientation: qt.Qt.Orientation, parent: Optional[qt.QWidget] = None
    ):
        super().__init__(orientation, parent)
        self._min = 0.0
        self._max = 1.0
        self._precision = 10000
        super().setRange(0, self._precision)
        self.valueChanged.connect(self._emitFloatValue)

    def setRange(self, min_val: float, max_val: float):
        self._min = min_val
        self._max = max_val

    def value(self) -> float:
        int_val = super().value()
        return self._min + (self._max - self._min) * int_val / self._precision

    def setFloatValue(self, val: float):
        ratio = (val - self._min) / (self._max - self._min)
        int_val = int(ratio * self._precision)
        super().setValue(int_val)

    def _emitFloatValue(self, _):
        float_val = self.value()
        self.floatValueChanged.emit(float_val)
