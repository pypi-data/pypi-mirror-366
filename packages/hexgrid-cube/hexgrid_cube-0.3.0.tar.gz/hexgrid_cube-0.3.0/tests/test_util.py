import math
from hexgrid_cube.util import lerp


rel_tol = 1e-09
abs_tol = 0.0


class TestLerp:
    def test_lerp_t_is_zero(self):
        assert lerp(10.0, 5.0, 0.0) == 10.0

    def test_lerp_t_is_one(self):
        assert lerp(10.0, 5.0, 1.0) == 5.0

    def test_lerp_t_is_almost_zero(self):
        assert math.isclose(lerp(10.0, 5.0, 0.000000001), 10.0, rel_tol=rel_tol, abs_tol=abs_tol)

    def test_lerp_t_is_almost_one(self):
        assert math.isclose(lerp(10.0, 5.0, 0.9999999999), 5.0, rel_tol=rel_tol, abs_tol=abs_tol)

    def test_lerp_t_is_point_five(self):
        assert lerp(10.0, 5.0, .5) == 7.5

    def test_lerp_t_is_not_representable_exactly_in_binary(self):
        # Python has great floating management and thus isclose is not required here
        assert math.isclose(lerp(10.0, 5.0, .1), 9.5, rel_tol=rel_tol, abs_tol=abs_tol)
