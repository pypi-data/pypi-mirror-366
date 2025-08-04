from silx.gui import qt

from ..common.master_file_widget import MasterFileWidget
from .geometry_parameters import GeometryParameterGroupBox


class GeometryTransformationSettings(qt.QGroupBox):
    sigParametersChanged = qt.Signal()

    def __init__(self, parent=None):
        super().__init__("Geometry settings", parent)
        self.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)

        layout = qt.QVBoxLayout()
        fileBtnLayout = qt.QFormLayout()
        self._geometryFileWidget = MasterFileWidget(
            dialogTitle="Geometry Parameter File"
        )
        fileBtnLayout.addRow("Import file", self._geometryFileWidget)
        layout.addLayout(fileBtnLayout)
        self._geoParameterGroup = GeometryParameterGroupBox(self)
        layout.addWidget(self._geoParameterGroup)
        self.setLayout(layout)

        self._geometryFileWidget.sigMasterFileChanged.connect(
            self._updateGeometryParameters
        )

    def _updateGeometryParameters(self, filePath: str):
        self._geoParameterGroup.fillGeometryValues(filePath=filePath)

    def getGeometryParameters(self) -> dict[str, str]:
        return self._geoParameterGroup.getGeometryParameters()

    def setGeometryFile(self, filePath: str):
        self._geometryFileWidget.setText(filePath)
