"""Collection of helpful functions used in the project that fit nowhere else."""


def lerp(a: float, b: float, t: float) -> float:
    """
    Return the linear interpolation between `a` and `b` at step `t` in [0, 1].

    Parameters
    ----------
    a : float
        the first point to interpolate

    b : float
        the second point to interpolate

    t : float
        parameter in [0, 1], interpolation step

    Returns
    -------
    float
        the linear interpolation between `a` and `b` at `t`.
    """
    return a * (1-t) + b*t
