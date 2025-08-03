import pytest
from hexgrid_cube.vector import Vector
from hexgrid_cube.hex import Hex

@pytest.fixture
def h():
    return Hex(1, 1)


@pytest.fixture
def v():
    return Vector(1, 1)


@pytest.fixture
def origin():
    return Vector(0, 0)


class TestVector:

    def test_raises_if_args_sum_not_zero(self):
        with pytest.raises(ValueError):
            Vector(-1, -1, -1)

    def test_coordinates_positional_order_is_q_r_s(self, v):
        assert v.q == 1 and v.r == 1 and v.s == -2

    def test_sets_s_coordinate_if_omitted(self, v):
        assert v.s == -2

    def test_str_conversion(self, v):
        assert str(v) == "q: 1, r: 1, s: -2"

    def test_repr(self, v):
        assert repr(v) == "1, 1, -2"

    def test_hashing(self, v):
        assert hash(v) == hash((1, 1, -2))

    def test_equality(self, v):
        assert v == Vector(1, 1)

    def test_equality_fails_if_all_different_coordinates(self, v, origin):
        assert not v == origin

    def test_equality_fails_if_two_different_coordinates(self, v):
        assert not v == Vector(1, 0)

    def test_equality_raises_if_compared_to_non_hex(self, v):
        with pytest.raises(ValueError):
            assert v == (1, 1, -2)

    def test_addition(self, v):
        h2 = Vector(-1, -1)
        assert v + h2 == Vector(0, 0)

    def test_subtraction(self, v):
        h2 = Vector(1, 1)
        assert v - h2 == Vector(0, 0)

    def test_addition_crashes_if_operand_non_hex(self, v):
        with pytest.raises(ValueError):
            v + (-1, -1, 2)

    def test_subtraction_raises_if_operand_non_vector(self, v):
        with pytest.raises(ValueError):
            v - (1, 1, -2)

    def test_multiplication(self, v):
        assert v * 2 == Vector(2, 2, -4)

    def test_multiplication_raises_if_operand_non_int(self, v):
        with pytest.raises(ValueError):
            v * v

    def test_and_not_origin_is_true(self, v):
        assert v & v

    def test_and_origin_is_false(self, v, origin):
        assert not v & origin

    def test_and_raises_if_operand_non_vector(self, v):
        with pytest.raises(ValueError):
            v & 1

    def test_or_one_origin_is_true(self, v, origin):
        assert v | origin

    def test_or_both_origin_is_false(self, origin):
        assert not origin | origin

    def test_or_raises_if_operand_non_hex(self, v):
        with pytest.raises(ValueError):
            v | 1

    def test_xor_both_true(self, v):
        assert not v ^ v

    def test_xor_both_false(self, origin):
        assert not origin ^ origin

    def test_xor_one_origin(self, v, origin):
        assert v ^ origin

    def test_xor_raises_if_operand_non_hex(self, v):
        with pytest.raises(ValueError):
            v ^ 1

    def test_neg(self, v):
        assert -v == Vector(-1, -1)

    def test_pos(self, v):
        assert +v == v

    def test_abs_s_neg(self, v):
        assert abs(v) == (1, 1, 2)

    def test_abs_s_only_pos(self):
        v = Vector(-1, -1)
        assert abs(v) == (1, 1, 2)

    def test_length(self, v):
        assert v.length() == 2

    def test_length_origin(self, origin):
        assert origin.length() == 0

    def test_div(self, v):
        v2 = Vector(2, 2)
        assert v2 / 2 == v

    def test_dot(self, v):
        v2 = Vector(-1, -1)
        assert v @ v2 == -3

    def test_to_hex_no_start(self, v, h):
        assert v.to_hex() == h

class TestVectorWithStart:
    def test_from_origin(self, v, h):
        assert Vector.from_origin(h) == v

    def test_from_hexes_origin(self, v, h):
        assert Vector.from_hexes(Hex(0, 0), h) == v

    def test_from_hexes(self, v):
        assert Vector.from_hexes(Hex(5, 5), Hex(6, 6)) == v

    def test_to_hex_from_origin(self, h):
        assert Vector.from_origin(h).to_hex() == h

    def test_to_hex(self):
        assert Vector.from_hexes(Hex(5, 5), Hex(6, 6)).to_hex() == Hex(6, 6)


class TestRotation:
    def test_0(self, v):
        assert v.rotate(0) == v.rotate(360) == v

    def test_60(self, v):
        assert v.rotate(60) == v.rotate(-300) == Vector(-1, 2, -1)

    def test_120(self, v):
        assert v.rotate(120)  == v.rotate(-240) == Vector(-2, 1, 1)

    def test_180(self, v):
        assert v.rotate(180) == v.rotate(-180) == Vector(-1, -1, 2)

    def test_240(self, v):
        assert v.rotate(240) == v.rotate(-120) == Vector(1, -2, 1)

    def test_300(self, v):
        assert v.rotate(300) == v.rotate(-60) == Vector(2, -1, -1)

    def test_rotation_raises_if_not_multiple_of_60(self, v):
        with pytest.raises(ValueError):
            v.rotate(90)
