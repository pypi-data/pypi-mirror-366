from silx.gui import qt

from ewoks3dxrd.models import GridIndexParameters

from .grid_index_parameter_group_box import GridIndexParameterGroupBox


class GridIndexSettings(qt.QWidget):
    sigGridSettingsChanged = qt.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Grid Index Config")
        self.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)
        layout = qt.QVBoxLayout()

        _gridSearchGroup = qt.QGroupBox("Sample and Beam Info")

        self._sampleWidth = qt.QSpinBox()
        self._sampleWidth.setRange(1, 10000)
        self._sampleWidth.setValue(1200)
        self._sampleWidth.setSuffix(" µm")
        self._sampleWidth.setToolTip("Provide width of sample.")

        self._sampleHeight = qt.QSpinBox()
        self._sampleHeight.setRange(1, 10000)
        self._sampleHeight.setValue(1200)
        self._sampleHeight.setSuffix(" µm")
        self._sampleHeight.setToolTip("Provide height of sample.")

        self._beamIlluminationRange = qt.QSpinBox()
        self._beamIlluminationRange.setRange(1, 10000)
        self._beamIlluminationRange.setValue(200)
        self._beamIlluminationRange.setSuffix(" µm")
        self._beamIlluminationRange.setToolTip("Provide beam height.")

        self._grainSpottingWidth = qt.QSpinBox()
        self._grainSpottingWidth.setRange(1, 10000)
        self._grainSpottingWidth.setValue(100)
        self._grainSpottingWidth.setSuffix(" µm")
        self._grainSpottingWidth.setToolTip("Provide 1 or 2 times detector pixel size.")

        gridSearchLayout = qt.QFormLayout(_gridSearchGroup)
        gridSearchLayout.addRow("Sample Width", self._sampleWidth)
        gridSearchLayout.addRow("Sample Height", self._sampleHeight)
        gridSearchLayout.addRow("Beam Width", self._beamIlluminationRange)
        gridSearchLayout.addRow("Grid Step", self._grainSpottingWidth)

        layout.addWidget(_gridSearchGroup)
        self._gridIndexParametergroup = GridIndexParameterGroupBox(self)
        layout.addWidget(self._gridIndexParametergroup)
        self.setLayout(layout)

    def getGridIndexParameters(self) -> dict:
        return self._gridIndexParametergroup.getGridIndexParameters().model_dump()

    def getGridXLimit(self) -> int:
        return self._sampleWidth.value()

    def getGridYLimit(self) -> int:
        return self._sampleHeight.value()

    def getGridZLimit(self) -> int:
        return self._beamIlluminationRange.value()

    def getGridStep(self) -> int:
        return self._grainSpottingWidth.value()

    def setGridIndexParameters(self, value: dict):
        self._gridIndexParametergroup.setGridIndexParameters(
            GridIndexParameters(**value)
        )

    def setGridXLimit(self, value: int):
        self._sampleWidth.setValue(value)

    def setGridYLimit(self, value: int):
        self._sampleHeight.setValue(value)

    def setGridZLimit(self, value: int):
        self._beamIlluminationRange.setValue(value)

    def setGridStep(self, value: int):
        self._grainSpottingWidth.setValue(value)
