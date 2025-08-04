from __future__ import annotations

import os

from silx.gui import qt

from ewoks3dxrd.models import SegmenterFolderConfig

from ..common.file_folder_browse_button import FileFolderBrowseButton
from ..common.master_file_widget import MasterFileWidget
from .constants import Detector, OmegaMotor
from .utils import find_possible_scan_numbers, get_unique_instrument_keys


class FolderMetadataGroupBox(qt.QGroupBox):
    sigMasterFileChanged = qt.Signal(str)

    def __init__(self, parent: qt.QWidget | None = None, **kwargs) -> None:
        super().__init__("Folder and Metadata Settings", parent=parent, **kwargs)
        folder_layout = qt.QFormLayout(self)
        self._master_file_path = MasterFileWidget(
            dialogTitle="3DXRD Experiment Master File"
        )
        folder_layout.addRow("Master File:", self._master_file_path)
        self._master_file_path.sigMasterFileChanged.connect(
            self._on_master_file_changed
        )

        self._omega_motor = qt.QComboBox()
        self._omega_motor.addItems([e.value for e in OmegaMotor])
        folder_layout.addRow("Omega Motor:", self._omega_motor)

        self._detector = qt.QComboBox()
        self._detector.addItems([e.value for e in Detector])
        folder_layout.addRow("Detector:", self._detector)

        self._scan_number = qt.QComboBox()
        folder_layout.addRow("Scan Number", self._scan_number)

        self._analyse_folder_path = FileFolderBrowseButton(
            dialogTitle="Select Analysis Folder", directory=True
        )
        folder_layout.addRow("Analyse Folder Path:", self._analyse_folder_path)

    def _on_master_file_changed(self, master_file_path: str):
        self._set_default_folder_metadata(master_file_path)
        instrument_keys = get_unique_instrument_keys(
            master_file=master_file_path, groups=["1.1", "1.2"]
        )
        self._set_default_detector(instrument_keys)
        self._set_default_motor(instrument_keys)

        self.sigMasterFileChanged.emit(master_file_path)

    def _set_default_folder_metadata(self, master_file: str):
        parent_dir = os.path.dirname(master_file)
        self._scan_number.clear()
        candidates = find_possible_scan_numbers(master_file)
        for c in candidates:
            self._scan_number.addItem(str(c))
        self._scan_number.setDisabled(len(candidates) <= 1)

        processed_data_path = os.path.dirname(parent_dir)
        processed_data_path = os.path.dirname(processed_data_path)
        processed_data_path = os.path.dirname(processed_data_path)
        processed_data_path = os.path.join(processed_data_path, "PROCESSED_DATA")
        if os.path.exists(processed_data_path):
            self._analyse_folder_path.setText(processed_data_path)

    def _set_default_detector(self, instrument_keys):
        detector_match = None
        for detector in Detector:
            if detector in instrument_keys:
                detector_match = detector
                break

        if detector_match:
            idx = self._detector.findText(detector_match)
            if idx != -1:
                self._detector.setCurrentIndex(idx)
                self._detector.setEnabled(False)

    def _set_default_motor(self, instrument_keys):
        omega_match = None
        for motor in OmegaMotor:
            if motor in instrument_keys:
                omega_match = motor
                break

        if omega_match:
            idx = self._omega_motor.findText(omega_match)
            if idx != -1:
                self._omega_motor.setCurrentIndex(idx)
                self._omega_motor.setEnabled(False)

    def getConfig(self) -> SegmenterFolderConfig:
        return SegmenterFolderConfig(
            omega_motor=self._omega_motor.currentText(),
            master_file=self._master_file_path.getText(),
            scan_number=int(self._scan_number.currentText()),
            detector=self._detector.currentText(),
            analyse_folder=self._analyse_folder_path.getText() or None,
        )

    def setConfig(self, config: SegmenterFolderConfig):
        self._master_file_path.setText(config.master_file)
        self._scan_number.setCurrentText(str(config.scan_number))
        self._omega_motor.setCurrentText(config.omega_motor)
        self._detector.setCurrentText(config.detector)
        if config.analyse_folder:
            self._analyse_folder_path.setText(config.analyse_folder)

    def getScanNumber(self) -> int:
        return int(self._scan_number.currentText())

    def getMasterFilePath(self) -> str:
        return self._master_file_path.getText()
