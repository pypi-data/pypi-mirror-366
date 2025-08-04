import numpy as np
import pytest

from qdyn.pulse import (
    gaussian,
    box,
    blackman,
    flattop,
    zero_shape,
    one_shape,
    rabi_pulse,
)

TLIST = np.linspace(0, 10, 21)

# fmt: off
CHECKS = [
    (
        #   func  t_array args   kwargs
        gaussian, TLIST, (5, 2), {},
        # tuples of values (t, ϵ(t)) to check
        [(5, 1)]
    ),
    (
        box, TLIST, (1, 9), {},
        [(0, 0), (0.5, 0), (1, 1), (2, 1), (9, 1), (9.5, 0)]
    ),
    (
        blackman, TLIST, (1, 9), {},
        [(0, 0), (1, 0), (5, 1), (9, 0), (10, 0)]
    ),
    (
        flattop, TLIST, (1, 9), dict(t_rise=1, func='blackman'),
        [(0, 0), (1, 0), (2, 1), (5, 1), (8, 1), (9, 0), (10, 0)]
    ),
    (
        flattop, TLIST, (1, 9), dict(t_rise=1, func='sinsq'),
        [(0, 0), (1, 0), (2, 1), (5, 1), (8, 1), (9, 0), (10, 0)]
    ),
    (
        zero_shape, TLIST, (), {},
        [(0, 0), (1, 0), (10, 0)]
    ),
    (
        one_shape, TLIST, (), {},
        [(0, 1), (1, 1), (10, 1)]
    ),
    (
        rabi_pulse, TLIST, (1, 9), dict(shape='blackman'),
        [(0, 0), (1, 0), (5, lambda v: v > 0), (9, 0), (10, 0)]
    ),
    (
        rabi_pulse, TLIST, (1, 9), dict(t_rise=1, shape='flattop_blackman'),
        [(0, 0), (1, 0), (5, lambda v: v > 0), (9, 0), (10, 0)]
    ),
    (
        rabi_pulse, TLIST, (1, 9), dict(shape='box'),
        [(0, 0), (5, lambda v: v > 0), (10, 0)]
    ),
]
# fmt: off

LIMIT = 1e-14


@pytest.mark.parametrize("func,t_array,args,kwargs,check_vals", CHECKS)
def test_shape_evaluation(func, t_array, args, kwargs, check_vals):
    """Check the evaluation of functions on scalars and arrays."""
    f_array = func(t_array, *args, **kwargs)
    f_scalar = np.array([func(t, *args, **kwargs) for t in t_array])

    assert np.max(np.abs(f_array - f_scalar)) < LIMIT

    for (val, expected) in check_vals:
        res = func(val, *args, **kwargs)
        if callable(expected):
            assert expected(res)
        else:
            assert abs(res - expected) < LIMIT
