import cython

import numpy as np
cimport numpy as np

from . cimport crounding

ctypedef np.float32_t float_t


@cython.boundscheck(False)
@cython.wraparound(False)
def errb_round(object inp, int mnbits=23, int abspw=-150, object out=None):
    """
    Round values in array up to absolute and relative precision.

    This function rounds elements of arrays up to relative and absolute precision.
    Relative precision defined as the number of significant mantissa bits given by
    the `mnbits` parameter. Absolute precision defined as the difference between
    two consecutive representative numbers and given as the power of two by the
    parameter `abspw`.

    :param inp:     An input array of single precision numbers
    :param mnbits:  The number of significant mantissa bits
    :param abspw:   The absolute precision given as the power of two,
                    actual precision is 2**abspw, e.g. 2**(-1) = 0.5
    :param out:     An output array with the same shape as the input array

    :return out:    An output array with rounded numbers
    """
    if inp.dtype != np.float32:
        raise ValueError(f"Input buffer invalid dtype, expected 'float32' but got '{inp.dtype}'")

    cdef int ndim = inp.ndim

    if out is None:
        out = np.zeros(inp.shape, np.float32)
    else:
        if out.dtype != np.float32:
            raise ValueError(f"Output buffer invalid dtype, expected 'float32' but got '{out.dtype}'")
        
    cdef np.ndarray inpbuf = inp
    cdef np.ndarray outbuf = out
    
    cdef float* a = <float *> inpbuf.data
    cdef float* r = <float *> outbuf.data
    
    cdef int n[32], inca[32], incr[32]
    cdef int dim
    
    cdef bint shape_mismatch = False
    for dim in range(ndim):
        n[dim] = inpbuf.shape[dim]
        shape_mismatch = shape_mismatch or (inpbuf.shape[dim] != outbuf.shape[dim])
        inca[dim] = inpbuf.strides[dim] / inpbuf.itemsize
        incr[dim] = outbuf.strides[dim] / outbuf.itemsize

    if shape_mismatch:
        raise ValueError("Input and output arrays have different shape")
        
    crounding.errb_round_arr(ndim, n, a, inca, r, incr, mnbits, abspw)
    return out


def errb_round_flat(np.ndarray inp, int mnbits=23, int abspw=-150, np.ndarray out=None):
    """
    Round values in array up to absolute and relative precision.

    This function rounds elements of arrays up to relative and absolute precision.
    Relative precision defined as the number of significant mantissa bits given by
    the `mnbits` parameter. Absolute precision defined as the difference between
    two consecutive representative numbers and given as the power of two by the
    parameter `abspw`.
    
    This version flattens arrays and can copy the buffer therefore.
    Do not specify sliced views to avoid it.

    :param inp:     An input array of single precision numbers
    :param mnbits:  The number of significant mantissa bits
    :param abspw:   The absolute precision given as the power of two,
                    actual precision is 2**abspw, e.g. 2**(-1) = 0.5
    :param out:     An output array with the same shape as the input array

    :return out:    An output array with rounded numbers
    """
    if inp.dtype != np.float32:
        raise ValueError(f"Buffer dtype mismatch, expected 'float32' but got '{inp.dtype}'")

    shape = (<object> inp).shape
    inp_view = inp.ravel()

    if out is None:
        if inp_view.flags['OWNDATA']:
            # `inp_view` is a copy, we may use it as output buffer
            out = inp_view.reshape(shape)
            out_view = inp_view
        else:
            # else allocate a new buffer
            out = np.zeros_like(inp)
            out_view = out.ravel()
    else:
        if inp.size != out.size:
            raise ValueError("Input and output arrays have different size")

        out_view = out.ravel()
        # Make sure we are still writing to the user's buffer
        if out_view.flags['OWNDATA']:
            raise ValueError("Output buffer cannot be flattened without copying")

    cdef float[:] a = inp_view
    cdef float[:] r = out_view

    cdef int inca = a.strides[0] // a.itemsize
    cdef int incr = r.strides[0] // r.itemsize

    crounding.errb_round_vec(a.size, &a[0], inca, &r[0], incr, mnbits, abspw)
    return out
