from __future__ import annotations

from silx.gui import qt
from silx.gui.plot import Plot2D


class Ewoks3DXRDPlot2D(Plot2D):
    def __init__(self, parent: qt.QWidget | None = None) -> None:
        super().__init__(parent=parent, backend="gl")
        self.setBackgroundColor("white")
        self.setKeepDataAspectRatio(True)
        self.setAxesMargins(0.06, 0.06, 0.06, 0.06)
        self.setGraphGrid(True)
        self.setInteractiveMode(mode="pan")
