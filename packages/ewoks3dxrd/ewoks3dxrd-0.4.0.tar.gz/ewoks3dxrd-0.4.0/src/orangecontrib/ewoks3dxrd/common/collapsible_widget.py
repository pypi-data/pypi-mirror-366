from __future__ import annotations

from silx.gui import qt


class CollapsibleWidget(qt.QWidget):

    def __init__(self, title: str = "", parent: qt.QWidget | None = None) -> None:
        super().__init__(parent=parent)
        layout = qt.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._toolButton = qt.QToolButton()
        self._toolButton.setSizePolicy(
            qt.QSizePolicy.Policy.Expanding, qt.QSizePolicy.Policy.Fixed
        )
        self._toolButton.setText(title)
        self._toolButton.setToolButtonStyle(
            qt.Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        )
        self._toolButton.setCheckable(True)
        self._toolButton.toggled.connect(self._toggleIcon)
        self._toolButton.setChecked(True)
        layout.addWidget(self._toolButton)

        self._contentsFrame = qt.QGroupBox()
        layout.addWidget(self._contentsFrame)
        self._toolButton.toggled.connect(self._contentsFrame.setVisible)

    def setLayout(self, layout: qt.QLayout | None) -> None:
        self._contentsFrame.setLayout(layout)

    def _toggleIcon(self, toggled: bool) -> None:
        self._toolButton.setArrowType(
            qt.Qt.ArrowType.DownArrow if toggled else qt.Qt.ArrowType.RightArrow
        )

    def isCollapsed(self) -> bool:
        return not self._toolButton.isChecked()

    def setCollapsed(self, collapsed: bool):
        self._toolButton.setChecked(not collapsed)
