from __future__ import annotations

import logging
from typing import Any, Callable

from ewoksorange.bindings import OWEwoksWidgetOneThread
from ewoksorange.bindings.owwidgets import ow_build_opts
from silx.gui import qt

from .utils import format_exception

_logger = logging.getLogger(__name__)


class Ewoks3DXRDWidget(OWEwoksWidgetOneThread, **ow_build_opts):
    want_main_area = True
    want_control_area = False
    resizing_enabled = True

    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)

        self._splitter = qt.QSplitter(qt.Qt.Orientation.Horizontal)
        self._splitter.setSizes([300, 700])
        self.mainArea.layout().addWidget(self._splitter)
        self._input_getters: dict[str, Callable[..., Any]] = {}
        self._input_setters: dict[str, Callable[[Any], None]] = {}

    def registerInput(
        self, name: str, getter: Callable[..., Any], setter: Callable[[Any], None]
    ):
        """Registers an input so its value can be restored at start-up and used at execution"""
        self._input_getters[name] = getter
        self._input_setters[name] = setter

    def _restoreDefaultInputs(self):
        for name, setter in self._input_setters.items():
            try:
                value = self.get_default_input_value(name)
                if value is not None:
                    setter(value)
            except Exception as error:
                _logger.warning(
                    f"Default input restoration failed for {type(self)}.{name}. Cause: {format_exception(error)}"
                )
                self.set_default_input(name, None)
                _logger.warning(f"Default input of {type(self)}.{name} was cleared.")

    def addControlWidget(self, widget: qt.QWidget):
        self._splitter.insertWidget(0, widget)

    def addMainWidget(self, widget: qt.QWidget):
        self._splitter.insertWidget(1, widget)

    def execute_ewoks_task(self, log_missing_inputs=False):
        self._disableControls()
        try:
            self.update_default_inputs(
                **{name: getter() for name, getter in self._input_getters.items()}
            )
            super().execute_ewoks_task(log_missing_inputs)
        except Exception as e:
            self.showError(e)
            self._enableControls()

    def task_output_changed(self):
        super().task_output_changed()
        self._enableControls()
        if self.task_exception is not None:
            self.showError(self.task_exception)
            return

        self.handleSuccessfulExecution()

    def handleSuccessfulExecution(self):
        pass

    def showError(self, error: Exception, title: str | None = None):
        qt.QMessageBox.critical(
            self,
            f"{title if title else self.name} Error",
            format_exception(error),
        )

    def _disableControls(self):
        controlWidget = self._splitter.widget(0)
        if controlWidget:
            controlWidget.setDisabled(True)

    def _enableControls(self):
        controlWidget = self._splitter.widget(0)
        if controlWidget:
            controlWidget.setEnabled(True)
            controlWidget.setEnabled(True)
            controlWidget.setEnabled(True)
