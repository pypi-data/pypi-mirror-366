from hexgrid_cube.point import Point


class TestPoint:
    def test_instantiates(self):
        p = Point(0, 0)
        assert p == (0, 0)

    def test_addition(self):
        p = Point(-2, -2)
        p2 = Point(2, 2)
        res = Point(0, 0)
        assert p.add(p2) == res
