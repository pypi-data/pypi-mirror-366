from pathlib import Path
from unittest import mock

import h5py
import numpy as np
import pytest
from extra_redu.fileutils import (
    ChannelData, exdf_constant, exdf_constant_string, exdf_save)
from extra_redu.fileutils.writer import (
    add_channel_data, add_properties, exdf_translate, exdf_type_cast,
    find_properties)

from .mock.datafile import make_mock_datafile
from .mock.h5py import MockH5Context


def test_exdf_translate():
    assert exdf_translate("_min_scores") == "minScores"
    assert exdf_translate("min_scores") == "minScores"
    exdf_translate("_fixed_threshold_1") == "fixedThreshold1"
    exdf_translate("_fixed_threshold1") == "fixedThreshold1"


def test_exdf_type_cast():
    assert exdf_type_cast(np.array(True).dtype) == np.uint8
    assert (exdf_type_cast(np.array("true").dtype)
            == h5py.string_dtype(encoding='utf-8', length=16))
    assert (exdf_type_cast(np.array("true".encode("ascii")).dtype)
            == h5py.string_dtype(encoding='ascii', length=4))
    assert exdf_type_cast(np.array(8).dtype) == int
    assert exdf_type_cast(np.array(8.).dtype) == float


class MockProcessor:

    def __init__(self):
        self.scalar = 1.
        self.vector = np.zeros(10, np.int16)
        self.string = "abc"

        self._keys = keys = {
            "scalar": np.ones(55, dtype=int),
            "vector": np.zeros([55, 3], dtype=float),
            "matrix": np.full([55, 3, 3], 3, dtype=np.uint16)
        }
        self.train_ids = train_ids = list(range(100001, 100011))
        self.count = count = np.arange(1, 11, dtype=int)
        self.pulse_ids = pulse_ids = np.concatenate(
            [np.arange(n, dtype=int) for n in count])
        self._channels = {
            "output.data": ChannelData(keys, train_ids, count, pulse_ids),
        }
        self.results = {
            "myScalar": np.full(10, 1, float),
            "omitScalar": np.full(10, 1, float),
            "myVector": np.zeros([10, 10], np.int16),
            "randomName": np.zeros([10, 10], np.int16),
            "myString": np.full(10, 'abc', "|S5"),
            "abcString": np.full(10, 'abc', "|S10"),
        }

    @exdf_constant
    def _my_scalar(self):
        return self.scalar

    @exdf_constant(omit=True)
    def _omit_scalar(self):
        return self.scalar

    @exdf_constant
    def _my_vector(self):
        return self.vector

    @exdf_constant(name="randomName")
    def _again_vector(self):
        return self.vector

    @exdf_constant_string(5)
    def _my_string(self):
        return self.string

    @exdf_constant_string(10, "abcString", omit=True)
    def _omit_string(self):
        return self.string

    def _not_exdf_property(self):
        return 1


@pytest.fixture
def proc():
    proc = MockProcessor()
    return proc


def test_channeldata(proc):
    keys = proc._keys
    train_ids = proc.train_ids
    count = proc.count
    pulse_ids = proc.pulse_ids
    ch = proc._channels["output.data"]

    assert sorted(ch.keys) == sorted(keys)
    assert sorted(ch.train_ids) == train_ids
    np.testing.assert_array_equal(ch.count, count)
    np.testing.assert_array_equal(ch.pulse_ids, pulse_ids)
    assert ch.trains_selected == np.s_[:]
    assert ch.pulses_selected == np.s_[:]
    np.testing.assert_array_equal(ch.count_selected, count)

    ch.select_trains(list(range(100003, 100007)))

    train_mask = np.zeros(10, bool)
    train_mask[2:6] = True
    pulse_mask = np.zeros(55, bool)
    pulse_mask[3:21] = True
    np.testing.assert_array_equal(ch.trains_selected, train_mask)
    np.testing.assert_array_equal(ch.pulses_selected, pulse_mask)
    np.testing.assert_array_equal(ch.count_selected, count[2:6])

    for n, v in ch.items():
        a = keys[n]
        np.testing.assert_array_equal(v, a[pulse_mask])

    ch.reset()
    for n, v in ch.items():
        a = keys[n]
        np.testing.assert_array_equal(v, a)


