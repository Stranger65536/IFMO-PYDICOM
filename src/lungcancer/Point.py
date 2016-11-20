class Point:
    def __init__(self, x, y):
        self._x = x
        self._y = y

    def __repr__(self):
        return "".join(["Point(", str(self._x), ",", str(self._y), ")"])

    def x(self):
        return self._x

    def y(self):
        return self._y
