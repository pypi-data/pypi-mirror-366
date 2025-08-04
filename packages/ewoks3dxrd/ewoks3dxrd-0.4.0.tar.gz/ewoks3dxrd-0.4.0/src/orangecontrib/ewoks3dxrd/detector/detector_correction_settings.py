from __future__ import annotations

import os
from typing import Any

from silx.gui import qt

from ewoks3dxrd.models import DetectorCorrectionFiles

from ..common.file_folder_browse_button import FileFolderBrowseButton


class DetectorCorrectionSettings(qt.QWidget):
    def __init__(self, parent: qt.QWidget | None = None) -> None:
        super().__init__(parent=parent)

        container_layout = qt.QVBoxLayout(self)
        self._radio_spline = qt.QRadioButton("Use Spline File")
        self._radio_correction_files = qt.QRadioButton("Use DX/DY Correction Files")
        self._radio_spline.setChecked(True)

        vbox_spline = qt.QVBoxLayout()
        vbox_spline.addWidget(self._radio_spline)
        self._spline_file = FileFolderBrowseButton(dialogTitle="Spline File")
        vbox_spline.addWidget(self._spline_file)

        vbox_correction = qt.QVBoxLayout()
        vbox_correction.addWidget(self._radio_correction_files)
        self._x_file = FileFolderBrowseButton(dialogTitle="Dx file")
        self._y_file = FileFolderBrowseButton(dialogTitle="Dy file")
        vbox_correction.addWidget(self._x_file)
        vbox_correction.addWidget(self._y_file)

        container_layout.addLayout(vbox_spline)
        container_layout.addLayout(vbox_correction)

        self._radio_spline.toggled.connect(self._toggle_correction_mode)
        self._radio_correction_files.toggled.connect(self._toggle_correction_mode)
        self._toggle_correction_mode()

    def _toggle_correction_mode(self):
        use_spline = self._radio_spline.isChecked()
        self._spline_file.setEnabled(use_spline)
        self._x_file.setDisabled(use_spline)
        self._y_file.setDisabled(use_spline)

    def getCorrectionFiles(self) -> DetectorCorrectionFiles:
        if self._radio_spline.isChecked():
            correction_files = self._spline_file.getText()
        else:
            correction_files = (self._x_file.getText(), self._y_file.getText())

        if not all(correction_files):
            raise ValueError("Set detector correction file(s).")

        return self._validate_correction_files(correction_files)

    def setCorrectionFiles(self, files: Any):
        correction_files = self._validate_correction_files(files)
        if isinstance(correction_files, str):
            self._spline_file.setText(correction_files)
        else:
            x_file, y_file = correction_files
            self._x_file.setText(x_file)
            self._y_file.setText(y_file)

    def _validate_correction_files(self, files: Any) -> DetectorCorrectionFiles:
        if isinstance(files, str):
            if not os.path.exists(files):
                raise FileNotFoundError(f"File does not exist: {files}")

        elif isinstance(files, tuple) and len(files) == 2:
            for f in files:
                if not os.path.exists(f):
                    raise FileNotFoundError(f"File does not exist: {f}")
        else:
            raise ValueError(f"Given correction files are not valid: {files}")

        return files
