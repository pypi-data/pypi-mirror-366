from __future__ import annotations

import os
from typing import Any

from silx.gui import qt

from ..common.collapsible_widget import CollapsibleWidget
from ..common.debounce_timer import DebounceTimer
from ..common.file_folder_browse_button import FileFolderBrowseButton
from .constants import DEFAULTS_CORRECTION_MAP, SEGMENTER_TOOLTIPS, CorrectionFiles


class CorrectionGroupBox(CollapsibleWidget):
    sigParamsChanged = qt.Signal()

    def __init__(self, parent: qt.QWidget | None = None, **kwargs) -> None:
        super().__init__("Correction Files", parent=parent, **kwargs)

        corr_layout = qt.QFormLayout()
        self._bg_file_btn = FileFolderBrowseButton(dialogTitle="Select Background File")
        self._mask_file_btn = FileFolderBrowseButton(dialogTitle="Select Mask File")
        self._dark_file_btn = FileFolderBrowseButton(dialogTitle="Select Dark File")
        self._flat_file_btn = FileFolderBrowseButton(
            dialogTitle="Select Flat Field File"
        )

        self._bg_file_btn.setToolTip(SEGMENTER_TOOLTIPS["bg_file"])
        self._mask_file_btn.setToolTip(SEGMENTER_TOOLTIPS["mask_file"])
        self._dark_file_btn.setToolTip(SEGMENTER_TOOLTIPS["dark_file"])
        self._flat_file_btn.setToolTip(SEGMENTER_TOOLTIPS["flat_file"])

        self._last_params: dict[str, str] = {}
        self._debounce_timer = DebounceTimer(
            callback=self._on_param_changed, timeout_ms=200, parent=self
        )

        for widget in [
            self._bg_file_btn,
            self._mask_file_btn,
            self._dark_file_btn,
            self._flat_file_btn,
        ]:
            widget._line_edit.textChanged.connect(self._debounce_timer.start)

        corr_layout.addRow("Background File:", self._bg_file_btn)
        corr_layout.addRow("Mask File:", self._mask_file_btn)
        corr_layout.addRow("Dark File:", self._dark_file_btn)
        corr_layout.addRow("Flat Field File:", self._flat_file_btn)

        self.setLayout(corr_layout)

    def setDefaultCorrectionFiles(self, motor_name: str) -> None:
        defaults = DEFAULTS_CORRECTION_MAP.get(motor_name)
        if not defaults:
            return
        self._bg_file_btn.clearText()
        self._mask_file_btn.clearText()
        self._dark_file_btn.clearText()
        self._flat_file_btn.clearText()

        self.setCorrectionFiles(defaults)

    def getCorrectionFiles(self) -> CorrectionFiles:
        return {
            "bg_file": self._bg_file_btn.getText() or None,
            "mask_file": self._mask_file_btn.getText() or None,
            "dark_file": self._dark_file_btn.getText() or None,
            "flat_file": self._flat_file_btn.getText() or None,
        }

    def setCorrectionFiles(self, correctionFiles: dict[str, Any]):
        bg_file = correctionFiles.get("bg_file")
        if bg_file:
            self._bg_file_btn.setText(bg_file)

        mask_file = correctionFiles.get("mask_file")
        if mask_file:
            self._mask_file_btn.setText(mask_file)

        dark_file = correctionFiles.get("dark_file")
        if dark_file:
            self._dark_file_btn.setText(dark_file)

        flat_file = correctionFiles.get("flat_file")
        if flat_file:
            self._flat_file_btn.setText(flat_file)

    def _on_param_changed(self):
        params = self.getCorrectionFiles()
        if not params or self._last_params == params:
            return

        invalid_files = {
            key: path
            for key, path in params.items()
            if path is not None and not os.path.isfile(path)
        }

        if invalid_files:
            """
            msg = "The following file(s) do not exist:\n"
            msg += "\n".join(f"- {key}: {path}" for key, path in invalid_files.items())
            qt.QMessageBox.critical(self, "Invalid Correction Files", msg)
            """
            return

        self._last_params = params
        self.sigParamsChanged.emit()