def test_find_properties(proc):
    results = proc.results
    train_ids = proc.train_ids
    properies = find_properties(proc)
    for name, prop in properies.items():
        arr, ts = prop(train_ids)
        np.testing.assert_array_equal(arr, results[name])
        assert hasattr(prop, "__exdf_property")
        assert prop.__exdf_property == name
        assert isinstance(prop.__exdf_omit, bool)

    assert "_not_exdf_property" not in properies


def test_add_properties(proc):
    train_ids = list(range(100001, 100006))
    num_trains = len(train_ids)
    file = make_mock_datafile(
        "output", "TEST00", 10, 1, max_trains=num_trains, data={})

    src = file.create_source("testSource")

    file.write_index(train_ids)
    file.write_schema()

    run_values = {}
    add_properties(src, proc, train_ids, run_values)

    # control data
    keys = ['randomName', 'myScalar', 'myString', 'myVector']
    assert sorted(src._keys) == sorted(keys)

    timestamp = np.zeros(num_trains, np.uint64)
    for key, (data, ts, ds_data, ds_ts) in src._keys.items():
        print(key)
        np.testing.assert_array_equal(
            data, proc.results[key][:num_trains])
        np.testing.assert_array_equal(ts, timestamp)
        assert isinstance(ds_data, h5py.Dataset)
        assert isinstance(ds_ts, h5py.Dataset)

    # run data
    keys = keys + ['omitScalar', 'abcString']
    assert sorted(src._run_keys) == sorted(keys)

    for key, (data, ts, ds_data, ds_ts) in src._run_keys.items():
        np.testing.assert_array_equal(
            data, proc.results[key][:1])
        assert ts == 0
        assert isinstance(ds_data, h5py.Dataset)
        assert isinstance(ds_ts, h5py.Dataset)


def test_add_channel_data(proc):
    train_ids = list(range(100001, 100006))
    num_trains = len(train_ids)
    file = make_mock_datafile(
        "output", "TEST00", 10, 1, max_trains=num_trains, data={})

    src = file.create_source("testSource:output.data")

    file.write_index(train_ids)
    file.write_schema()

    ch = proc._channels["output.data"]
    add_channel_data(src, ch, train_ids)

    assert sorted(src._keys) == sorted(proc._keys)
    np.testing.assert_array_equal(src._count, proc.count[:5])
    np.testing.assert_array_equal(src._pulse_ids, proc.pulse_ids[:15])
    assert src._num_entries == 15

    for key, (data, ds) in src._keys.items():
        np.testing.assert_array_equal(data, proc._keys[key][:15])
        assert isinstance(ds, h5py.Dataset)


