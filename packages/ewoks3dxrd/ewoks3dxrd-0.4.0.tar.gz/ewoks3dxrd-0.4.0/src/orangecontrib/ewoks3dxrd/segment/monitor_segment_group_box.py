from __future__ import annotations

import numpy as np
from silx.gui import qt
from silx.gui.plot import Plot1D

from ewoks3dxrd.io import get_monitor_data

from ..common.collapsible_widget import CollapsibleWidget
from .constants import MONITOR_KEYS
from .utils import get_unique_instrument_keys


class MonitorSegmentGroupBox(CollapsibleWidget):

    def __init__(self, parent: qt.QWidget | None = None, **kwargs) -> None:
        super().__init__("Monitor Settings", parent=parent, **kwargs)

        monitor_layout = qt.QFormLayout()
        self._monitor_name = qt.QComboBox()
        self._monitor_name.addItem("None")
        self._monitor_name.currentTextChanged.connect(self._toggle_monitor_plot_btn)
        self._monitor_plot_btn = qt.QPushButton("Show Monitor Data")
        self._monitor_plot_btn.clicked.connect(self._on_show_monitor_clicked)
        self._monitor_plot_btn.setDisabled(True)

        monitor_layout.addRow("Monitor:", self._monitor_name)
        monitor_layout.addRow(self._monitor_plot_btn)

        self._scan_number = None
        self.setLayout(monitor_layout)

    def _on_show_monitor_clicked(self):
        current_monitor = self._monitor_name.currentText()
        if current_monitor == "None" or self._scan_number is None:
            return
        y_data = get_monitor_data(
            masterfile_path=self._master_file_path,
            scan_number=self._scan_number,
            monitor_name=current_monitor,
        )
        plot = Plot1D()
        plot.setWindowTitle(f"Monitor Name: {current_monitor}")
        plot.addCurve(range(len(y_data)), y_data, legend=current_monitor)
        plot.resize(800, 600)
        plot.show()

    def fillWidgetValues(self, master_file_path: str, scan_number: str):
        self._scan_number = scan_number
        self._master_file_path = master_file_path
        instrument_keys = get_unique_instrument_keys(
            master_file=master_file_path,
            groups=[self._scan_number + ".1", self._scan_number + ".2"],
        )

        monitor_keys = [
            k for k in instrument_keys if any(k.startswith(m) for m in MONITOR_KEYS)
        ]
        self._monitor_name.clear()
        self._monitor_name.addItem("None")
        for m in monitor_keys:
            monitor_data = get_monitor_data(
                masterfile_path=self._master_file_path,
                scan_number=self._scan_number,
                monitor_name=m,
            )
            if np.any(monitor_data <= 0):
                continue
            else:
                self._monitor_name.addItem(m)

    def getMonitorName(self) -> str | None:
        if self._monitor_name.currentText() == "None":
            return None

        return self._monitor_name.currentText()

    def setMonitorName(self, monitorName: str | None):
        if monitorName is None:
            self._monitor_name.setCurrentText("None")

        self._monitor_name.setCurrentText(monitorName)

    def _toggle_monitor_plot_btn(self, text: str):
        self._monitor_plot_btn.setDisabled(text == "None")
