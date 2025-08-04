from __future__ import annotations

import numpy as np
import qtawesome
from silx.gui import qt
from silx.gui.colors import Colormap
from silx.gui.dialog.ColormapDialog import ColormapDialog
from silx.gui.plot import PlotWidget, actions
from silx.gui.plot.items import Scatter
from silx.gui.plot.tools import PositionInfo

_UNFILTERED_PEAKS_LEGEND = "unfiltered"


class _PeakFilterToolBar(qt.QToolBar):
    togglePeaks = qt.Signal(bool)

    def __init__(
        self,
        plot: PlotWidget,
        parent=None,
    ):
        super().__init__("Plot Tools", parent)

        self.setToolButtonStyle(qt.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        zoomAction = actions.mode.ZoomModeAction(parent=self, plot=plot)
        panAction = actions.mode.PanModeAction(parent=self, plot=plot)
        self.addAction(panAction)
        self.addAction(zoomAction)
        plot.setInteractiveMode("pan")

        resetZoom = actions.control.ResetZoomAction(parent=self, plot=plot)
        self.addAction(resetZoom)
        colormapAction = actions.control.ColormapAction(parent=self, plot=plot)
        colormapDialog = ColormapDialog(parent=self)
        colormapAction.setColorDialog(colormapDialog)
        self.addAction(colormapAction)
        self._togglePeaksAction = qt.QAction(
            qtawesome.icon("fa6s.xmark", rotated=45), "Show/Hide Unfiltered Peaks", self
        )
        self._togglePeaksAction.setIconText("Unfiltered peaks")
        self._togglePeaksAction.setCheckable(True)
        self._togglePeaksAction.setChecked(True)
        self._togglePeaksAction.triggered.connect(self.togglePeaks)
        self.addAction(self._togglePeaksAction)


class PeakFilterPlot2D(qt.QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._initCentralLayout()
        toolbar = _PeakFilterToolBar(
            plot=self._plot,
            parent=self,
        )
        toolbar.togglePeaks.connect(self._toggleInPeaks)
        toolbar.setToolButtonStyle(qt.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.addToolBar(qt.Qt.TopToolBarArea, toolbar)
        self._toolbar = toolbar

    def _initCentralLayout(self):
        centralWidget = qt.QWidget(self)
        self.setCentralWidget(centralWidget)

        self._plot = PlotWidget(parent=centralWidget, backend="gl")
        self._plot.setGraphGrid(True)
        self._plot.setAxesMargins(0.05, 0.03, 0.03, 0.05)
        self._plot.setKeepDataAspectRatio(False)
        positionInfo = PositionInfo(plot=self._plot, parent=centralWidget)

        layout = qt.QGridLayout(centralWidget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._plot, 0, 0)
        layout.addWidget(positionInfo, 1, 0, 1, 2)

        centralWidget.setLayout(layout)

    def getPlotWidget(self) -> PlotWidget:
        return self._plot

    def addUnfilteredScatter(
        self,
        x: np.ndarray,
        y: np.ndarray,
        value: np.ndarray,
        colormap: Colormap | dict,
    ) -> Scatter:
        scatter = self._plot.addScatter(
            x=x,
            y=y,
            value=value,
            colormap=colormap,
            symbol="+",
            legend=_UNFILTERED_PEAKS_LEGEND,
        )
        scatter.setSymbolSize(7)
        return scatter

    def addFilteredScatter(
        self,
        x: np.ndarray,
        y: np.ndarray,
        value: np.ndarray,
        colormap: Colormap | dict,
    ) -> Scatter:
        scatter = self._plot.addScatter(
            x=x,
            y=y,
            value=value,
            colormap=colormap,
            symbol="o",
            legend="filtered",
        )
        scatter.setSymbolSize(7)
        return scatter

    def resetZoom(self):
        self._plot.resetZoom()

    def setYAxisLogarithmic(self, flag=True):
        self._plot.setYAxisLogarithmic(flag)

    def setGraphXLabel(self, str_val: str):
        self._plot.setGraphXLabel(str_val)

    def setGraphYLabel(self, label: str):
        self._plot.setGraphYLabel(label)

    def _toggleInPeaks(self, checked: bool):
        scatter = self._plot.getScatter(legend=_UNFILTERED_PEAKS_LEGEND)
        if scatter:
            scatter.setVisible(checked)

    def addCurve(self, x: np.ndarray, y: np.ndarray, legend: str, linewidth: int):
        self._plot.addCurve(x, y, legend=legend, linewidth=linewidth)
