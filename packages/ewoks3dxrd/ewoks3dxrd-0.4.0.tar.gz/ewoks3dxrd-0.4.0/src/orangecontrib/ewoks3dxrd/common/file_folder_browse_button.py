from __future__ import annotations
from silx.gui import qt
from .filename_completer_line_edit import FilenameCompleterLineEdit


class FileFolderBrowseButton(qt.QWidget):
    def __init__(
        self,
        parent: qt.QWidget | None = None,
        dialogTitle: str = "",
        directory: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(parent=parent, **kwargs)

        layout = qt.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._line_edit = FilenameCompleterLineEdit(self)
        _browse_btn = qt.QPushButton("Browse...")

        def open_dialog():
            if directory:
                path = qt.QFileDialog.getExistingDirectory(self, dialogTitle)
            else:
                path, _ = qt.QFileDialog.getOpenFileName(self, dialogTitle)
            if path:
                self._line_edit.setText(path)

        _browse_btn.clicked.connect(open_dialog)

        layout.addWidget(self._line_edit)
        layout.addWidget(_browse_btn)

    def getText(self) -> str:
        return self._line_edit.text().strip()

    def setText(self, path: str):
        self._line_edit.setText(path)

    def eventFilter(self, source, event):
        if event.type() == qt.QtCore.QEvent.Type.ToolTip and self.getText():
            qt.QToolTip.showText(event.globalPos(), self.getText(), self)
            return True
        return super().eventFilter(source, event)

    def clearText(self):
        self._line_edit.clear()
