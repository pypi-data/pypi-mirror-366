from pathlib import Path

import numpy as np
import pytest
from extra_redu.fileutils.datafile import ControlSource, InstrumentSource
from extra_redu.fileutils.h5utils import escape_key

from .mock.datafile import make_mock_datafile


@pytest.fixture
def filedata_content():
    content = {
        'INDEX': {
            'trainId': ((20,), np.uint64, list(range(20))),
            'timestamp': ((20,), np.uint64, [0] * 20),
            'flag': ((20,), np.int32, [1] * 20),
            'origin': ((20,), np.int32, [-1] * 20)},
        'METADATA': {
            'creationDate': ((1,), None, b'20240715T093001Z'),
            'daqLibrary': ((1,), None, b'1.x'),
            'dataFormatVersion': ((1,), None, b'1.2'),
            'dataSources': {
                'dataSourceId': ((2,), None, [
                    b'CONTROL/SPB_DET_AGIPD1M1/REDU/LITPX_COUNTER',
                    b'INSTRUMENT/SPB_DET_AGIPD1M1/REDU/LITPX_COUNTER:output/litpx'  # noqa: E501
                ]),
                'deviceId': ((2,), None, [
                    b'SPB_DET_AGIPD1M1/REDU/LITPX_COUNTER',
                    b'SPB_DET_AGIPD1M1/REDU/LITPX_COUNTER:output/litpx'
                ]),
                'root': ((2,), None, [b'CONTROL', b'INSTRUMENT'])
            },
            'karaboFramework': ((1,), None, b'2.x'),
            'proposalNumber': ((1,), None, np.uint32(0)),
            'runNumber': ((1,), None, np.uint32(10)),
            'sequenceNumber': ((1,), None, np.uint32(1)),
            'updateDate': ((1,), None, b'20240715T093001Z')
        }
    }
    return content


def test_datafile(filedata_content):
    written_data = {}
    file = make_mock_datafile(
        "output", "TEST00", 10, 1, max_trains=20, data=written_data)
    h5file = file._file
    assert h5file.filename.endswith("output/CORR-R0010-TEST00-S00001.h5")

    assert file._max_trains == 20
    assert file._num_trains == 0

    assert file._DataFile__sources == {}
    assert file._DataFile__meta["daqLibrary"] == "1.x"
    assert file._DataFile__meta["dataFormatVersion"] == "1.2"
    assert file._DataFile__meta["karaboFramework"] == "2.x"
    assert file._DataFile__meta["proposalNumber"] == np.uint32(0)
    assert file._DataFile__meta["runNumber"] == np.uint32(10)
    assert file._DataFile__meta["sequenceNumber"] == np.uint32(1)

    np.testing.assert_array_equal(
        file._DataFile__index["train_ids"], np.array([], np.uint64))

    file.create_source("SPB_DET_AGIPD1M1/REDU/LITPX_COUNTER")

    with pytest.raises(ValueError, match=r"is already exist.$"):
        file.create_source("SPB_DET_AGIPD1M1/REDU/LITPX_COUNTER")

    with pytest.raises(ValueError, match=r"^invalid source format"):
        file.create_source("SPB_DET_AGIPD1M1/REDU/LITPX_COUNTER:output")

    file.create_source("SPB_DET_AGIPD1M1/REDU/LITPX_COUNTER:output.litpx")

    file.create_index()

    train_ids = list(range(20))
    file.write_index(train_ids)

    filename, testfile_content = written_data.popitem()
    assert testfile_content == filedata_content


def test_datafile_read(filedata_content):
    data = {
        Path("output/CORR-R0010-TEST00-S00001.h5").resolve(): filedata_content,
    }
    file = make_mock_datafile(
        "output", "TEST00", 10, 1, mode="a", max_trains=20, data=data)

    assert file._max_trains == 20
    assert file._num_trains == 19

    assert file._DataFile__meta["daqLibrary"] == "1.x"
    assert file._DataFile__meta["dataFormatVersion"] == "1.2"
    assert file._DataFile__meta["karaboFramework"] == "2.x"
    assert file._DataFile__meta["proposalNumber"] == np.uint32(0)
    assert file._DataFile__meta["runNumber"] == np.uint32(10)
    assert file._DataFile__meta["sequenceNumber"] == np.uint32(1)

    _meta = filedata_content["METADATA"]
    expeced_sources = _meta["dataSources"]["deviceId"][2]
    for i, (source_id, source) in enumerate(file._DataFile__sources.items()):
        assert escape_key(source_id) == expeced_sources[i].decode()
        assert isinstance(
            source, InstrumentSource if ':' in source_id else ControlSource)


@pytest.fixture
def control_content():
    content = {
        'CONTROL/SPB_DET_AGIPD1M-1/REDU/LITPX_COUNTER': {
            'threshold/value': ((10,), np.float64, [0.7] * 10),
            'threshold/timestamp': ((10,), 'u8', [1] * 10)},
        'RUN/SPB_DET_AGIPD1M-1/REDU/LITPX_COUNTER': {
            'threshold/value': ((1,), np.float64, [0.7]),
            'threshold/timestamp': ((1,), 'u8', [1])
        },
        'INDEX/SPB_DET_AGIPD1M-1/REDU/LITPX_COUNTER': {
            'first': ((10,), np.uint64, list(range(10))),
            'count': ((10,), np.uint64, [1] * 10)
        }
    }
    return content


