from __future__ import annotations
import weakref
from enum import StrEnum

from silx.gui import qt
from silx.gui.colors import cursorColorForColormap
from silx.gui.plot import PlotWidget


class ColorOption(StrEnum):
    AUTO = "Auto"
    BLACK = "Black"
    WHITE = "White"


class PeakColorComboBox(qt.QComboBox):
    currentColorChanged = qt.Signal(str)

    def __init__(self, plot: PlotWidget, parent=None):
        super().__init__(parent)
        self._plotRef = weakref.ref(plot)
        for option in ColorOption:
            self.addItem(option.value)

        self.currentTextChanged.connect(self._emitNewColor)

    def _getPlotColormapName(self) -> str | None:
        plot = self._plotRef()
        if plot is None:
            return None

        return plot.getDefaultColormap().getName()

    def _optionToColor(self, option: str) -> str:
        if option == ColorOption.BLACK:
            return "black"
        elif option == ColorOption.WHITE:
            return "white"
        elif option == ColorOption.AUTO:
            currentColormapName = self._getPlotColormapName()
            if currentColormapName is None:
                return "pink"
            return cursorColorForColormap(currentColormapName)
        else:
            raise ValueError(f"Unknown option: {option}")

    def _emitNewColor(self, option: str):
        color = self._optionToColor(option)
        self.currentColorChanged.emit(color)

    def getCurrentColor(self) -> str:
        return self._optionToColor(self.currentText())
