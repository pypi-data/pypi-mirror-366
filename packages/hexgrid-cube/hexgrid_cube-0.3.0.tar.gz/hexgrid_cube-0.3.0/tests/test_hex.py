import pytest
from hexgrid_cube.hex import Hex


@pytest.fixture
def h():
    return Hex(1, 1)


@pytest.fixture
def origin():
    return Hex(0, 0)


@pytest.fixture
def lerp_target():
    return Hex(10, 10)


class TestHex:

    def test_raises_if_args_sum_not_zero(self):
        with pytest.raises(ValueError):
            Hex(-1, -1, -1)

    def test_coordinates_positional_order_is_q_r_s(self, h):
        assert h.q == 1 and h.r == 1 and h.s == -2

    def test_sets_s_coordinate_if_omitted(self, h):
        assert h.s == -2

    def test_str_conversion(self, h):
        assert str(h) == "q: 1, r: 1, s: -2"

    def test_repr(self, h):
        assert repr(h) == "1, 1, -2"

    def test_hashing(self, h):
        assert hash(h) == hash((1, 1, -2))

    def test_equality(self, h):
        assert h == Hex(1, 1)

    def test_equality_fails_if_all_different_coordinates(self, h, origin):
        assert not h == origin

    def test_equality_fails_if_two_different_coordinates(self, h):
        assert not h == Hex(1, 0)

    def test_equality_raises_if_compared_to_non_hex(self, h):
        with pytest.raises(ValueError):
            assert h == (1, 1, -2)

    def test_addition(self, h):
        h2 = Hex(-1, -1)
        assert h + h2 == Hex(0, 0)

    def test_subtraction(self, h):
        h2 = Hex(1, 1)
        assert h - h2 == Hex(0, 0)

    def test_addition_crashes_if_operand_non_hex(self, h):
        with pytest.raises(ValueError):
            h + (-1, -1, 2)

    def test_subtraction_raises_if_operand_non_hex(self, h):
        with pytest.raises(ValueError):
            h - (1, 1, -2)

    def test_multiplication(self, h):
        assert h * 2 == Hex(2, 2, -4)

    def test_multiplication_raises_if_operand_non_int(self, h):
        with pytest.raises(ValueError):
            h * h

    def test_and_not_origin_is_true(self, h):
        assert h & h

    def test_and_origin_is_false(self, h, origin):
        assert not h & origin

    def test_and_raises_if_operand_non_hex(self, h):
        with pytest.raises(ValueError):
            h & 1

    def test_or_one_origin_is_true(self, h, origin):
        assert h | origin

    def test_or_both_origin_is_false(self, origin):
        assert not origin | origin

    def test_or_raises_if_operand_non_hex(self, h):
        with pytest.raises(ValueError):
            h | 1

    def test_xor_both_true(self, h):
        assert not h ^ h

    def test_xor_both_false(self, origin):
        assert not origin ^ origin

    def test_xor_one_origin(self, h, origin):
        assert h ^ origin

    def test_xor_raises_if_operand_non_hex(self, h):
        with pytest.raises(ValueError):
            h ^ 1

    def test_neg(self, h):
        assert -h == Hex(-1, -1)

    def test_pos(self, h):
        assert +h == h

    def test_abs_s_neg(self, h):
        assert abs(h) == (1, 1, 2)

    def test_abs_s_only_pos(self):
        h = Hex(-1, -1)
        assert abs(h) == (1, 1, 2)

    def test_length(self, h):
        assert h.length() == 2

    def test_length_origin(self, origin):
        assert origin.length() == 0

    def test_distance_identical_hexes_null(self, h):
        assert h.distance(h) == 0

    def test_distance_origin_is_length(self, h, origin):
        assert h.distance(origin) == h.length()

    def test_distance(self, h):
        assert h.distance(-h) == 4

    def test_ring(self, h):
        assert h.ring(1) == [Hex(1, 2), Hex(2, 1), Hex(1, 0),
                             Hex(2, 0), Hex(0, 1), Hex(0, 2)]

    def test_ring_crash_if_radius_not_positive(self, h):
        with pytest.raises(ValueError):
            h.ring(0)
        with pytest.raises(ValueError):
            h.ring(-1)


