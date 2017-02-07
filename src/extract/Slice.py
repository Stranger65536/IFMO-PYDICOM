# coding=utf-8
from uuid import uuid4

from matplotlib.path import Path
from numpy import array
from numpy import mgrid
from numpy import vstack


def area(points):
    # return self._area if self._area else

    xc = array([point.x for point in points])
    yc = array([point.y for point in points])

    nr, nc = yc.max() - yc.min() + 1, xc.max() - xc.min() + 1

    xc -= xc.min()
    yc -= yc.min()

    xy_crop = vstack((xc, yc)).T

    y_grid, x_grid = mgrid[:nr, :nc]
    xy_pix = vstack((x_grid.ravel(), y_grid.ravel())).T
    pth = Path(xy_crop, closed=True)

    return int(sum(pth.contains_points(xy_pix, radius=-1)))


class Slice(object):
    def __init__(self, image_uid, z_pos, points):
        self._image_uid = image_uid
        self._z_pos = float(z_pos)
        self._area = area(points)
        self._uid = uuid4().hex
        self._points = tuple(points)

    @property
    def image_uid(self):
        return self._image_uid

    @property
    def z_pos(self):
        return self._z_pos

    @property
    def area(self):
        return self._area

    @property
    def uid(self):
        return self._uid

    @property
    def points(self):
        return self._points

    def __eq__(self, other):
        if not isinstance(other, Slice):
            return False

        return \
            self.image_uid == other.image_uid and \
            self.z_pos == other.z_pos and \
            self.points == other.points

    def __hash__(self, *args, **kwargs):
        return hash((self._image_uid,
                     self._z_pos,
                     self._points))

    def __repr__(self, *args, **kwargs):
        return ''.join(['Slice(',
                        str(self._image_uid), ',',
                        str(self._z_pos), ',',
                        str(self._area), ',',
                        str(self._uid), ',',
                        str(self._points), ')'])

    def __str__(self, *args, **kwargs):
        return self.__repr__(*args, **kwargs)
