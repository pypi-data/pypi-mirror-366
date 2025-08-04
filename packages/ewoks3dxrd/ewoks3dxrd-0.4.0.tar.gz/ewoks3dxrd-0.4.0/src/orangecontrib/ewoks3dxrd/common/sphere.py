from __future__ import annotations
import numpy as np
from silx.gui.plot3d.items.core import ItemChangedType
from silx.gui.plot3d.items import DataItem3D, ColormapMixIn
from silx.gui.plot3d.scene import primitives
from silx.io.url import DataUrl
from ewoks3dxrd.nexus.grains import read_grains
from ewoks3dxrd.nexus.utils import group_exists


class Spheres(DataItem3D, ColormapMixIn):

    def __init__(self, positions=None, radii=None, values=None, parent=None):
        DataItem3D.__init__(self, parent=parent)
        ColormapMixIn.__init__(self)
        self._colorVal = values
        self._radiiNorm = 0.0001
        if positions is None:
            positions = np.zeros((0, 3), dtype=np.float32)
        if radii is None:
            radii = np.zeros((0, 1), dtype=np.float32)
        self._sphere = primitives.Spheres(positions, self._radiiNorm * radii)
        self._getScenePrimitive().children.append(self._sphere)
        self._colormapChanged()

    def _colormapChanged(self):
        super()._colormapChanged()
        self.setValues(self._colorVal, copy=False)

    def setRadii(self, radii: np.array):
        position = self._sphere.getAttribute(name="position", copy=False)
        if len(position) != len(radii):
            raise ValueError("Shape mismatch")
        self._sphere.setAttribute(name="radius", array=self._radiiNorm * radii)

    def setPosition(self, newPosition: np.array):
        oldPosition = self._sphere.getAttribute(name="position", copy=False)
        if newPosition.size != oldPosition.size:
            raise ValueError("Shape mismatch")
        self._sphere.setAttribute(name="position", array=newPosition)

    def setValues(self, values: np.array, copy: bool = True):
        self._colorVal = values
        if self._colorVal is None:
            self._sphere.setAttribute(name="color", array=(1.0, 1.0, 1.0, 1.0))
            return

        colors = self.getColormap().applyToData(self._colorVal) / 255
        self._sphere.setAttribute(name="color", array=colors, copy=True)

    def setRadiiNorm(self, radiiNorm: float):
        radii = self._sphere.getAttribute(name="radius") / self._radiiNorm
        self._radiiNorm = radiiNorm
        self.setRadii(radii=radii)

    def setData(self, positions: np.array, radii: np.array, values: np.array):
        self._sphere.setAttribute(name="position", array=positions)
        self._sphere.setAttribute(name="radius", array=self._radiiNorm * radii)
        self._colorVal = values
        colors = self.getColormap().applyToData(self._colorVal) / 255
        self._sphere.setAttribute(name="color", array=colors)
        self._updated(ItemChangedType.DATA)


def build_grain_spheres(grain_url: str, sphere_scale: float = 0.0001) -> Spheres:
    data_url = DataUrl(grain_url)
    group_exists(filename=data_url.file_path(), data_group_path=data_url.data_path())
    grains = read_grains(
        grain_file_h5=data_url.file_path(),
        entry_name=data_url.data_path(),
        process_group_name="",
    )

    position = np.transpose(np.array([grain.translation for grain in grains])).reshape(
        -1, 3
    )

    sphere = Spheres(
        positions=position,
        radii=np.array([float(grain.mean_intensity) for grain in grains]),
        values=np.array([float(grain.npks) for grain in grains]),
    )
    sphere.setRadiiNorm(radiiNorm=sphere_scale)
    return sphere
