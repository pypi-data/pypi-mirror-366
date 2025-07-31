cdef extern from "rounding.h":
    float errb_round_f(float arg, int mnbits, int abspw)
    void errb_round_vec(int n, const float *v, int incv, float *r, int incr, int mnbits, int abspw)
    void errb_round_arr(int ndim, int *n, const float *v, const int *incv, 
                        float *r, const int *incr, int mnbits, int abspw)
