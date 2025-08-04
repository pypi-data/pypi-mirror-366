from __future__ import annotations

from typing import Any

from silx.gui import qt

from ewoks3dxrd.models import SegmenterConfig, SegmenterFolderConfig

from .constants import CorrectionFiles
from .correction_group_box import CorrectionGroupBox
from .folder_metadata_group_box import FolderMetadataGroupBox
from .monitor_segment_group_box import MonitorSegmentGroupBox
from .omega_frame_group_box import OmegaFrameGroupBox
from .segmenter_param_group_box import SegmenterParamGroupBox


class SegmenterSettings(qt.QWidget):
    sigParametersChanged = qt.Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Segmenter Config")
        self.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)
        layout = qt.QVBoxLayout()
        self._folder_group = FolderMetadataGroupBox(self)
        layout.addWidget(self._folder_group)
        self._folder_group.sigMasterFileChanged.connect(self._fill_defaults)
        self._omega_frame_group = OmegaFrameGroupBox(self)
        layout.addWidget(self._omega_frame_group)
        self._segmenter_group = SegmenterParamGroupBox(self)
        layout.addWidget(self._segmenter_group)
        self._correction_group = CorrectionGroupBox(self)
        layout.addWidget(self._correction_group)

        self._omega_frame_group.sigFrameIdxReleased.connect(self._on_parameters_changed)
        self._correction_group.sigParamsChanged.connect(self._on_parameters_changed)
        self._segmenter_group.sigParamsChanged.connect(self._on_parameters_changed)

        self._monitor_segment_group = MonitorSegmentGroupBox(self)
        layout.addWidget(self._monitor_segment_group)
        layout.addStretch(1)

        self.setLayout(layout)

    def getParameters(self) -> dict[str, Any]:
        return {
            "segmenter_config": self.getSegmenterConfig(),
            "file_folders": self.getFolderConfig(),
            "correction_files": self.getCorrectionFiles(),
            "monitor_name": self.getMonitorName(),
        }

    def getFolderConfig(self) -> dict[str, Any]:
        return self._folder_group.getConfig().model_dump()

    def setFolderConfig(self, folderConfig: dict):
        self._folder_group.setConfig(SegmenterFolderConfig(**folderConfig))

    def getSegmenterConfig(self) -> dict[str, Any]:
        return self._segmenter_group.getConfig().model_dump()

    def setSegmenterConfig(self, segmenterConfig: dict):
        self._segmenter_group.setConfig(SegmenterConfig(**segmenterConfig))

    def getCorrectionFiles(self) -> CorrectionFiles:
        return self._correction_group.getCorrectionFiles()

    def setCorrectionFiles(self, correctionFiles: dict):
        self._correction_group.setCorrectionFiles(correctionFiles)

    def getMonitorName(self) -> str | None:
        return self._monitor_segment_group.getMonitorName()

    def setMonitorName(self, monitorName: str | None):
        self._monitor_segment_group.setMonitorName(monitorName)

    def _on_parameters_changed(self):
        params = self.getParameters()
        if params:
            self.sigParametersChanged.emit(params)
        else:
            print("Invalid input. Please check the form.")

    def _fill_defaults(self, master_file_path: str):
        motor_name = self._folder_group.getConfig().omega_motor
        self._correction_group.setDefaultCorrectionFiles(motor_name=motor_name)
        scan_number = str(self._folder_group.getScanNumber())
        self._omega_frame_group.setOmegaArray(
            master_file=master_file_path,
            omega_motor=motor_name,
            scan_id=scan_number + ".1",
        )
        self._monitor_segment_group.fillWidgetValues(
            master_file_path=master_file_path, scan_number=scan_number
        )
        self._on_parameters_changed()

    def getScanNumber(self) -> int:
        return self._folder_group.getScanNumber()

    def getFrameIdx(self) -> int | None:
        return self._omega_frame_group.getFrameIdx()

    def getMasterFilePath(self) -> str:
        return self._folder_group.getMasterFilePath()
