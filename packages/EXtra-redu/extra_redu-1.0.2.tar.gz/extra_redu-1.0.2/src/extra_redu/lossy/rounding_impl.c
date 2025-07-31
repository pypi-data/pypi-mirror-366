#include <stdint.h>

float errb_round_f(float arg, int mnbits, int abspw)
{
    uint32_t s, m, mask, half, odd, up, r;
    int nb, nz, e;
    union {
        float fl;
        uint32_t dw;
    } a;
    
    /* decode float number */
    a.fl = arg;
    /* sign */
    s = a.dw & 0x80000000;
    /* exponent */
    e = (a.dw >> 23) & 0xFFu;
    /* significand */
    m = a.dw & 0x7FFFFFu;
    m = (e == 0) ? (m << 1) : (m | 0x800000u);
    
    /* number of significand bits after rounding */
    nb = (int) e - abspw - 0x7F;
    nb = (nb > mnbits) ? mnbits : nb;
    /* number of non-significant bits to reset minus one */
    nz = 22 - nb;
    
    /* mask to reset non-significant bits */
    mask = 0xFFFFFFFFu << (nz + 1);
    
    /* `r` is a half of last significant digit if one of following: */
    /* (odd) if the remaining number is odd */
    /* (up ) if the discarding remainder is greater than half of the */
    /*       last significant digit */
    /* else zero */
    half = 1u << nz;
    odd = (m & (half << 1)) >> 1;
    up = (uint32_t)((m & ~mask) > half) << nz;
    r = odd | up;

    /* round to the nearest even */
    m = (m + r) & mask;
    /* increase exponent if mantissa of overflowed */
    e += (uint32_t)(m == 0x01000000);
    /* encode float number back */
    a.dw = m ? (s) | (e << 23) | (m & 0x7FFFFF) : 0;
    
    return a.fl;
}

void errb_round_vec(int n, const float *v, int incv, float *r, int incr, int mnbits, int abspw)
{
    int i, ri, vi;
    ri = 0;
    vi = 0;
    for (i = 0; i < n; i++) {
        r[ri] = errb_round_f(v[vi], mnbits, abspw);
        ri += incv;
        vi += incr;
    }
}

#define MAX_DIM 32

void errb_round_arr(int ndim, int *n, const float *v, const int *incv, 
                    float *r, const int *incr, int mnbits, int abspw)
{
    int i[MAX_DIM], rii[MAX_DIM], vii[MAX_DIM];
    int dim;
    
    for (dim = 0; dim < ndim; dim++)
        i[dim] = rii[dim] = vii[dim] = 0;
    
    rii[0] = -incr[0];
    vii[0] = -incv[0];
    dim = 0;
    while (dim < ndim) {
        rii[dim] += incr[dim];
        vii[dim] += incv[dim];
        /* copy offset of outer axis to inner axes */
        while (dim > 0) {
            rii[dim-1] = rii[dim];
            vii[dim-1] = vii[dim];
            dim--;
        }

        /* round element */
        r[rii[0]] = errb_round_f(v[vii[0]], mnbits, abspw);

        /* increment index */
        dim = 0;
        i[dim]++;
        while (dim < ndim && i[dim] >= n[dim]) {
            i[dim] = rii[dim] = vii[dim] = 0;
            dim++;
            i[dim]++;
        }
    }
}
