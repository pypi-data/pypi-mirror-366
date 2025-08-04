from __future__ import annotations

from ewokscore import missing_data
from silx.gui import qt


class ProcessNameLineEdit(qt.QLineEdit):

    def __init__(self, default: str, parent: qt.QWidget | None = None):
        super().__init__(parent)
        self.setPlaceholderText(default)
        self.label = "Output NeXus Group Name"
        self.setToolTip(
            f"Name of the NeXus group where data will be saved. Default: '{default}'"
        )

    def getText(self) -> str | missing_data.MissingData:
        value = self.text().strip()
        if value == "":
            return missing_data.MISSING_DATA
        return value
