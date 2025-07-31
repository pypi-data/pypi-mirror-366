import numpy as np


def test_litpx_counter(litpx_counter, spi_data, mask):
    goodpx = mask == 0
    np.testing.assert_array_equal(
        litpx_counter.num_lit_px,
        np.sum(spi_data > 0.7, axis=(-2, -1), initial=0, where=goodpx)
    )
    np.testing.assert_array_equal(
        litpx_counter.total_intensity,
        np.sum(spi_data, axis=(-2, -1), initial=0, where=goodpx).astype(int)
    )
    np.testing.assert_array_equal(
        litpx_counter.num_unmasked_px, np.sum(goodpx, axis=(-1, -2))
    )
