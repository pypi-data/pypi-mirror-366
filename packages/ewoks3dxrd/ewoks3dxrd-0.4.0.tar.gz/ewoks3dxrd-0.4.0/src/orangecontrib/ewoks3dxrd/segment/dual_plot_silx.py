from __future__ import annotations

import numpy as np
import qtawesome
from silx.gui import qt
from silx.gui.colors import Colormap, rgba
from silx.gui.dialog.ColormapDialog import ColormapDialog
from silx.gui.plot import PlotWidget, actions
from silx.gui.plot.ColorBar import ColorBarWidget
from silx.gui.plot.items import Scatter
from silx.gui.plot.tools import PositionInfo
from silx.gui.plot.utils.axis import SyncAxes

from .peak_color_combobox import PeakColorComboBox

IMAGE_NAME = "image"
SCATTER_NAME = "scatter"


class _PlotPanel(qt.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._plot = PlotWidget(parent=self, backend="gl")
        self._plot.setGraphGrid(True)
        self._plot.setAxesMargins(0.05, 0.03, 0.03, 0.05)
        self._plot.setKeepDataAspectRatio(True)
        cmap = Colormap(
            name="viridis", normalization="log", autoscaleMode="percentile_1_99"
        )
        self._plot.setDefaultColormap(cmap)

        self._colorbar = ColorBarWidget(parent=self)
        self._colorbar.setPlot(self._plot)
        self._colorbar.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Expanding)
        self._colorbar.setVisible(False)

        positionInfo = PositionInfo(
            plot=self._plot,
            parent=self,
            converters=(
                ("X", lambda x, y: x),
                ("Y", lambda x, y: y),
                ("Data", self._dataConverter),
            ),
        )

        layout = qt.QGridLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._plot, 0, 0)
        layout.addWidget(self._colorbar, 0, 1)
        layout.addWidget(positionInfo, 1, 0, 1, 2)
        self.setLayout(layout)

    def _dataConverter(self, x: float, y: float) -> str:
        # Inspired by https://github.com/silx-kit/silx/blob/a9d04d831bd6dcb88026aac896cf834a41d0fc93/src/silx/gui/plot/PlotWindow.py#L999
        image = self._plot.getImage(IMAGE_NAME)
        if image is None:
            return "-"

        pixel_coords = self._plot.dataToPixel(x, y)
        if pixel_coords is None:
            return "-"

        picked_image = image.pick(*pixel_coords)
        if picked_image is None:
            return "-"

        indices = picked_image.getIndices(copy=False)
        if indices is None:
            return "-"

        row, col = indices[0][0], indices[1][0]
        return f"{image.getData(copy=False)[row, col]:.2f}"

    def getPlotWidget(self) -> PlotWidget:
        return self._plot

    def setColorBarVisible(self, visible: bool) -> None:
        self._colorbar.setVisible(visible)

    def setImage(
        self, array2D: np.ndarray, title: str, xLabel: str, yLabel: str
    ) -> None:
        self._plot.setGraphTitle(title)
        # Reset zoom only if the image does not exist
        resetzoom = self._plot.getImage(IMAGE_NAME) is None
        self._plot.addImage(array2D, legend=IMAGE_NAME, resetzoom=resetzoom)
        self._plot.setGraphXLabel(xLabel)
        self._plot.setGraphYLabel(yLabel)

    def setScatter(
        self, x: np.ndarray, y: np.ndarray, colormap: Colormap | dict, symbol: str
    ):
        self._plot.addScatter(
            x=x,
            y=y,
            value=np.ones(len(x)),
            colormap=colormap,
            symbol=symbol,
            legend=SCATTER_NAME,
        )

    def getScatter(self) -> Scatter | None:
        return self._plot.getScatter(legend=SCATTER_NAME)

    def getColorBarWidget(self) -> ColorBarWidget:
        return self._colorbar

    def setScatterColor(self, color: str):
        scatter = self._plot.getScatter(SCATTER_NAME)
        if scatter is None:
            return
        scatter.setColormap({"colors": [rgba(color)]})


