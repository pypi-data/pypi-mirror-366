import datetime
from unittest import mock

import h5py
from extra_redu.fileutils import DataFile

from .h5py import MockH5Context


def make_mock_datafile(folder, aggregator, run, sequence,
                       prefix="CORR", mode="w", max_trains=500, data=None):
    if data is None:
        data = {}
    h5context = MockH5Context(data)

    now = datetime.datetime(2024, 7, 15, 9, 30, 1)
    with mock.patch.object(h5py.File, "__new__", h5context):
        file = DataFile.from_details(
            folder, aggregator, run, sequence, prefix, mode, max_trains)

    def _h5File__new__(cls, *args, **kwargs):
        return object.__new__(h5py.File)
    h5py.File.__new__ = _h5File__new__

    file._DataFile__meta.update({
        "creationDate": now,
        "updateDate": now,
    })
    file._h5context = h5context
    return file
