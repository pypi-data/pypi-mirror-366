import pytest
import numpy as np
from extra_redu import errb_round


def test_abs_rounding():
    a = np.arange(-256., 256.125, 0.125, dtype=np.float32)
    c = np.round(a)

    b = errb_round(a, abspw=0)
    np.testing.assert_array_equal(b, c)


def test_rel_rounding():
    a = np.arange(0, 65520, dtype=np.float32)
    c = a.astype(np.float16).astype(np.float32)

    b = errb_round(a, mnbits=10)
    np.testing.assert_array_equal(b, c)


def test_all_rounding():
    a = np.arange(0, 16384, 0.0625, dtype=np.float32)
    c = a.astype(np.float16).astype(np.float32)
    k = (c != np.round(c))
    c[k] = np.round(a[k]).astype(np.float16).astype(np.float32)

    b = errb_round(a, 10, 0)
    np.testing.assert_array_equal(b, c)


def test_3d_array_rounding():
    a = np.linspace(0, 5000, 262144, dtype=np.float32).reshape(64, 64, 64)
    c = np.round(a)

    b = errb_round(a, 23, 0)
    assert b.shape == a.shape
    np.testing.assert_array_equal(b, c)

    b[:] = 0
    errb_round(a, 23, 0, out=b)
    assert b.shape == a.shape
    np.testing.assert_array_equal(b, c)

    b = np.zeros([60, 64, 64], dtype=np.float32)
    errmsg = 'Input and output arrays have different shape'
    with pytest.raises(ValueError, match=errmsg):
        errb_round(a, 23, 0, out=b)


def test_array_views_rounding():
    a = np.linspace(0, 5000, 262144, dtype=np.float32).reshape(64, 64, 64)
    s = a[5:60:3, :, :]
    c = np.round(s)

    b = errb_round(s, 23, 0)
    assert b.shape == s.shape
    np.testing.assert_array_equal(b, c)

    b[:] = 0
    errb_round(s, 23, 0, out=b)
    assert b.shape == s.shape
    np.testing.assert_array_equal(b, c)

    b = np.zeros([64, 64, 64], dtype=np.float32)
    errb_round(s, 23, 0, out=b[5:60:3, :, :])
    np.testing.assert_array_equal(b[5:60:3, :, :], c)
