from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
import qtawesome
from silx.gui import qt
from silx.gui.colors import Colormap
from silx.gui.qt import QSizePolicy
from silx.io.utils import DataUrl

from ewoks3dxrd.io import get_frame_image, get_monitor_scale_factor_for_frame_index
from ewoks3dxrd.nexus.peaks import read_peaks_attributes
from ewoks3dxrd.segment import segment_frame
from ewoks3dxrd.tasks.segment_scan import SegmentScan

from .common.ewoks3dxrd_plot2d import Ewoks3DXRDPlot2D
from .common.ewoks3dxrd_widget import Ewoks3DXRDWidget
from .segment.dual_plot_silx import SilxSyncDualPlot
from .segment.segmenter_settings import SegmenterSettings
from .segment.utils import ask_confirmation_to_repeat_segmentation


class OWFrameSegmenter(Ewoks3DXRDWidget, ewokstaskclass=SegmentScan):
    name = "Peaks Segmentation"
    description = "Runs segmentation on a scan, with preview on a frame."
    icon = "icons/filter_frames.svg"
    _ewoks_inputs_to_hide_from_orange = (
        "overwrite",
        "folder_config",
        "segmenter_algo_params",
        "correction_files",
        "monitor_name",
    )

    def __init__(self):
        super().__init__()

        _settingsPanelWidget = qt.QWidget(self)
        settingLayout = qt.QVBoxLayout(_settingsPanelWidget)

        self._settingsPanel = SegmenterSettings(self)
        self._settingsPanel.sigParametersChanged.connect(self._displayFrame)
        scrollArea = qt.QScrollArea(self)
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(self._settingsPanel)
        settingLayout.addWidget(scrollArea)
        self._settingsPanel.sigParametersChanged.connect(self._displayFrame)

        segmentProgressOverWriteLayout = qt.QFormLayout()
        self._overwriteCheckbox = qt.QCheckBox()
        self._progressBar = qt.QProgressBar()
        self._progressBar.setRange(0, 100)
        self._progressBar.setValue(0)
        segmentProgressOverWriteLayout.addRow(
            "Overwrite Segmentation Result", self._overwriteCheckbox
        )
        segmentProgressOverWriteLayout.addRow(self._progressBar)
        settingLayout.addLayout(segmentProgressOverWriteLayout)

        btnLayout = qt.QHBoxLayout()
        self._executeScanSegmentationBtn = qt.QPushButton("Execute Segment Scan")
        self._executeScanSegmentationBtn.clicked.connect(self._executeEwoksTask)
        self._executeScanSegmentationBtn.setSizePolicy(
            qt.QSizePolicy.Preferred, qt.QSizePolicy.Fixed
        )
        btnLayout.addWidget(self._executeScanSegmentationBtn)
        self._showSegmentationPlotBtn = qt.QPushButton(qtawesome.icon("fa6.eye"), None)
        self._showSegmentationPlotBtn.setFlat(True)
        self._showSegmentationPlotBtn.setToolTip("Show 3D segmented result")
        self._showSegmentationPlotBtn.clicked.connect(self._plotSegmentationOutput)
        self._showSegmentationPlotBtn.setDisabled(True)
        self._showSegmentationPlotBtn.setSizePolicy(
            qt.QSizePolicy.Fixed, qt.QSizePolicy.Preferred
        )
        btnLayout.addWidget(self._showSegmentationPlotBtn)
        settingLayout.addLayout(btnLayout)

        self._lastParams = None

        self._plotWidget = SilxSyncDualPlot(self)
        self._plotWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.addControlWidget(_settingsPanelWidget)
        self.addMainWidget(self._plotWidget)
        self.registerInput(
            "folder_config",
            self._settingsPanel.getFolderConfig,
            self._settingsPanel.setFolderConfig,
        )
        self.registerInput(
            "segmenter_algo_params",
            self._settingsPanel.getSegmenterConfig,
            self._settingsPanel.setSegmenterConfig,
        )
        self.registerInput(
            "correction_files",
            self._settingsPanel.getCorrectionFiles,
            self._settingsPanel.setCorrectionFiles,
        )
        self.registerInput(
            "monitor_name",
            self._settingsPanel.getMonitorName,
            self._settingsPanel.setMonitorName,
        )
        self.registerInput(
            "overwrite",
            self._overwriteCheckbox.isChecked,
            self._overwriteCheckbox.setChecked,
        )
        self._restoreDefaultInputs()

    def _displayFrame(self, params: dict | None):
        if not params:
            return

        raw_image, scale_factor = self._getRawImage(params)
        try:
            smoothed_img, peak_pos = segment_frame(raw_image, params, scale_factor)
        except Exception as e:
            self.showError(e)
            return

        self._plotWidget.setLeftImage(
            array2D=raw_image,
            title=f"Raw Image. {len(peak_pos[0])} peaks found",
            xLabel="f_raw",
            yLabel="s_raw",
        )
        self._plotWidget.setRightImage(
            array2D=smoothed_img,
            title="Background Corrected Image",
            xLabel="f_raw",
            yLabel="s_raw",
        )
        self._plotWidget.setRightScatter(x=peak_pos[0], y=peak_pos[1])

    def _getRawImage(self, params: dict) -> tuple[np.ndarray, float | None]:
        masterfile_path = Path(self._settingsPanel.getMasterFilePath())
        frame_idx = self._settingsPanel.getFrameIdx()
        raw_image = get_frame_image(
            file_path=masterfile_path,
            detector=params["file_folders"]["detector"],
            scan_id=str(self._settingsPanel.getScanNumber()) + ".1",
            frame_idx=frame_idx,
        ).astype("uint16")

        monitor_name = params["monitor_name"]
        if monitor_name is None:
            return raw_image, None

        scale_factor = get_monitor_scale_factor_for_frame_index(
            masterfile_path=masterfile_path,
            scan_number=str(self._settingsPanel.getScanNumber()),
            detector=params["file_folders"]["detector"],
            monitor_name=monitor_name,
            frame_idx=frame_idx,
        )
        return raw_image, scale_factor

    def _getParameters(self) -> dict[str, Any]:
        params = self._settingsPanel.getParameters()
        params = {
            **params,
            "overwrite": self._overwriteCheckbox.isChecked(),
        }
        return params

    def _executeEwoksTask(self):
        try:
            params = self._getParameters()
            if params == self._lastParams:
                decision = ask_confirmation_to_repeat_segmentation()
                if decision == "cancel":
                    return
                elif decision == "show":
                    self._plotSegmentationOutput()
                    return
                elif decision == "continue":
                    pass
                else:
                    raise ValueError(f"Unknown decision {decision}")
        except Exception as e:
            self.showError(e)
            return

        self.execute_ewoks_task()

    def handleSuccessfulExecution(self):
        self._lastParams = self._getParameters()
        self._plotSegmentationOutput()
        self._showSegmentationPlotBtn.setEnabled(True)
        self.progressBarSet(100)

    def _plotSegmentationOutput(self):
        outputs = self.get_task_output_values()
        data_url = DataUrl(outputs["segmented_peaks_url"])
        nexus_file_path = data_url.file_path()
        segmented_data_group_path = data_url.data_path()

        segmented_3d_peaks = read_peaks_attributes(
            filename=nexus_file_path,
            process_group=segmented_data_group_path,
        )
        plot = Ewoks3DXRDPlot2D()
        plot.addScatter(
            x=segmented_3d_peaks["f_raw"],
            y=segmented_3d_peaks["s_raw"],
            value=segmented_3d_peaks["omega"],
            legend="3D Segmented Peaks",
            symbol="x",
            colormap=Colormap(
                name="viridis",
            ),
        )
        plot.setGraphXLabel("f_raw")
        plot.setGraphYLabel("s_raw")
        plot.setGraphTitle("3D Segmented Peaks")
        plot.resetZoom()
        plot.show()

    def progressBarSet(self, value: int):
        self._progressBar.setValue(int(math.ceil(value)))

    def progressBarInit(self):
        self._progressBar.setValue(0)
