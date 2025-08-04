from __future__ import annotations

from typing import Optional

from ewokscore import missing_data
from silx.gui import qt
from silx.gui.plot3d.SceneWindow import SceneWindow

from ewoks3dxrd.tasks.make_grain_map import MakeGrainMap

from .common.ewoks3dxrd_widget import Ewoks3DXRDWidget
from .common.grain_size_slider import GrainSizeSlider
from .common.sphere import Spheres, build_grain_spheres
from .makegrains.grain_map_parameter_group_box import GrainMapParameterGroupBox


class OWMakeGrainMap(Ewoks3DXRDWidget, ewokstaskclass=MakeGrainMap):
    name = "Refine Grain Mapping"
    description = "Second Stage Indexing (refine grain positions)."
    icon = "icons/maps.svg"
    _ewoks_inputs_to_hide_from_orange = (
        "overwrite",
        "intensity_frac",
        "hkl_tols",
        "minpks",
        "intensity_two_theta_range",
        "symmetry",
        "analyse_folder",
        "process_group_name",
    )

    def __init__(self):
        super().__init__()
        self._settingsPanelWidget = qt.QWidget(self)
        settingLayout = qt.QVBoxLayout(self._settingsPanelWidget)

        self._settingsPanel = GrainMapParameterGroupBox(self)
        settingLayout.addWidget(self._settingsPanel)

        executeOverWriteLayout = qt.QFormLayout()
        self._inputGrainDataUrl = qt.QLineEdit()
        self._inputStrongFilteredPeaksDataUrl = qt.QLineEdit()

        self._allAlignedPeaksWidget = qt.QWidget()
        allAlignedPeaksLayout = qt.QHBoxLayout(self._allAlignedPeaksWidget)
        allAlignedPeaksLayout.setContentsMargins(0, 0, 0, 0)
        self._allAlignedPeaksDataUrl = qt.QLineEdit()
        self._allAlignedPeaksCheckbox = qt.QCheckBox("Use all Peaks")
        allAlignedPeaksLayout.addWidget(self._allAlignedPeaksDataUrl)
        allAlignedPeaksLayout.addWidget(self._allAlignedPeaksCheckbox)
        self._allAlignedPeaksWidget.setToolTip(
            "Use all peaks aligned with lattice rings to validate grains. Otherwise, grains are refined using only strongly filtered peaks."
        )

        self._latticeParFile = qt.QLineEdit()
        self._overwrite = qt.QCheckBox()

        self._refineGrainsBtn = qt.QPushButton("Refine Grains")
        executeOverWriteLayout.addRow("Input Grain Data URL", self._inputGrainDataUrl)
        executeOverWriteLayout.addRow(
            "Strong Filtered Peaks URL", self._inputStrongFilteredPeaksDataUrl
        )
        executeOverWriteLayout.addRow("All Peaks Data URL", self._allAlignedPeaksWidget)
        executeOverWriteLayout.addRow(
            "Lattice Parameter File Path", self._latticeParFile
        )
        executeOverWriteLayout.addRow("Overwrite", self._overwrite)
        executeOverWriteLayout.addRow(self._refineGrainsBtn)

        self._grainSlider = GrainSizeSlider()
        self._grainSlider.floatValueChanged.connect(self._updateGrainSize)
        self._grainSphere: Optional[Spheres] = None
        executeOverWriteLayout.addRow("Grain Size", self._grainSlider)

        settingLayout.addLayout(executeOverWriteLayout)
        self.addControlWidget(self._settingsPanelWidget)

        self._refineGrainsPlot = SceneWindow(self)
        self._refineGrainsPlot.getParamTreeView().parent().setVisible(False)
        self._refineGrainsPlot.getGroupResetWidget().parent().setVisible(False)
        self._refineGrainsPlot.getSceneWidget().setBackgroundColor((0.8, 0.8, 0.8, 1.0))
        self._refineGrainsPlot.setSizePolicy(
            qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding
        )
        self.addMainWidget(self._refineGrainsPlot)

        self._refineGrainsBtn.clicked.connect(self.execute_ewoks_task)

        self.registerInput(
            "indexed_grain_data_url",
            self._inputGrainDataUrl.text,
            self._inputGrainDataUrl.setText,
        )
        self.registerInput(
            "intensity_filtered_data_url",
            self._inputStrongFilteredPeaksDataUrl.text,
            self._inputStrongFilteredPeaksDataUrl.setText,
        )
        self.registerInput(
            "hkl_tols",
            self._settingsPanel.getTolerances,
            self._settingsPanel.setTolerances,
        )
        self.registerInput(
            "minpks", self._settingsPanel.getMinPeaks, self._settingsPanel.setMinPeaks
        )
        self.registerInput(
            "intensity_fine_filtered_data_url",
            self._getIntensityFineFilteredDataUrl,
            self._allAlignedPeaksDataUrl.setText,
        )
        self.registerInput(
            "intensity_two_theta_range",
            self._settingsPanel.getTwoThetaRange,
            self._settingsPanel.setTwoThetaRange,
        )
        self.registerInput(
            "symmetry", self._settingsPanel.getSymmetry, self._settingsPanel.setSymmetry
        )
        self.registerInput(
            "lattice_file", self._latticeParFile.text, self._latticeParFile.setText
        )
        self.registerInput(
            "overwrite", self._overwrite.isChecked, self._overwrite.setChecked
        )
        self._restoreDefaultInputs()

    def _getIntensityFineFilteredDataUrl(self) -> missing_data.MissingData | str:
        url = self._allAlignedPeaksDataUrl.text().strip()
        if not url:
            return missing_data.MISSING_DATA

        return url

    def handleNewSignals(self):

        all_peaks_url = self.get_task_input_value("intensity_fine_filtered_data_url")
        if isinstance(all_peaks_url, str):
            self._allAlignedPeaksDataUrl.setText(all_peaks_url)

        strong_filtered_peaks_url = self.get_task_input_value(
            "intensity_filtered_data_url"
        )
        if isinstance(strong_filtered_peaks_url, str):
            self._inputStrongFilteredPeaksDataUrl.setText(strong_filtered_peaks_url)

        grains_data_url = self.get_task_input_value("indexed_grain_data_url")
        if isinstance(grains_data_url, str):
            self._inputGrainDataUrl.setText(grains_data_url)

        lattice_file = self.get_task_input_value("lattice_file")
        if isinstance(lattice_file, str):
            self._latticeParFile.setText(lattice_file)

        folder_file_config = self.get_task_input_value("folder_file_config")
        if isinstance(lattice_file, str):
            self.set_default_input("folder_file_config", folder_file_config)

    def handleSuccessfulExecution(self):
        if self.get_task_output_value("make_map_data_url", None) is None:
            return
        self._plot3DGrains(self.get_task_output_value("make_map_data_url"))

    def _plot3DGrains(self, url: str):
        self._refineGrainsPlot.getSceneWidget().clearItems()
        self._grainSphere = build_grain_spheres(url, self._grainSlider.value())
        self._refineGrainsPlot.getSceneWidget().addItem(self._grainSphere)

    def _updateGrainSize(self, size: float):
        if self._grainSphere:
            self._grainSphere.setRadiiNorm(radiiNorm=size)
