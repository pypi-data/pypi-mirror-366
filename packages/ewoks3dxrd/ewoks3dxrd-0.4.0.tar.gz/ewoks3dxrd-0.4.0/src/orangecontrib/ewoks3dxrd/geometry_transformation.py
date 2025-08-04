from pathlib import Path

from ImageD11.unitcell import unitcell as UnitCell
from silx.gui import qt
from silx.gui.colors import Colormap
from silx.io.utils import DataUrl

from ewoks3dxrd.io import save_par_file
from ewoks3dxrd.nexus.peaks import read_peaks_attributes
from ewoks3dxrd.tasks.geometry_transformation import GeometryTransformation

from .common.ewoks3dxrd_plot2d import Ewoks3DXRDPlot2D
from .common.ewoks3dxrd_widget import Ewoks3DXRDWidget
from .geometry.geometry_transformation_settings import GeometryTransformationSettings
from .lattice.lattice_parameters import LatticeParameters


class OWGeometryTransformation(Ewoks3DXRDWidget, ewokstaskclass=GeometryTransformation):
    name = "Geometry Transformation"
    description = (
        "Generate ds, g-vectors, eta, etc on detector corrected segmented 3D Peaks."
    )
    icon = "icons/settings.svg"
    _ewoks_inputs_to_hide_from_orange = (
        "overwrite",
        "geometry_par_file",
    )

    def __init__(self):
        super().__init__()

        self._settingsPanelWidget = qt.QWidget(self)
        settingLayout = qt.QVBoxLayout(self._settingsPanelWidget)
        self._latticeGroup = LatticeParameters("Show lattice rings", self)
        self._latticeGroup.setCheckable(True)
        self._ds_ring_limits = 1.5
        self._latticeGroup.sigLatticeParamsChanged.connect(self._plotRings)
        self._latticeGroup.toggled.connect(self._plotRings)
        self._latticeGroup.toggled.connect(self._latticeGroup.layout().setEnabled)
        self._settingsPanel = GeometryTransformationSettings(self)

        scrollContent = qt.QWidget()
        scrollLayout = qt.QVBoxLayout(scrollContent)
        scrollLayout.addWidget(self._settingsPanel)
        scrollLayout.addWidget(self._latticeGroup)
        scrollLayout.addStretch(1)  # Optional: pushes widgets to top

        scrollArea = qt.QScrollArea(self)
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(scrollContent)

        settingLayout.addWidget(scrollArea)

        executeOverWriteLayout = qt.QFormLayout()
        self._detector_corrected_url = qt.QLineEdit()
        self._overwrite = qt.QCheckBox()
        self._computeGeometryCalculationBtn = qt.QPushButton(
            "Compute Geometry Vectors for Peaks"
        )
        executeOverWriteLayout.addRow(
            "Input: Detector Corrected URL", self._detector_corrected_url
        )
        executeOverWriteLayout.addRow("Overwrite", self._overwrite)
        executeOverWriteLayout.addRow(self._computeGeometryCalculationBtn)
        settingLayout.addLayout(executeOverWriteLayout)
        self._computeGeometryCalculationBtn.clicked.connect(self.execute_ewoks_task)
        self.addControlWidget(self._settingsPanelWidget)

        self._plot = Ewoks3DXRDPlot2D(self)
        self._plot.setKeepDataAspectRatio(False)
        self._plot.getColorBarWidget().setVisible(False)
        self._plot.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)
        self.addMainWidget(self._plot)
        self.registerInput(
            "spatial_corrected_data_url",
            self._validateInputUrl,
            self._detector_corrected_url.setText,
        )
        self.registerInput(
            "geometry_par_file",
            self._prepareGeometryFile,
            self._settingsPanel.setGeometryFile,
        )
        self.registerInput(
            "overwrite", self._overwrite.isChecked, self._overwrite.setChecked
        )
        self._restoreDefaultInputs()

    def _plotRings(self, limit: float | None = None):
        if not self._latticeGroup.isChecked():
            self._plot.clearCurves()
            return

        if limit is None:
            limit = self._ds_ring_limits
        else:
            self._ds_ring_limits = limit

        params = self._latticeGroup.getLatticeParameters()
        try:
            unit_cell = UnitCell(
                lattice_parameters=params["lattice_parameters"],
                symmetry=int(params["lattice_space_group"]),
            )
            unit_cell.makerings(limit=limit)

            for i, ring_ds in enumerate(unit_cell.ringds):
                self._plot.addCurve(
                    [ring_ds, ring_ds], [-190, 190], legend=f"Ring_{i}", linewidth=2
                )
            self._plot.setGraphXLabel("Reciprocal Distance (ds)")
            self._plot.setGraphYLabel("Azimuthal Angle (eta)")
        except Exception as e:
            self.showError(e)

    def handleNewSignals(self):
        spatial_corrected_data_url = self.get_task_input_value(
            "spatial_corrected_data_url"
        )
        if spatial_corrected_data_url is not None:
            self._detector_corrected_url.setText(spatial_corrected_data_url)

    def handleSuccessfulExecution(self):
        if self.get_task_output_value("geometry_updated_data_url") is None:
            return

        data_url = DataUrl(self.get_task_output_value("geometry_updated_data_url"))
        nexus_file_path, geometry_data_group_path = (
            data_url.file_path(),
            data_url.data_path(),
        )
        geo_3d_peaks = read_peaks_attributes(
            filename=nexus_file_path,
            process_group=geometry_data_group_path,
        )
        scatter = self._plot.addScatter(
            x=geo_3d_peaks["ds"],
            y=geo_3d_peaks["eta"],
            value=geo_3d_peaks["Number_of_pixels"],
            colormap=Colormap(
                name="viridis", normalization="log", autoscaleMode="percentile_1_99"
            ),
            symbol="o",
            legend="aligned Peaks",
        )
        scatter.setSymbolSize(7)
        self._plot.setGraphXLabel("Reciprocal distance (ds)")
        self._plot.setGraphYLabel("Azimuthal angle (eta)")
        self._plot.resetZoom()
        self._plotRings(limit=max(geo_3d_peaks["ds"]))

    def _validateInputUrl(self):
        input_url = self._detector_corrected_url.text().strip()
        if not input_url:
            raise ValueError("No detector corrected data URL to process.")

        return input_url

    def _prepareGeometryFile(self) -> str:
        file_path = Path(DataUrl(self._detector_corrected_url.text()).file_path())
        geometry_file = file_path.parent / "geometry_tdxrd.par"
        parameters = self._settingsPanel.getGeometryParameters()
        if not parameters:
            raise ValueError("No geometry parameters to write")
        save_par_file(geometry_file, parameters)
        return str(geometry_file)
