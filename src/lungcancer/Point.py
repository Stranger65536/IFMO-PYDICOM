class Point:
    def __init__(self, x, y):
        self._x = x
        self._y = y

    def x(self):
        return self._x

    def y(self):
        return self._y

    def __eq__(self, other):
        if not isinstance(other, Point):
            return False

        return self._x == other._x and self._y == other._y

    def __hash__(self, *args, **kwargs):
        return hash((self._x, self._y))

    def __repr__(self):
        return "".join(["Point(", str(self._x), ",", str(self._y), ")"])
