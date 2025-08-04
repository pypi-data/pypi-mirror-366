from __future__ import annotations

from silx.gui import qt
from silx.gui.colors import Colormap
from silx.io.utils import DataUrl

from ewoks3dxrd.nexus.peaks import read_peaks_attributes
from ewoks3dxrd.nexus.utils import group_exists
from ewoks3dxrd.tasks.filter_by_intensity import FilterByIntensity, Inputs

from .common.ewoks3dxrd_widget import Ewoks3DXRDWidget
from .common.peak_filter_plot2d import PeakFilterPlot2D
from .common.process_name_line_edit import ProcessNameLineEdit


class OWIntensityFilter(Ewoks3DXRDWidget, ewokstaskclass=FilterByIntensity):
    name = "Intensity Filter"
    description = "Filter peaks based on the Intensity."
    icon = "icons/filter-invert.svg"

    _ewoks_inputs_to_hide_from_orange = (
        "overwrite",
        "intensity_frac",
        "process_group_name",
    )

    def __init__(self):
        super().__init__()

        self._settingsPanelWidget = qt.QWidget(self)
        settingLayout = qt.QVBoxLayout(self._settingsPanelWidget)

        self._intensityFrac = qt.QDoubleSpinBox()
        self._intensityFrac.setSingleStep(0.0001)
        self._intensityFrac.setRange(0.001, 1.0)
        self._intensityFrac.setValue(0.9999)
        self._intensityFrac.setDecimals(4)
        hbox = qt.QHBoxLayout()
        label = qt.QLabel("Intensity Fraction")
        hbox.addWidget(label)
        hbox.addWidget(self._intensityFrac)
        settingLayout.addLayout(hbox)

        executeOverWriteLayout = qt.QFormLayout()
        self._processNameLineEdit = ProcessNameLineEdit(
            Inputs.model_fields["process_group_name"].default
        )
        self._inputPeaksUrl = qt.QLineEdit()
        self._overwrite = qt.QCheckBox()
        self._filterPeaksBtn = qt.QPushButton("Filter Peaks")
        executeOverWriteLayout.addRow("Incoming Data URL", self._inputPeaksUrl)
        executeOverWriteLayout.addRow(
            self._processNameLineEdit.label, self._processNameLineEdit
        )
        executeOverWriteLayout.addRow("Overwrite", self._overwrite)
        executeOverWriteLayout.addRow(self._filterPeaksBtn)
        settingLayout.addLayout(executeOverWriteLayout)
        self._filterPeaksBtn.clicked.connect(self.execute_ewoks_task)

        self.addControlWidget(self._settingsPanelWidget)
        self._plot = PeakFilterPlot2D(self)
        self.addMainWidget(self._plot)
        self.registerInput(
            "lattice_filtered_data_url",
            self._validateInputUrl,
            self._inputPeaksUrl.setText,
        )
        self.registerInput(
            "intensity_frac", self._intensityFrac.value, self._intensityFrac.setValue
        )
        self.registerInput(
            "process_group_name",
            self._processNameLineEdit.getText,
            self._processNameLineEdit.setText,
        )
        self.registerInput(
            "overwrite", self._overwrite.isChecked, self._overwrite.setChecked
        )
        self._restoreDefaultInputs()
        self._plotIncomingPeaks()

    def handleNewSignals(self):
        input_url = self.get_task_input_value("lattice_filtered_data_url", None)
        if input_url:
            self._inputPeaksUrl.setText(input_url)
            self._validateInputUrl()
            self._plotIncomingPeaks()

    def _plotIncomingPeaks(self):
        inputUrl = self._inputPeaksUrl.text().strip()
        if not inputUrl:
            return
        data_url = DataUrl(inputUrl)
        nexus_file_path, lattice_data_group_path = (
            data_url.file_path(),
            data_url.data_path(),
        )
        lattice_3d_peaks = read_peaks_attributes(
            filename=nexus_file_path,
            process_group=lattice_data_group_path,
        )

        self._plot.addUnfilteredScatter(
            x=lattice_3d_peaks["ds"],
            y=lattice_3d_peaks["sum_intensity"],
            value=len(lattice_3d_peaks["ds"]) * [1],
            colormap=Colormap(name="viridis", autoscaleMode="percentile_1_99"),
        )
        self._plot.setGraphXLabel("Reciprocal distance (ds)")
        self._plot.setGraphYLabel("Sum Intensity")
        self._plot.setYAxisLogarithmic(True)
        self._plot.resetZoom()

    def handleSuccessfulExecution(self):
        if self.get_task_output_value("intensity_filtered_data_url", None) is None:
            return

        data_url = DataUrl(self.get_task_output_value("intensity_filtered_data_url"))
        nexus_file_path, lattice_data_group_path = (
            data_url.file_path(),
            data_url.data_path(),
        )
        intensity_3d_peaks = read_peaks_attributes(
            filename=nexus_file_path,
            process_group=lattice_data_group_path,
        )
        self._plot.addFilteredScatter(
            x=intensity_3d_peaks["ds"],
            y=intensity_3d_peaks["sum_intensity"],
            value=intensity_3d_peaks["Number_of_pixels"],
            colormap=Colormap(
                name="viridis", normalization="log", autoscaleMode="percentile_1_99"
            ),
        )
        self._plot.setGraphXLabel("Reciprocal distance (ds)")
        self._plot.setGraphYLabel("Sum Intensity")
        self._plot.resetZoom()

    def _validateInputUrl(self) -> str:
        input_peaks_url = DataUrl(self._inputPeaksUrl.text().strip())
        group_exists(
            filename=input_peaks_url.file_path(),
            data_group_path=input_peaks_url.data_path(),
        )
        return input_peaks_url.path()
