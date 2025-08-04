from __future__ import annotations

import numpy as np
from silx.gui import qt
from silx.gui.colors import Colormap
from silx.io.utils import DataUrl

from ewoks3dxrd.nexus.peaks import read_peaks_attributes
from ewoks3dxrd.tasks.detector_spatial_correction import DetectorSpatialCorrection

from .common.ewoks3dxrd_plot2d import Ewoks3DXRDPlot2D
from .common.ewoks3dxrd_widget import Ewoks3DXRDWidget
from .detector.detector_correction_settings import DetectorCorrectionSettings


class OWDetectorCorrection(Ewoks3DXRDWidget, ewokstaskclass=DetectorSpatialCorrection):
    name = "Detector Correction"
    description = "Correct spatial deformed detector into plane"
    icon = "icons/distortion_plane.svg"

    _ewoks_inputs_to_hide_from_orange = (
        "overwrite",
        "correction_files",
    )

    def __init__(self):
        super().__init__()

        settings_panel_widget = qt.QWidget(self)
        setting_layout = qt.QVBoxLayout(settings_panel_widget)
        self._settings_widget = DetectorCorrectionSettings()

        action_layout = qt.QFormLayout()
        self._segmenter_url = qt.QLineEdit()
        self._overwrite = qt.QCheckBox("Overwrite")
        execute_btn = qt.QPushButton("Execute Detector Correction")
        execute_btn.clicked.connect(self.execute_ewoks_task)
        action_layout.addRow("Segmented URL", self._segmenter_url)
        self._segmenter_url.textChanged.connect(self._drawInputSegmentedPeaks)
        action_layout.addWidget(self._overwrite)
        action_layout.addWidget(execute_btn)

        setting_layout.addWidget(self._settings_widget, stretch=1)
        setting_layout.addLayout(action_layout)
        self.addControlWidget(settings_panel_widget)

        self._plot = Ewoks3DXRDPlot2D(self)
        self._plot.getColorBarWidget().setVisible(False)
        self.addMainWidget(self._plot)
        self.registerInput(
            "segmented_peaks_url", self._validateInputs, self._segmenter_url.setText
        )
        self.registerInput(
            "correction_files",
            self._settings_widget.getCorrectionFiles,
            self._settings_widget.setCorrectionFiles,
        )
        self.registerInput(
            "overwrite", self._overwrite.isChecked, self._overwrite.setChecked
        )
        self._restoreDefaultInputs()

    def handleNewSignals(self):
        segmented_peaks_url = self.get_task_input_value("segmented_peaks_url", None)
        if segmented_peaks_url is not None:
            self._segmenter_url.setText(segmented_peaks_url)
            self._drawInputSegmentedPeaks()

    def _drawInputSegmentedPeaks(self):
        data_url = DataUrl(self._segmenter_url.text().strip())
        nexus_file_path = data_url.file_path()
        segmented_data_group_path = data_url.data_path()

        segmented_3d_peaks = read_peaks_attributes(
            filename=nexus_file_path,
            process_group=segmented_data_group_path,
        )
        scatter = self._plot.addScatter(
            x=segmented_3d_peaks["f_raw"],
            y=segmented_3d_peaks["s_raw"],
            value=np.ones(len(segmented_3d_peaks["f_raw"])),
            colormap=Colormap(
                colors=np.array(
                    [
                        [0.0, 0.0, 1.0],
                    ],
                    dtype=np.float32,
                )
            ),
            symbol="o",
            legend="rawPixels",
        )
        scatter.setSymbolSize(7)
        self._plot.setGraphXLabel("fast column")
        self._plot.setGraphYLabel("slow column")
        self._plot.setGraphTitle("Raw Pixels O (blue)")
        self._plot.resetZoom()

    def handleSuccessfulExecution(self):
        data_url = DataUrl(self.get_task_output_value("spatial_corrected_data_url"))
        nexus_file_path = data_url.file_path()
        detector_data_group_path = data_url.data_path()

        det_corrected_3d_peaks = read_peaks_attributes(
            filename=nexus_file_path,
            process_group=detector_data_group_path,
        )
        scatter = self._plot.addScatter(
            x=det_corrected_3d_peaks["fc"],
            y=det_corrected_3d_peaks["sc"],
            value=np.ones(len(det_corrected_3d_peaks["fc"])),
            colormap=Colormap(
                colors=np.array(
                    [
                        [1.0, 0.0, 0.0],
                    ],
                    dtype=np.float32,
                )
            ),
            symbol="+",
            legend="corrected Pixels",
        )
        scatter.setSymbolSize(7)
        self._plot.setGraphTitle("Raw Pixels O  (blue) vs Corrected Pixels + (red)")
        self._plot.resetZoom()

    def _validateInputs(self) -> str:
        input_url = self._segmenter_url.text().strip()
        if not input_url:
            raise ValueError("No segmenter data URL to process.")
        return input_url
