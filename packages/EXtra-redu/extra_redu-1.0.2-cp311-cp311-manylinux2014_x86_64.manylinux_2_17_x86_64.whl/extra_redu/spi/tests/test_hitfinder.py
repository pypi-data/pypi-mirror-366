import numpy as np
from extra_redu.spi import SpiHitfinder


def test_hitfinder_adaptive(litpx_counter, spi_ref, spi_adaptive_threshold):

    np.random.seed(seed=3)
    hitfinder = SpiHitfinder(modules=[3, 4, 8, 15])
    hitfinder.find_hits(litpx_counter)

    assert abs(hitfinder.overall_hitrate - 0.02838709677419355) < 1e-7

    np.testing.assert_array_equal(
        np.flatnonzero(hitfinder.hit_mask), spi_ref.hit_ix)
    np.testing.assert_array_equal(
        np.flatnonzero(hitfinder.miss_mask), spi_ref.miss_ix)
    np.testing.assert_array_equal(
        np.flatnonzero(hitfinder.data_mask), spi_ref.data_ix)
    np.testing.assert_array_equal(
        hitfinder.hitscore[hitfinder.data_mask], spi_ref.data_hitscore)

    np.testing.assert_allclose(
        hitfinder.threshold, spi_adaptive_threshold)

    hitfinder.plot_hitrate()
    hitfinder.plot_hitscore_hist(num_bins=100)
    hitfinder.plot_hitscore()
