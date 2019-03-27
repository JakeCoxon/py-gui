import copy


class Point():
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def with_x(self, x):
        return Point(x, self.y)

    def with_y(self, y):
        return Point(self.x, y)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x},{self.y})"

    def __iter__(self):
        yield self.x
        yield self.y

    def __hash__(self):
        return hash((self.x, self.y))

    def copy(self):
        return copy.deepcopy(self)

