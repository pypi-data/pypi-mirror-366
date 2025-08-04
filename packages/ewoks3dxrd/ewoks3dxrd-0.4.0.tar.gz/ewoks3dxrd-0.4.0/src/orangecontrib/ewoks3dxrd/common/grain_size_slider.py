from silx.gui import qt
from .double_slider import QDoubleSlider


class GrainSizeSlider(QDoubleSlider):
    def __init__(self, orientation=qt.Qt.Orientation.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self.setRange(0.00002, 0.0002)
        self.setFloatValue(0.0001)
