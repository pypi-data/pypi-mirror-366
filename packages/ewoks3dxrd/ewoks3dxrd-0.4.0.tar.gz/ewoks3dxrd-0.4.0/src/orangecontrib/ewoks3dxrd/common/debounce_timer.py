from __future__ import annotations
from silx.gui import qt


class DebounceTimer(qt.QTimer):
    def __init__(
        self, callback: callable[[], None], timeout_ms: int = 200, parent=None
    ):
        super().__init__(parent)
        self._callback = callback
        self.setSingleShot(True)
        self.setInterval(timeout_ms)
        self.timeout.connect(self._callback)