def test_exdf_save(proc):
    h5context = MockH5Context()

    with mock.patch.object(h5py.File, "__new__", h5context):
        processors = {
            "TST_FILEUTILS/EXDF/SAVE": proc,
        }
        with pytest.raises(ValueError, match=r"^invalid aggregator format"):
            exdf_save(".", "TST0", 11, processors=processors,
                      train_ids=None, sequence_size=6)

        exdf_save(".", "TST00", 11, processors=processors,
                  train_ids=None, sequence_size=6)

    def _h5File__new__(cls, *args, **kwargs):
        return object.__new__(h5py.File)
    h5py.File.__new__ = _h5File__new__

    written_files = sorted(h5context.file_content)
    expected_files = [
        Path(f"CORR-R0011-TST00-S{seqno:05d}.h5").resolve()
        for seqno in range(2)
    ]
    assert written_files == expected_files

    frm0 = 0
    trn0 = 0
    num_trains_in_seq = [6, 4]
    expected_keys = [
        'METADATA',
        'INDEX',
        'CONTROL/TST_FILEUTILS/EXDF/SAVE',
        'INDEX/TST_FILEUTILS/EXDF/SAVE',
        'INSTRUMENT/TST_FILEUTILS/EXDF/SAVE:output/data',
        'INDEX/TST_FILEUTILS/EXDF/SAVE:output/data',
        'RUN/TST_FILEUTILS/EXDF/SAVE'
    ]

    for seqno, num_trains in enumerate(num_trains_in_seq):
        # first file
        filename = written_files[seqno]
        trnN = trn0 + num_trains

        num_frames = np.sum(proc.count[trn0:trnN])
        frmN = frm0 + num_frames
        content = h5context.file_content[filename]

        assert sorted(content) == sorted(expected_keys)

        meta = content["METADATA"]

        assert meta["proposalNumber"][2] == 0
        assert meta["runNumber"][2] == 11
        assert meta["sequenceNumber"][2] == seqno

        assert sorted(meta["dataSources"]["dataSourceId"][2]) == sorted([
            b'CONTROL/TST_FILEUTILS/EXDF/SAVE',
            b'INSTRUMENT/TST_FILEUTILS/EXDF/SAVE:output/data'
        ])

        assert content["INDEX"]["trainId"][2] == proc.train_ids[trn0:trnN]

        # instrument source
        inst = content['INSTRUMENT/TST_FILEUTILS/EXDF/SAVE:output/data']

        assert sorted(inst) == sorted(
            ['scalar', 'vector', 'matrix', 'pulseId'])
        np.testing.assert_array_equal(
            inst["scalar"][2], np.ones(num_frames, np.int64))
        np.testing.assert_array_equal(
            inst["vector"][2], np.zeros((num_frames, 3), np.float64))
        np.testing.assert_array_equal(
            inst["matrix"][2], np.full((num_frames, 3, 3), 3, np.uint16))
        np.testing.assert_array_equal(
            inst["pulseId"][2], proc.pulse_ids[frm0:frmN])

        inst_index = content['INDEX/TST_FILEUTILS/EXDF/SAVE:output/data']
        np.testing.assert_array_equal(
            inst_index["count"][2], proc.count[trn0:trnN])
        np.testing.assert_array_equal(
            inst_index["first"][2],
            np.cumsum(proc.count[trn0:trnN]) - proc.count[trn0:trnN]
        )

        # control source
        ctrl = content['CONTROL/TST_FILEUTILS/EXDF/SAVE']

        ctrl_keys = [
            'randomName/value', 'randomName/timestamp',
            'myScalar/value', 'myScalar/timestamp',
            'myString/value', 'myString/timestamp',
            'myVector/value', 'myVector/timestamp'
        ]
        assert sorted(ctrl) == sorted(ctrl_keys)
        np.testing.assert_array_equal(
            ctrl["randomName/value"][2], np.zeros((num_trains, 10), np.int16))
        np.testing.assert_array_equal(
            ctrl["myScalar/value"][2], np.ones(num_trains))
        np.testing.assert_array_equal(
            ctrl["myVector/value"][2], np.zeros((num_trains, 10), np.float64))
        np.testing.assert_array_equal(
            ctrl["myString/value"][2], np.array([b'abc'] * num_trains))

        ts = np.zeros(num_trains, np.uint64)
        for key in ctrl_keys:
            if key.endswith("/timestamp"):
                np.testing.assert_array_equal(ctrl[key][2], ts)

        run = content['RUN/TST_FILEUTILS/EXDF/SAVE']
        run_keys = ctrl_keys + [
            'omitScalar/value', 'omitScalar/timestamp',
            'abcString/value', 'abcString/timestamp'
        ]
        assert sorted(run) == sorted(run_keys)
        np.testing.assert_array_equal(
            run["randomName/value"][2], np.zeros((1, 10), np.int16))
        np.testing.assert_array_equal(
            run["myScalar/value"][2], np.ones(1))
        np.testing.assert_array_equal(
            run["myVector/value"][2], np.zeros((1, 10), np.float64))
        np.testing.assert_array_equal(
            run["myString/value"][2], [b'abc'])

        np.testing.assert_array_equal(
            run["omitScalar/value"][2], np.ones(1))
        np.testing.assert_array_equal(
            run["abcString/value"][2], [b'abc'])

        for key in ctrl_keys:
            if key.endswith("/timestamp"):
                assert run[key][2] == [0]

        trn0 = trnN
        frm0 = frmN
