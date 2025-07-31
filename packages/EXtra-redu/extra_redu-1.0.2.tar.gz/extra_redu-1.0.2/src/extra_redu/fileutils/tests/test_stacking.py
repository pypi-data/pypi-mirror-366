from unittest import mock

import numpy as np
import pytest
from extra_redu.fileutils import StackedPulseKeyProxy, StackedPulseSource
from extra_redu.fileutils.stacking import StackedPulseKey

from .mock.extra_data import MockDataCollection, MockSourceData


class SPB_AGIPD:
    detector_id = "SPB_DET_AGIPD1M-1"
    len_detector_id = len(detector_id)
    train_ids = list(range(990, 1110))
    num_trains = len(train_ids)
    count = np.pad(np.repeat(351, 100), [10, 10],
                   constant_values=[0, 0])
    first = np.pad(np.arange(0, 35100, 351), [10, 10],
                   constant_values=[0, 35100])
    pid = np.tile(
        np.arange(1, 352, dtype=np.uint64), 100)
    tid = np.repeat(
        train_ids, count).astype(np.uint64)
    nfrm = np.sum(count)

    @classmethod
    def sources(cls, num_sources=16):
        return (
            f"{cls.detector_id}/CORR/{modno}CH0:output"
            for modno in range(num_sources)
        )

    @classmethod
    def source_data(cls, modno):
        return {
            "image.pulseId": cls.pid.reshape(cls.nfrm, 1),
            "image.data": np.full((cls.nfrm, 32, 4), 3 * modno, np.float32),
        }

    @classmethod
    def get_data(cls):
        data = {
            name: MockSourceData(name, cls.train_ids, cls.count,
                                 cls.source_data(modno))
            for modno, name in enumerate(cls.sources())
        }
        return data


@pytest.fixture
def agipd():
    return SPB_AGIPD


@pytest.fixture
def run(agipd):
    # detector
    data = agipd.get_data()
    # other sources
    data.update({
        "SA1_XTD2_ATT/MDL/MAIN": mock.MagicMock(),
        "SA1_XTD2_XGM/XGM/DOOCS": mock.MagicMock(),
        "SPB_IRU_AGIPD1M1/MDL/DATA_SELECTOR": mock.MagicMock(),
        "SPB_IRU_AGIPD1M1/MDL/FPGA_COMP": mock.MagicMock(),
        "SPB_IRU_AGIPD1M1/REDU/LITFRM": mock.MagicMock(),
        "SPB_XTD9_XGM/XGM/DOOCS": mock.MagicMock(),
        "SA1_XTD2_XGM/XGM/DOOCS:output": mock.MagicMock(),
        "SPB_XTD9_XGM/XGM/DOOCS:output": mock.MagicMock()
    })
    return MockDataCollection.mock(agipd.train_ids, data=data)


@pytest.fixture
def detector(run, agipd):
    sources_ptrn = agipd.detector_id + r"/CORR/(?P<key>\d+)CH0:output"
    return StackedPulseSource.from_datacollection(run, sources_ptrn, "image")


def test_stacked_pusle_source(agipd, detector):
    assert detector.num_sources == 16
    assert detector.index_group == "image"
    assert detector.num_events == 35100
    assert detector.train_ids == agipd.train_ids[10:-10]

    data_trains = agipd.count != 0
    count = agipd.count[data_trains]
    first = agipd.first[data_trains]

    np.testing.assert_array_equal(detector.trainId, agipd.tid)
    np.testing.assert_array_equal(detector.pulseId, agipd.pid)
    np.testing.assert_array_equal(detector.count, count)
    np.testing.assert_array_equal(detector.first, first)

    np.testing.assert_array_equal(detector.data_counts(), count)
    np.testing.assert_array_equal(detector.train_id_coordinates(), agipd.tid)

    assert detector.mask.shape == (agipd.nfrm, 16)


def test_stacked_pulse_key(agipd, detector):
    img = detector["data"]
    assert isinstance(img, StackedPulseKey)
    assert isinstance(img.stack, StackedPulseSource)
    assert img.key == "image.data"

    assert img.dtype == np.float32
    assert img.shape == (agipd.nfrm, 16, 32, 4)
    image_data = np.broadcast_to(
        np.arange(0, 16 * 3, 3, dtype=np.float32).reshape(1, 16, 1, 1),
        (agipd.nfrm, 16, 32, 4)
    )
    np.testing.assert_array_equal(img.ndarray(), image_data)


def test_stacked_pulse_key_proxy():
    arr = np.zeros([20, 30, 40], dtype=np.float16)
    key = StackedPulseKeyProxy(arr)
    assert key.dtype == np.float16
    assert key.shape == (20, 30, 40)
    np.testing.assert_array_equal(key.ndarray(), arr)
    np.testing.assert_array_equal(
        key.ndarray(np.s_[3:20:2]), arr[:, 3:20:2])
