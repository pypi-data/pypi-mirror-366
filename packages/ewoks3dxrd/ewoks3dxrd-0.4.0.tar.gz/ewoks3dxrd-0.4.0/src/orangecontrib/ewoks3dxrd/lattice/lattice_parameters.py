from __future__ import annotations

from pathlib import Path
from typing import Any

from silx.gui import qt

from ewoks3dxrd.io import read_lattice_cell_data
from ewoks3dxrd.models import UnitCellParameters

from ..common.collapsible_widget import CollapsibleWidget
from ..common.master_file_widget import MasterFileWidget


class LatticeParameters(qt.QGroupBox):
    sigLatticeParamsChanged = qt.Signal()

    def __init__(
        self,
        title: str = "Lattice Parameter Settings",
        parent: qt.QWidget | None = None,
        **kwargs,
    ) -> None:
        super().__init__(title, parent=parent, **kwargs)
        self._latticeName = None

        layout = qt.QVBoxLayout(self)

        fileLayout = qt.QFormLayout()
        self._latticeParFile = MasterFileWidget(dialogTitle="Lattice Parameter File")
        self._latticeParFile.sigMasterFileChanged.connect(self._onLatticeFileChanged)
        fileLayout.addRow("Lattice File:", self._latticeParFile)
        layout.addLayout(fileLayout)

        editingFieldsBox = CollapsibleWidget("Edit Parameters")
        formLayout = qt.QFormLayout()
        self._aEdit = qt.QDoubleSpinBox()
        self._aEdit.setSuffix(" Å")
        self._aEdit.setRange(0.01, 1000)
        self._aEdit.setValue(1)
        self._aEdit.setDecimals(4)
        formLayout.addRow("a:", self._aEdit)

        self._bEdit = qt.QDoubleSpinBox()
        self._bEdit.setSuffix(" Å")
        self._bEdit.setRange(0.01, 1000)
        self._bEdit.setValue(1)
        self._bEdit.setDecimals(4)
        formLayout.addRow("b:", self._bEdit)

        self._cEdit = qt.QDoubleSpinBox()
        self._cEdit.setSuffix(" Å")
        self._cEdit.setRange(0.01, 1000)
        self._cEdit.setValue(1)
        self._cEdit.setDecimals(4)
        formLayout.addRow("c:", self._cEdit)

        self._alphaEdit = qt.QDoubleSpinBox()
        self._alphaEdit.setSuffix(" °")
        self._alphaEdit.setRange(0, 179.999)
        self._alphaEdit.setValue(90.0)
        formLayout.addRow("α:", self._alphaEdit)

        self._betaEdit = qt.QDoubleSpinBox()
        self._betaEdit.setSuffix(" °")
        self._betaEdit.setRange(0, 179.999)
        self._betaEdit.setValue(90.0)
        formLayout.addRow("β:", self._betaEdit)

        self._gammaEdit = qt.QDoubleSpinBox()
        self._gammaEdit.setSuffix(" °")
        self._gammaEdit.setRange(0, 179.999)
        self._gammaEdit.setValue(90.0)
        formLayout.addRow("γ:", self._gammaEdit)

        self._spaceGroupEdit = qt.QSpinBox()
        self._spaceGroupEdit.setRange(1, 230)
        self._spaceGroupEdit.setValue(229)
        formLayout.addRow("Space Group (#):", self._spaceGroupEdit)

        editingFieldsBox.setCollapsed(True)
        editingFieldsBox.setLayout(formLayout)
        layout.addWidget(editingFieldsBox)
        layout.addStretch(1)

        for widget in [
            self._aEdit,
            self._bEdit,
            self._cEdit,
            self._alphaEdit,
            self._betaEdit,
            self._gammaEdit,
            self._spaceGroupEdit,
        ]:
            widget.valueChanged.connect(self.sigLatticeParamsChanged.emit)

    def _onLatticeFileChanged(self):
        filePath = Path(self._latticeParFile.getText())
        ext = filePath.suffix
        if ext == ".cif" or ext == ".par":
            unit_cell_parameters: UnitCellParameters = read_lattice_cell_data(filePath)
        else:
            qt.QMessageBox.warning(
                self, "Unsupported Format", "Only .cif and .par formats are supported."
            )
            return

        self._latticeName = filePath.stem

        self._aEdit.setValue(unit_cell_parameters.a)
        self._bEdit.setValue(unit_cell_parameters.b)
        self._cEdit.setValue(unit_cell_parameters.c)
        self._alphaEdit.setValue(unit_cell_parameters.alpha)
        self._betaEdit.setValue(unit_cell_parameters.beta)
        self._gammaEdit.setValue(unit_cell_parameters.gamma)
        self._spaceGroupEdit.setValue(int(unit_cell_parameters.space_group))

    def getLatticeParameters(self) -> dict[str, Any]:
        return {
            "lattice_parameters": (
                self._aEdit.value(),
                self._bEdit.value(),
                self._cEdit.value(),
                self._alphaEdit.value(),
                self._betaEdit.value(),
                self._gammaEdit.value(),
            ),
            "lattice_space_group": self._spaceGroupEdit.value(),
            "lattice_name": self._latticeName,
        }

    def setFile(self, value: str):
        self._latticeParFile.setText(value)
