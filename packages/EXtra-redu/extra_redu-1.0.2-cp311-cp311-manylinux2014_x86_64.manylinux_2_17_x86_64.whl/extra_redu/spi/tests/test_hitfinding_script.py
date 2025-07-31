from unittest import mock

import h5py
import numpy as np
from extra_redu.fileutils.tests.mock.h5py import MockH5Context
from extra_redu.spi.hitfinding import main


def test_spi_hitfinding_script(spi_run, spi_data, mask, spi_ref,
                               spi_adaptive_threshold):
    h5context = MockH5Context()
    detector_id = "SPB_DET_AGIPD1M-1"
    open_run = "extra_redu.spi.hitfinding.open_run"
    with mock.patch(open_run, return_value=spi_run), mock.patch.object(h5py.File, "__new__", h5context):  # noqa: E501
        np.random.seed(seed=3)
        argv = [
            "-p", "700000",
            "-r", "1",
            "-d", detector_id,
            "-t", "0.7",
            "-n", "2",
            "-m", "3", "4", "8", "15",
        ]
        main(argv)

    def _h5File__new__(cls, *args, **kwargs):
        return object.__new__(h5py.File)
    h5py.File.__new__ = _h5File__new__

    filename, spi_outfile = h5context.file_content.popitem()

    # lit-pixels
    src = "INSTRUMENT/SPB_DET_AGIPD1M-1/REDU/LITPX_COUNTER:output"
    litpx_counter_data = spi_outfile[f"{src}/data"]

    goodpx = mask == 0
    np.testing.assert_array_equal(
        litpx_counter_data["litPixels"][2],
        np.sum(spi_data > 0.7, axis=(-2, -1), initial=0, where=goodpx)
    )
    np.testing.assert_array_equal(
        litpx_counter_data["totalIntensity"][2],
        np.sum(spi_data, axis=(-2, -1), initial=0, where=goodpx).astype(int)
    )
    np.testing.assert_array_equal(
        litpx_counter_data["unmaskedPixels"][2],
        np.sum(goodpx, axis=(-1, -2))
    )

    # hitscore and selection
    src = "INSTRUMENT/SPB_DET_AGIPD1M-1/REDU/SPI_HITFINDER:output"
    hitfinder_data = spi_outfile[f"{src}/data"]

    data_mask = np.array(hitfinder_data["dataFlag"][2], bool)
    hitscore = np.array(hitfinder_data["hitscore"][2],
                        dtype=hitfinder_data["hitscore"][1])

    np.testing.assert_array_equal(
        np.flatnonzero(hitfinder_data["hitFlag"][2]), spi_ref.hit_ix)
    np.testing.assert_array_equal(
        np.flatnonzero(hitfinder_data["missFlag"][2]), spi_ref.miss_ix)
    np.testing.assert_array_equal(
        np.flatnonzero(data_mask), spi_ref.data_ix)
    np.testing.assert_array_equal(
        hitscore[data_mask], spi_ref.data_hitscore)

    # threshold
    src = "INSTRUMENT/SPB_DET_AGIPD1M-1/REDU/SPI_HITFINDER:output"
    hitfinder_threshold_data = spi_outfile[f"{src}/threshold"]

    np.testing.assert_allclose(
        hitfinder_threshold_data["value"][2], spi_adaptive_threshold)
