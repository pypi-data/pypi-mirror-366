from __future__ import annotations

from typing import Any

from silx.gui import qt

from ewoks3dxrd.models import SegmenterConfig

from ..common.collapsible_widget import CollapsibleWidget
from ..common.debounce_timer import DebounceTimer
from .constants import SEGMENTER_DEFAULTS, SEGMENTER_TOOLTIPS


class SegmenterParamGroupBox(CollapsibleWidget):
    sigParamsChanged = qt.Signal()

    def __init__(self, parent: qt.QWidget | None = None, **kwargs) -> None:
        super().__init__("Segmentation Parameters", parent=parent, **kwargs)
        seg_layout = qt.QFormLayout()
        self._threshold = qt.QLineEdit(str(SEGMENTER_DEFAULTS["threshold"]))
        self._smooth_sigma = qt.QLineEdit(str(SEGMENTER_DEFAULTS["smooth_sigma"]))
        self._bgc = qt.QLineEdit(str(SEGMENTER_DEFAULTS["bgc"]))
        self._min_px = qt.QLineEdit(str(SEGMENTER_DEFAULTS["min_px"]))
        self._offset_threshold = qt.QLineEdit(
            str(SEGMENTER_DEFAULTS["offset_threshold"])
        )
        self._ratio_threshold = qt.QLineEdit(str(SEGMENTER_DEFAULTS["ratio_threshold"]))

        self._threshold.setValidator(qt.QIntValidator())
        self._smooth_sigma.setValidator(qt.QDoubleValidator())
        self._bgc.setValidator(qt.QDoubleValidator())
        self._min_px.setValidator(qt.QIntValidator())
        self._offset_threshold.setValidator(qt.QIntValidator())
        self._ratio_threshold.setValidator(qt.QIntValidator())

        self._threshold.setToolTip(SEGMENTER_TOOLTIPS["threshold"])
        self._smooth_sigma.setToolTip(SEGMENTER_TOOLTIPS["smooth_sigma"])
        self._bgc.setToolTip(SEGMENTER_TOOLTIPS["bgc"])
        self._min_px.setToolTip(SEGMENTER_TOOLTIPS["min_px"])
        self._offset_threshold.setToolTip(SEGMENTER_TOOLTIPS["offset_threshold"])
        self._ratio_threshold.setToolTip(SEGMENTER_TOOLTIPS["ratio_threshold"])

        seg_layout.addRow("Threshold:", self._threshold)
        seg_layout.addRow("Smooth Sigma:", self._smooth_sigma)
        seg_layout.addRow("Background Constant:", self._bgc)
        seg_layout.addRow("Min Pixels:", self._min_px)
        seg_layout.addRow("Offset Threshold:", self._offset_threshold)
        seg_layout.addRow("Ratio Threshold:", self._ratio_threshold)
        self.setLayout(seg_layout)

        self._last_params: dict[str, Any] = {}
        self._debounce_timer = DebounceTimer(
            callback=self._on_param_changed, timeout_ms=200, parent=self
        )

        for widget in [
            self._threshold,
            self._smooth_sigma,
            self._bgc,
            self._min_px,
            self._offset_threshold,
            self._ratio_threshold,
        ]:
            widget.textChanged.connect(self._debounce_timer.start)

    def getConfig(self) -> SegmenterConfig:
        return SegmenterConfig(
            threshold=int(self._threshold.text()),
            smooth_sigma=self._to_locale_float(self._smooth_sigma),
            bgc=self._to_locale_float(self._bgc),
            min_px=int(self._min_px.text()),
            offset_threshold=int(self._offset_threshold.text()),
            ratio_threshold=int(self._ratio_threshold.text()),
        )

    def setConfig(self, config: SegmenterConfig):
        self._threshold.setText(str(config.threshold))
        self._smooth_sigma.setText(str(config.smooth_sigma))
        self._bgc.setText(str(config.bgc))
        self._offset_threshold.setText(str(config.offset_threshold))
        self._ratio_threshold.setText(str(config.ratio_threshold))

    def _to_locale_float(self, text_field: qt.QLineEdit):
        value, ok = self.locale().toFloat(text_field.text())
        if not ok:
            raise ValueError(f"Invalid float input: '{text_field.text()}'")
        return value

    def _on_param_changed(self):
        params = self.getConfig()
        if not params or self._last_params == params:
            return

        self._last_params = params.model_dump()
        self.sigParamsChanged.emit()
