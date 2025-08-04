from __future__ import annotations

from typing import Optional

import numpy as np
from ewoksorange.gui.orange_imports import Input
from ImageD11.unitcell import unitcell as UnitCell
from silx.gui import qt
from silx.gui.colors import Colormap
from silx.gui.plot3d.SceneWindow import SceneWindow
from silx.io.utils import DataUrl

from ewoks3dxrd.io import read_lattice_cell_data
from ewoks3dxrd.nexus.peaks import read_peaks_attributes
from ewoks3dxrd.nexus.utils import group_exists
from ewoks3dxrd.tasks.grid_index_grains import GridIndexGrains

from .common.ewoks3dxrd_widget import Ewoks3DXRDWidget
from .common.grain_size_slider import GrainSizeSlider
from .common.peak_filter_plot2d import PeakFilterPlot2D
from .common.sphere import Spheres, build_grain_spheres
from .indexer.grid_index_settings import GridIndexSettings


class OWGridIndexing(Ewoks3DXRDWidget, ewokstaskclass=GridIndexGrains):
    name = "Grid Indexing"
    description = "Multiprocessing positional search for the grains."
    icon = "icons/grid-search.svg"
    _ewoks_inputs_to_hide_from_orange = (
        "overwrite",
        "grid_index_parameters",
        "grid_abs_x_limit",
        "grid_abs_y_limit",
        "grid_abs_z_limit",
        "grid_step",
        "seed",
        "analyse_folder",
    )

    class Inputs:
        lattice_file = Input("lattice_file", str)

    def __init__(self):
        super().__init__()
        self._settingsPanelWidget = qt.QWidget(self)
        settingLayout = qt.QVBoxLayout(self._settingsPanelWidget)

        self._settingsPanel = GridIndexSettings(self)
        scrollArea = qt.QScrollArea(self)
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(self._settingsPanel)
        settingLayout.addWidget(scrollArea)

        executeOverWriteLayout = qt.QFormLayout()
        self._inputDataUrl = qt.QLineEdit()
        self._overwrite = qt.QCheckBox()
        self._gridIndexerBtn = qt.QPushButton("Run Grid Indexing")
        executeOverWriteLayout.addRow("Input: Data URL", self._inputDataUrl)
        executeOverWriteLayout.addRow("Overwrite", self._overwrite)
        executeOverWriteLayout.addRow(self._gridIndexerBtn)

        self._grainSlider = GrainSizeSlider()
        self._grainSlider.floatValueChanged.connect(self._updateGrainSize)
        self._grainSphere: Optional[Spheres] = None
        executeOverWriteLayout.addRow("Grain Size", self._grainSlider)

        settingLayout.addLayout(executeOverWriteLayout)
        self._gridIndexerBtn.clicked.connect(self.execute_ewoks_task)

        self._grainsPlot = SceneWindow(self)
        self._grainsPlot.setSizePolicy(
            qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding
        )
        self._grainsPlot.getParamTreeView().parent().setVisible(False)
        self._grainsPlot.getGroupResetWidget().parent().setVisible(False)
        self._grainsPlot.getSceneWidget().setBackgroundColor((0.8, 0.8, 0.8, 1.0))

        self._peaksPlot = PeakFilterPlot2D(self)
        self._plotTabWidget = qt.QTabWidget()
        self._plotTabWidget.addTab(self._peaksPlot, "Incoming Peaks")
        self._plotTabWidget.addTab(self._grainsPlot, "Generated Grains")

        self.addControlWidget(self._settingsPanelWidget)
        self.addMainWidget(self._plotTabWidget)

        self._latticeFile = None
        self._ds_ring_limits = 1.4

        self.registerInput(
            "indexer_filtered_data_url", self._getInputUrl, self._inputDataUrl.setText
        )
        self.registerInput(
            "grid_index_parameters",
            self._settingsPanel.getGridIndexParameters,
            self._settingsPanel.setGridIndexParameters,
        )
        self.registerInput(
            "grid_abs_x_limit",
            self._settingsPanel.getGridXLimit,
            self._settingsPanel.setGridXLimit,
        )
        self.registerInput(
            "grid_abs_y_limit",
            self._settingsPanel.getGridYLimit,
            self._settingsPanel.setGridYLimit,
        )
        self.registerInput(
            "grid_abs_z_limit",
            self._settingsPanel.getGridZLimit,
            self._settingsPanel.setGridZLimit,
        )
        self.registerInput(
            "grid_step",
            self._settingsPanel.getGridStep,
            self._settingsPanel.setGridStep,
        )
        self.registerInput(
            "overwrite", self._overwrite.isChecked, self._overwrite.setChecked
        )
        self._restoreDefaultInputs()

    def handleNewSignals(self):
        input_peaks_url = self.get_task_input_value("indexer_filtered_data_url")
        if isinstance(input_peaks_url, str):
            self._inputDataUrl.setText(input_peaks_url)
            self._plotIncomingPeaks()

    def _plotIncomingPeaks(self):
        input_peaks_url = self.get_task_input_value("indexer_filtered_data_url", None)
        if input_peaks_url is None:
            return

        data_url = DataUrl(input_peaks_url)
        nexus_file_path, data_group_path = (
            data_url.file_path(),
            data_url.data_path(),
        )
        incoming_3d_peaks = read_peaks_attributes(
            filename=nexus_file_path,
            process_group=data_group_path,
        )
        self._peaksPlot.addUnfilteredScatter(
            x=incoming_3d_peaks["ds"],
            y=incoming_3d_peaks["eta"],
            value=len(incoming_3d_peaks["eta"]) * [1],
            colormap=Colormap(name="viridis", autoscaleMode="percentile_1_99"),
        )
        self._ds_ring_limits = max(incoming_3d_peaks["ds"])

        self._peaksPlot.setGraphXLabel("Reciprocal distance (ds)")
        self._peaksPlot.setGraphYLabel("Sum Intensity")
        self._peaksPlot.resetZoom()
        if self._latticeFile:
            self._plotLatticeCurve()

    def _plotLatticeCurve(self):
        if self._inputDataUrl.text() == "":
            return
        data_url = DataUrl(self._inputDataUrl.text())
        nexus_file_path, data_group_path = (
            data_url.file_path(),
            data_url.data_path(),
        )
        incoming_3d_peaks = read_peaks_attributes(
            filename=nexus_file_path,
            process_group=data_group_path,
        )

        unit_cell = read_lattice_cell_data(lattice_data_file_path=self._latticeFile)
        unit_cell = UnitCell(
            lattice_parameters=unit_cell.lattice_parameters,
            symmetry=int(unit_cell.space_group),
        )
        unit_cell.makerings(limit=self._ds_ring_limits)
        for i, ring_ds in enumerate(unit_cell.ringds):
            self._peaksPlot.addCurve(
                x=np.array([ring_ds, ring_ds]),
                y=np.array(
                    [
                        min(incoming_3d_peaks["eta"]),
                        max(incoming_3d_peaks["eta"]),
                    ]
                ),
                legend=f"Ring {i}",
                linewidth=2,
            )

    def handleSuccessfulExecution(self):
        output_url = self.get_task_output_value("grid_indexed_grain_data_url", None)
        if output_url is None:
            return
        self._plotTabWidget.setCurrentWidget(self._grainsPlot)
        self._plot3DGrains(output_url)

    def _plot3DGrains(self, url: str):
        self._grainsPlot.getSceneWidget().clearItems()
        self._grainSphere = build_grain_spheres(url, self._grainSlider.value())
        self._grainsPlot.getSceneWidget().addItem(self._grainSphere)

    @Inputs.lattice_file
    def setLatticeFile(self, lattice_file: str):
        self._latticeFile = lattice_file
        self._plotLatticeCurve()

    def _updateGrainSize(self, size: float):
        if self._grainSphere:
            self._grainSphere.setRadiiNorm(radiiNorm=size)
            self._grainSphere.setRadiiNorm(radiiNorm=size)

    def _getInputUrl(self) -> str:
        input_url = DataUrl(self._inputDataUrl.text().strip())
        group_exists(
            filename=input_url.file_path(),
            data_group_path=input_url.data_path(),
        )
        return input_url.path()