class TestHexFromTuple:

    def test_raises_if_tuple_sum_not_zero(self):
        with pytest.raises(ValueError):
            Hex.from_tuple((-1, -1, -1))

    def test_coordinates_positional_order_is_q_r_s(self):
        h = Hex.from_tuple((1, 2, -3))
        assert h.q == 1 and h.r == 2 and h.s == -3

    def test_s_coordinate_set_if_omitted(self):
        h = Hex.from_tuple((1, 1))
        assert h.s == -2

    def test_raises_if_len_is_1(self):
        with pytest.raises(ValueError):
            Hex.from_tuple((1,))

    def test_raises_if_len_gt_3(self):
        with pytest.raises(ValueError):
            Hex.from_tuple((1, 2, -3, 4))


class TestDirections:

    def test_dir_zero(self, origin):
        assert origin.direction(0) == Hex(1, 0)

    def test_dir_one(self, origin):
        assert origin.direction(1) == Hex(0, 1)

    def test_dir_two(self, origin):
        assert origin.direction(2) == Hex(-1, 1)

    def test_dir_three(self, origin):
        assert origin.direction(3) == Hex(-1, 0)

    def test_dir_four(self, origin):
        assert origin.direction(4) == Hex(0, -1)

    def test_dir_five(self, origin):
        assert origin.direction(5) == Hex(1, -1)

    def test_dir_six(self, origin):
        assert origin.direction(6) == Hex(1, 0)

    def test_dir_minus_one(self, origin):
        assert origin.direction(-1) == origin.direction(5)


class TestNeighbours:

    def test_neighbour_origin_is_direction(self, origin):
        for direction in range(6):
            assert origin.neighbour(direction) == origin.direction(direction)

    def test_neighbour_zero(self, h):
        assert h.neighbour(0) == Hex(2, 1)

    def test_neighbour_one(self, h):
        assert h.neighbour(1) == Hex(1, 2)

    def test_neighbour_two(self, h):
        assert h.neighbour(2) == Hex(0, 2)

    def test_neighbour_three(self, h):
        assert h.neighbour(3) == Hex(0, 1)

    def test_neighbour_four(self, h):
        assert h.neighbour(4) == Hex(1, 0)

    def test_neighbour_five(self, h):
        assert h.neighbour(5) == Hex(2, 0)

    def test_neighbours(self, h):
        assert [Hex(2, 1), Hex(1, 2), Hex(0, 2),
                Hex(0, 1), Hex(1, 0), Hex(2, 0)] == h.neighbours()


class TestFractionalHex:

    def test_exact_floats(self, h):
        assert Hex.fractional_hex(1.0, 1.0, -2.0) == h

    def test_almost_integers(self, h):
        assert Hex.fractional_hex(1.000000001, 1.000000001, -2.000000002) == h

    def test_sum_almost_null(self, h):
        assert Hex.fractional_hex(.99, .99, -2.0)

    def test_decimal_approximation(self, h):
        assert Hex.fractional_hex(.9, .9, -1.8) == h

    def test_q_most_off(self, h):
        assert Hex.fractional_hex(0.5, 1.0, -2.0) == h

    def test_r_most_off(self, h):
        assert Hex.fractional_hex(1.0, 0.5, -2.0) == h

    def test_s_most_off(self, h):
        assert Hex.fractional_hex(1.0, 1.0, 2.0) == h

    def test_s_change_if_all_equals(self, h):
        assert Hex.fractional_hex(1.0, 1.0, 1.0) == h

    def test_division(self, h):
        h2 = Hex(2, 2)
        assert h2 / 2 == h

    def test_division_raises_if_operand_non_int(self, h):
        with pytest.raises(ValueError):
            h / h

    def test_hex_lerp_midpoint(self, origin, lerp_target):
        assert origin.hex_lerp(lerp_target, .5) == Hex(5, 5)

    def test_hex_lerp_t_zero_returns_self(self, origin, lerp_target):
        assert origin.hex_lerp(lerp_target, 0) == origin

    def test_hex_lerp_t_one_returns_lerp_target(self, origin, lerp_target):
        assert origin.hex_lerp(lerp_target, 1) == lerp_target

    def test_hex_lerp_steps(self, origin):
        lerp_target = Hex(10, 0)
        for step in range(11):
            assert origin.hex_lerp(lerp_target, step / origin.distance(lerp_target)) == Hex(step, 0)

    def test_hex_lerp_rounds_to_closest_hex(self):
        origin = Hex(0, -10)
        target = Hex(1, 9)
        assert origin.hex_lerp(target, 1 / origin.distance(target)) == Hex(0, -9)

    def test_draw_line(self, origin):
        target = Hex(10, 0)
        assert origin.draw_line(target) == [Hex(_, 0) for _ in range(10)]