class SilxSyncDualPlot(qt.QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._initCentralLayout()
        self._addToolbars()
        self._syncAxes()

    def _initCentralLayout(self):
        self._leftPanel = _PlotPanel(self)
        self._rightPanel = _PlotPanel(self)

        splitter = qt.QSplitter(qt.Qt.Horizontal)
        splitter.addWidget(self._leftPanel)
        splitter.addWidget(self._rightPanel)
        self.setCentralWidget(splitter)

    def _addToolbars(self):
        toolbar = qt.QToolBar("Plot Tools", self)
        toolbar.setToolButtonStyle(qt.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.addToolBar(qt.Qt.TopToolBarArea, toolbar)

        zoomAction = actions.mode.ZoomModeAction(
            parent=self, plot=self._leftPanel.getPlotWidget()
        )
        panAction = actions.mode.PanModeAction(
            parent=self, plot=self._leftPanel.getPlotWidget()
        )
        toolbar.addAction(panAction)
        toolbar.addAction(zoomAction)
        self._leftPanel.getPlotWidget().setInteractiveMode("pan")
        self._leftPanel.getPlotWidget().sigInteractiveModeChanged.connect(
            self._syncInteractionMode
        )

        resetZoom = actions.control.ResetZoomAction(
            parent=self, plot=self._leftPanel.getPlotWidget()
        )
        toolbar.addAction(resetZoom)

        colormapAction = actions.control.ColormapAction(
            parent=self, plot=self._leftPanel.getPlotWidget()
        )
        colormapDialog = ColormapDialog(parent=self)

        colormapAction.setColorDialog(colormapDialog)
        toolbar.addAction(colormapAction)
        self._rightPanel.getPlotWidget().setDefaultColormap(
            self._leftPanel.getPlotWidget().getDefaultColormap()
        )

        toggleColorbarAction = actions.control.ColorBarAction(
            plot=self._leftPanel, parent=self
        )
        toggleColorbarAction.setCheckable(True)
        toggleColorbarAction.setChecked(False)
        toolbar.addAction(toggleColorbarAction)
        toggleColorbarAction.triggered.connect(self._toggleBothColorbars)

        toolbar.addSeparator()

        self._togglePeaksAction = qt.QAction(
            qtawesome.icon("fa6s.xmark", rotated=45), "Show/Hide Segmented Peaks", self
        )
        self._togglePeaksAction.setIconText("Peaks")
        self._togglePeaksAction.setCheckable(True)
        self._togglePeaksAction.setChecked(True)
        self._togglePeaksAction.triggered.connect(self._toggleSegmentPeaks)
        toolbar.addAction(self._togglePeaksAction)

        self._peakColorComboBox = PeakColorComboBox(
            parent=self, plot=self._rightPanel.getPlotWidget()
        )
        self._peakColorComboBox.currentColorChanged.connect(self._changePeakColor)
        toolbar.addWidget(self._peakColorComboBox)

    def _syncInteractionMode(self):
        mode = self._leftPanel.getPlotWidget().getInteractiveMode()
        self._rightPanel.getPlotWidget().setInteractiveMode(**mode)

    def _toggleBothColorbars(self, checked):
        self._leftPanel.setColorBarVisible(checked)
        self._rightPanel.setColorBarVisible(checked)

    def _syncAxes(self):
        self._xSync = SyncAxes(
            [
                self._leftPanel.getPlotWidget().getXAxis(),
                self._rightPanel.getPlotWidget().getXAxis(),
            ]
        )
        self._ySync = SyncAxes(
            [
                self._leftPanel.getPlotWidget().getYAxis(),
                self._rightPanel.getPlotWidget().getYAxis(),
            ]
        )

    def _toggleSegmentPeaks(self):
        scatter = self._rightPanel.getScatter()
        if scatter:
            scatter.setVisible(self._togglePeaksAction.isChecked())

    def _changePeakColor(self, newColor: str):
        self._rightPanel.setScatterColor(newColor)

    def setLeftImage(
        self, array2D: np.ndarray, title: str, xLabel: str, yLabel: str
    ) -> None:
        self._rightPanel.setImage(array2D, title, xLabel, yLabel)

    def setRightImage(
        self, array2D: np.ndarray, title: str, xLabel: str, yLabel: str
    ) -> None:
        self._leftPanel.setImage(array2D, title, xLabel, yLabel)

    def setRightScatter(self, x: np.ndarray, y: np.ndarray):
        self._rightPanel.setScatter(
            x=x,
            y=y,
            colormap={"colors": [rgba(self._peakColorComboBox.getCurrentColor())]},
            symbol="x",
        )
        # Sync the visibily of the scatter with the action status
        self._toggleSegmentPeaks()
