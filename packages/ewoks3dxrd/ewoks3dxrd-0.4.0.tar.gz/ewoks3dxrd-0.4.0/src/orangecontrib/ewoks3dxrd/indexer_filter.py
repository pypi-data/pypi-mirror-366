from __future__ import annotations

from pathlib import Path

from ImageD11.unitcell import unitcell as UnitCell
from silx.gui import qt
from silx.gui.colors import Colormap
from silx.gui.widgets.FloatEdit import FloatEdit
from silx.io.utils import DataUrl

from ewoks3dxrd.io import read_lattice_cell_data
from ewoks3dxrd.nexus.peaks import read_peaks_attributes
from ewoks3dxrd.nexus.utils import group_exists
from ewoks3dxrd.tasks.filter_by_index import FilterByIndexer, Inputs

from .common.ewoks3dxrd_widget import Ewoks3DXRDWidget
from .common.master_file_widget import MasterFileWidget
from .common.peak_filter_plot2d import PeakFilterPlot2D
from .common.process_name_line_edit import ProcessNameLineEdit
from .common.tuple_input_widget import TupleInputWidget


class OWIndexerFilter(Ewoks3DXRDWidget, ewokstaskclass=FilterByIndexer):
    name = "Index Filter"
    description = "Choose rings aligned peaks."
    icon = "icons/rings-smallest.svg"

    _ewoks_inputs_to_hide_from_orange = (
        "overwrite",
        "rings",
        "process_group_name",
    )

    def __init__(self):
        super().__init__()

        controlWidget = qt.QWidget()
        layout = qt.QVBoxLayout(controlWidget)

        settingsWidget = qt.QGroupBox("Index filter settings")
        settingsLayout = qt.QFormLayout(settingsWidget)
        self._ringIndexTuple = TupleInputWidget()
        settingsLayout.addRow("Select Rings", self._ringIndexTuple)
        self._lattice_file = MasterFileWidget("Select Lattice File")
        settingsLayout.addRow("Lattice file", self._lattice_file)
        self._ds_tol = FloatEdit()
        self._ds_tol.setAlignment(qt.Qt.AlignmentFlag.AlignLeft)
        settingsLayout.addRow("Reciprocal distance tolerance", self._ds_tol)
        layout.addWidget(settingsWidget)

        executeOverWriteLayout = qt.QFormLayout()
        self._inputPeaksUrl = qt.QLineEdit()
        self._processNameLineEdit = ProcessNameLineEdit(
            default=Inputs.model_fields["process_group_name"].default
        )
        self._overwrite = qt.QCheckBox()
        self._filterPeaksBtn = qt.QPushButton("Filter according to selected rings")

        executeOverWriteLayout.addRow("Incoming Data URL", self._inputPeaksUrl)
        executeOverWriteLayout.addRow(
            self._processNameLineEdit.label, self._processNameLineEdit
        )
        executeOverWriteLayout.addRow("Overwrite", self._overwrite)
        executeOverWriteLayout.addRow(self._filterPeaksBtn)
        layout.addLayout(executeOverWriteLayout)
        self._filterPeaksBtn.clicked.connect(self.execute_ewoks_task)

        self.addControlWidget(controlWidget)
        self._plot = PeakFilterPlot2D(self)
        self.addMainWidget(self._plot)

        self.registerInput(
            "intensity_filtered_data_url",
            self._getInputUrl,
            self._inputPeaksUrl.setText,
        )
        self.registerInput(
            "rings",
            self._ringIndexTuple.getValue,
            self._ringIndexTuple.setValue,
        )
        self.registerInput("ds_tol", self._ds_tol.value, self._ds_tol.setValue)
        self.registerInput(
            "lattice_file", self._lattice_file.getText, self._lattice_file.setText
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
        input_peaks_url = self.get_task_input_value("intensity_filtered_data_url", None)
        if input_peaks_url:
            self._inputPeaksUrl.setText(input_peaks_url)
        wavelength = self.get_task_input_value("wavelength", None)
        if wavelength:
            self.set_default_input("wavelength", wavelength)
        ds_tol = self.get_task_input_value("ds_tol", None)
        if ds_tol:
            self._ds_tol.setText(str(ds_tol))
        lattice_parameter_file = self.get_task_input_value("lattice_file", None)
        if lattice_parameter_file:
            self._lattice_file.setText(str(lattice_parameter_file))

        if (
            wavelength is None
            or ds_tol is None
            or lattice_parameter_file is None
            or input_peaks_url is None
        ):
            return
        self._validateInputs()
        self._plotIncomingPeaks()

    def _plotIncomingPeaks(self):
        input_url = self.get_task_input_value("intensity_filtered_data_url", None)
        if input_url is None:
            return
        data_url = DataUrl(input_url)
        nexus_file_path, lattice_data_group_path = (
            data_url.file_path(),
            data_url.data_path(),
        )
        intensity_3d_peaks = read_peaks_attributes(
            filename=nexus_file_path,
            process_group=lattice_data_group_path,
        )
        self._plot.addUnfilteredScatter(
            x=intensity_3d_peaks["ds"],
            y=intensity_3d_peaks["sum_intensity"],
            value=len(intensity_3d_peaks["sum_intensity"]) * [1],
            colormap=Colormap(name="viridis", autoscaleMode="percentile_1_99"),
        )
        self._plot.setGraphXLabel("Reciprocal distance (ds)")
        self._plot.setGraphYLabel("Sum Intensity")
        self._plot.setYAxisLogarithmic(True)
        self._plot.resetZoom()
        self._plotRings(
            ds_limit=max(intensity_3d_peaks["ds"]),
            y_limits=[
                min(intensity_3d_peaks["sum_intensity"]),
                max(intensity_3d_peaks["sum_intensity"]),
            ],
        )

    def _plotRings(self, ds_limit: float, y_limits):
        lattice_file_name = self.get_task_input_value("lattice_file")
        if not lattice_file_name:
            return
        unit_cell = read_lattice_cell_data(lattice_data_file_path=lattice_file_name)
        try:
            unit_cell = UnitCell(
                lattice_parameters=unit_cell.lattice_parameters,
                symmetry=int(unit_cell.space_group),
            )
            unit_cell.makerings(limit=ds_limit)

            for i, ring_ds in enumerate(unit_cell.ringds):
                self._plot.addCurve(
                    [ring_ds, ring_ds], y_limits, legend=f"Ring {i}", linewidth=2
                )
        except Exception as e:
            self.showError(e, title="Lattice Ring Plot")

    def handleSuccessfulExecution(self):
        if self.get_task_output_value("indexer_filtered_data_url", None) is None:
            return

        data_url = DataUrl(self.get_task_output_value("indexer_filtered_data_url"))
        nexus_file_path, data_group_path = (
            data_url.file_path(),
            data_url.data_path(),
        )
        index_3d_peaks = read_peaks_attributes(
            filename=nexus_file_path,
            process_group=data_group_path,
        )
        self._plot.addFilteredScatter(
            x=index_3d_peaks["ds"],
            y=index_3d_peaks["sum_intensity"],
            value=index_3d_peaks["Number_of_pixels"],
            colormap=Colormap(
                name="viridis", normalization="log", autoscaleMode="percentile_1_99"
            ),
        )
        self._plot.resetZoom()

    def _validateInputs(self):
        assert isinstance(float(self._ds_tol.text()), float)
        assert Path(str(self._lattice_file.getText().strip())).exists()
        input_peaks_url = DataUrl(self._inputPeaksUrl.text().strip())
        group_exists(
            filename=input_peaks_url.file_path(),
            data_group_path=input_peaks_url.data_path(),
        )

    def _getInputUrl(self) -> str:
        input_peaks_url = DataUrl(self._inputPeaksUrl.text().strip())
        group_exists(
            filename=input_peaks_url.file_path(),
            data_group_path=input_peaks_url.data_path(),
        )
        return input_peaks_url.path()

    def _getRingIndices(self):
        ringIndices = self._ringIndexTuple.getValue()
        if not ringIndices:
            raise ValueError("No ring selected")

        return ringIndices
