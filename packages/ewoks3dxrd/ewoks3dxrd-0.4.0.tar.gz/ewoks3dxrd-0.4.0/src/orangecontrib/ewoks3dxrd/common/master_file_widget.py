from __future__ import annotations
from silx.gui import qt
import os
from ..common.filename_completer_line_edit import FilenameCompleterLineEdit


class MasterFileWidget(qt.QWidget):
    sigMasterFileChanged = qt.Signal(str)

    def __init__(
        self,
        dialogTitle="Select Master File",
        parent: qt.QWidget | None = None,
        **kwargs,
    ) -> None:
        super().__init__(parent=parent, **kwargs)

        self._line_edit = FilenameCompleterLineEdit(self)
        self._browse_btn = qt.QPushButton("Browse...")

        layout = qt.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._line_edit)
        layout.addWidget(self._browse_btn)

        self._dialog_title = dialogTitle
        self._browse_btn.clicked.connect(self._open_file_dialog)
        self._line_edit.textChanged.connect(self._on_text_changed)
        self._last_emitted_path = None

    def _open_file_dialog(self):
        path, _ = qt.QFileDialog.getOpenFileName(self, self._dialog_title)
        if path:
            self._line_edit.setText(path)

    def getText(self) -> str:
        return self._line_edit.text().strip()

    def setText(self, file_path):
        self._line_edit.setText(file_path)

    def _on_text_changed(self, text: str):
        path = text.strip()
        if os.path.isfile(path) and path != self._last_emitted_path:
            self._last_emitted_path = path
            self.sigMasterFileChanged.emit(path)
