from typing import Any, Iterable, Type

from silx.gui import qt


class TupleInputWidget(qt.QWidget):
    def __init__(
        self,
        placeHolderText: str = "Enter tuple, e.g. 0, 1, 2",
        Type: Type = int,
        parent: qt.QWidget | None = None,
    ):
        super().__init__(parent)

        self._tupleEdit = qt.QLineEdit()
        self._tupleEdit.setPlaceholderText(placeHolderText)

        layout = qt.QVBoxLayout(self)
        layout.addWidget(self._tupleEdit)
        layout.setContentsMargins(0, 0, 0, 0)

        self._type = Type
        self._tupleEdit.editingFinished.connect(self._validate)

    def _validate(self):
        try:
            _ = self.getValue()
            self._tupleEdit.setStyleSheet("")
        except Exception:
            self._tupleEdit.setStyleSheet("border: 1px solid red")

    def getValue(self) -> tuple:
        text = self._tupleEdit.text().strip()

        if not text:
            return tuple()

        try:
            return tuple(self._type(part) for part in text.split(",") if part.strip())
        except ValueError as e:
            raise ValueError(f"Input must be a tuple of {self._type.__name__}") from e

    def setValue(self, values: Iterable[Any]):
        self._tupleEdit.setText(",".join(str(value) for value in values))