def test_control_source(control_content):
    written_data = {}
    file = make_mock_datafile(
        "output", "TEST00", 10, 1, max_trains=10, data=written_data)
    file._num_trains = 10

    with pytest.raises(ValueError, match=r"^invalid source format"):
        src = ControlSource(file, "SPB_DET_AGIPD1M-1/REDU/@LITPX_COUNTER")

    name = "SPB_DET_AGIPD1M-1/REDU/LITPX_COUNTER"
    src = ControlSource(file, name)

    assert src.root == "CONTROL"
    assert src._keys == {}
    assert src._group is None
    assert src._run_keys == {}
    assert src._run_group is None

    assert src._source == name

    assert src.name == name
    assert src.h5path == f"CONTROL/{name}"
    assert src.h5path_index == f"INDEX/{name}"
    assert src.h5path_run == f"RUN/{name}"

    assert src.num_entries == 10

    src.create_group()
    src.create_run_group()
    src.create_index()
    src.write_index()

    with pytest.raises(ValueError, match=r"is always one$"):
        src.add_key("threshold", np.array([0.7, 0.8]))

    with pytest.raises(ValueError, match=r"^The data shape"):
        src.add_key("threshold", np.array([[0.7, 0.8]]), shape=(1, 1))

    with pytest.raises(ValueError, match=r"^The length of the data"):
        src.add_key("threshold", 0.7, 1, np.array([0.7, 0.8]))

    with pytest.raises(ValueError, match=r"^The data shape in RUN"):
        src.add_key("threshold", 0.7, 1, np.array([[0.7, 0.8]]))

    with pytest.raises(ValueError, match=r"^The data type in RUN"):
        src.add_key("threshold", 0.7, 1, np.array(0.7, dtype=np.float32))

    with pytest.raises(ValueError, match=r"^The timestamp \(2\)"):
        src.add_key("threshold", 0.7, 1, 0.7, [0, 1])

    with pytest.raises(ValueError, match=r"a scalar or a vector$"):
        src.add_key("threshold", 0.7, 1, 0.7, np.array([[0, 1]]))

    src.add_key("threshold", 0.7, 1, 0.7, 1)

    data, ts, data_ds, ts_ds = src._keys["threshold"]
    assert list(src._keys) == ["threshold"]
    assert data == 0.7
    assert ts == 1

    src.write_keys()

    filename, testfile_content = written_data.popitem()
    assert testfile_content == control_content


@pytest.fixture
def instrument_content():
    first = [0, 0, 1, 3, 6, 10, 15, 21, 28, 36]
    count = list(range(10))
    pid = []
    for n in count:
        pid.extend(range(n))
    content = {
        'INSTRUMENT/SPB_DET_AGIPD1M-1/REDU/LITPX_COUNTER:output/litpx': {
            'pulseId': ((np.int64(45),), np.uint64, pid),
            'litPixels': ((np.int64(45),), np.int64, pid)
        },
        'INDEX/SPB_DET_AGIPD1M-1/REDU/LITPX_COUNTER:output/litpx': {
            'first': ((10,), np.uint64, first),
            'count': ((10,), np.uint64, count)
        }
    }
    return content


def test_instrument_source(instrument_content):
    written_data = {}
    file = make_mock_datafile(
        "output", "TEST00", 10, 1, max_trains=10, data=written_data)
    file._num_trains = 10

    with pytest.raises(ValueError, match=r"^invalid source format"):
        src = InstrumentSource(
            file, "SPB_DET_AGIPD1M-1/REDU/LITPX_COUNTER:output")

    name = "SPB_DET_AGIPD1M-1/REDU/LITPX_COUNTER"
    channel = "output.litpx"
    src = InstrumentSource(file, f"{name}:{channel}")

    assert src.root == "INSTRUMENT"
    assert src._keys == {}
    assert src._group is None
    assert not hasattr(src, "_run_keys")
    assert not hasattr(src, "_run_group")

    np.testing.assert_array_equal(
        src._count, np.zeros(10, np.uint64))

    assert src._pulse_ids is None
    assert src._num_entries == 0

    assert src._source == name
    assert src._channel == channel

    assert src.name == f"{name}:{channel}"
    h5name = f"{name}:{channel.replace('.', '/')}"
    assert src.h5path == f"INSTRUMENT/{h5name}"
    assert src.h5path_index == f"INDEX/{h5name}"

    assert src.num_entries == 0

    src.create_group()

    count = np.arange(10)
    nevt = np.sum(count)
    pulse_ids = np.concatenate([np.arange(n) for n in count])
    src.set_index(count, pulse_ids)

    assert src.num_entries == nevt
    assert src._num_entries == nevt
    np.testing.assert_array_equal(src._pulse_ids, pulse_ids)
    np.testing.assert_array_equal(src._count, count)

    src.create_index()
    src.write_index()

    with pytest.raises(ValueError, match=r"^The length of the data"):
        src.add_key("litPixels", count)

    with pytest.raises(ValueError, match=r"^The data shape"):
        src.add_key("litPixels", pulse_ids, shape=(1, 1))

    src.add_key("litPixels", pulse_ids, shape=())

    data, ds = src._keys["litPixels"]
    assert sorted(src._keys) == ["litPixels", "pulseId"]

    np.testing.assert_array_equal(data, pulse_ids)

    src.write_keys()

    filename, testfile_content = written_data.popitem()
    assert testfile_content == instrument_content
