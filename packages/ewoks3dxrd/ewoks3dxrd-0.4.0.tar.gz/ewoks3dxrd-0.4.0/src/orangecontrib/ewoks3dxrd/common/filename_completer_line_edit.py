from __future__ import annotations
from silx.gui import qt


class FilenameCompleterLineEdit(qt.QLineEdit):
    def __init__(self, parent: qt.QWidget | None = None, **kwargs) -> None:
        super().__init__(parent=parent, **kwargs)

        completer = qt.QCompleter()
        model = qt.QFileSystemModel(completer)
        model.setOption(qt.QFileSystemModel.Option.DontWatchForChanges, True)
        model.setRootPath(qt.QDir.rootPath())

        completer.setModel(model)
        completer.setCompletionRole(qt.QFileSystemModel.Roles.FileNameRole)
        self.setCompleter(completer)
        self.installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == qt.QtCore.QEvent.Type.ToolTip and self.text():
            qt.QToolTip.showText(event.globalPos(), self.text(), self)
            return True
        return super().eventFilter(source, event)
