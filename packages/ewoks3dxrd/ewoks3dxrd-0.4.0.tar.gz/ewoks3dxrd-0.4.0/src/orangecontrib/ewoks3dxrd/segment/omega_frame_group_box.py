from __future__ import annotations

import numpy as np
from silx.gui import qt

from .utils import get_omega_array


class OmegaFrameGroupBox(qt.QGroupBox):
    sigFrameIdxReleased = qt.Signal()

    def __init__(self, parent: qt.QWidget | None = None, **kwargs) -> None:
        super().__init__("Omega and Frame Selection", parent=parent, **kwargs)

        self._omega_array: np.ndarray | None = None
        self._frame_idx: int | None = None

        omega_frame_layout = qt.QGridLayout(self)
        self._frame_slider = qt.QSlider(qt.Qt.Horizontal)
        self._frame_index_label = qt.QLabel("Frame: auto")  # Left side
        self._omega_label = qt.QLabel("Omega: auto")
        omega_frame_layout.addWidget(self._frame_index_label)
        omega_frame_layout.addWidget(self._frame_slider)
        omega_frame_layout.addWidget(self._omega_label)

        # https://doc.qt.io/qt-6/qabstractslider.html#tracking-prop
        self._frame_slider.setTracking(False)
        self._frame_slider.valueChanged.connect(self._on_slider_changed)

    def _on_slider_changed(self, slider_val: int):
        if self._omega_array is None:
            return
        self._frame_idx = slider_val
        omega_value = float(self._omega_array[self._frame_idx])

        self._frame_index_label.setText(f"Frame Index: {self._frame_idx}")
        self._omega_label.setText(f"Omega: {omega_value:.2f}°")

        self.sigFrameIdxReleased.emit()

    def setOmegaArray(self, master_file: str, omega_motor: str, scan_id: str):
        self._omega_array = get_omega_array(
            file_path=master_file,
            omega_motor=omega_motor,
            scan_id=scan_id,
        )
        self._frame_slider.setMinimum(0)
        self._frame_slider.setMaximum(len(self._omega_array) - 1)

    def getFrameIdx(self) -> int | None:
        return self._frame_idx
