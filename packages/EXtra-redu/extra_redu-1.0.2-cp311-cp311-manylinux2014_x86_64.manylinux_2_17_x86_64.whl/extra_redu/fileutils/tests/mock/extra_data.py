from unittest import mock

import numpy as np
from extra_data import (
    DataCollection, KeyData, PropertyNameError, SourceData, SourceNameError,
    by_id)


class MockKeyData:
    def __init__(self, train_ids, count, data):
        self.train_ids = train_ids
        self.count = count
        self.data = np.asarray(data)

    @classmethod
    def mock(cls, train_ids, count, data):
        keydata = cls(train_ids, count, data)
        mock_key = mock.MagicMock(
            spec=KeyData, wraps=keydata)
        mock_key.train_ids = keydata.train_ids
        mock_key.dtype = keydata.dtype
        mock_key.shape = keydata.shape
        return mock_key

    def ndarray(self):
        return self.data

    def data_counts(self, labelled=True):
        if labelled:
            import pandas as pd
            return pd.Series(self.count, index=self.train_ids)
        else:
            return self.count

    @property
    def dtype(self):
        return self.data.dtype

    @property
    def shape(self):
        return self.data.shape

    def as_single_value(self, rtol):
        if np.ndim(self.data) == 0:
            return self.data
        return self.data[0]


class MockSourceData:
    def __init__(self, source_id, train_ids, count, data):
        self.source_id = source_id
        self.train_ids = train_ids
        self.count = count
        self.data = data

    @classmethod
    def mock(cls, source_id, train_ids, count, data):
        source = cls(source_id, train_ids, count, data)
        return mock.MagicMock(
            spec=SourceData, wraps=source)

    @staticmethod
    def _wrap(source):
        mock_source = mock.MagicMock(
            spec=SourceData, wraps=source)
        mock_source.train_ids = source.train_ids
        mock_source.__getitem__.side_effect = source.__getitem__
        mock_source.source = source.source_id
        return mock_source

    @property
    def source(self):
        return self.source_id

    def __getitem__(self, key):
        if key not in self.data:
            raise PropertyNameError(key, self.source_id)

        arr = self.data[key]
        return MockKeyData.mock(self.train_ids, self.count, arr)

    def select_trains(self, selected_trains):
        if isinstance(selected_trains, by_id):
            ix = np.flatnonzero(np.isin(
                self.train_ids, selected_trains.value))
        else:
            ix = selected_trains

        trn_flag = np.zeros(len(self.train_ids), bool)
        trn_flag[ix] = True

        frm_flag = np.repeat(trn_flag, self.count)
        data_sliced = {
            name: elem[frm_flag] for name, elem in self.data.items()}

        return self.__class__(self.source_id,
                              np.asarray(self.train_ids)[ix].tolist(),
                              self.count[ix], data_sliced)


class MockDataCollection:
    def __init__(self, train_ids, data):
        self.train_ids = train_ids
        self.data = data

        self.all_sources = list(data.keys())
        self.instrument_sources = []
        self.control_sources = []
        for source in data:
            if ':' in source:
                self.instrument_sources.append(source)
            else:
                self.control_sources.append(source)

    @classmethod
    def mock(cls, train_ids, data):
        run = cls(train_ids, data)
        return MockDataCollection._wrap(run)

    @staticmethod
    def _wrap(run):
        mock_run = mock.MagicMock(
            spec=DataCollection, wraps=run)
        mock_run.all_sources = run.all_sources
        mock_run.instrument_sources = run.instrument_sources
        mock_run.control_sources = run.control_sources
        mock_run.__getitem__.side_effect = run.__getitem__
        return mock_run

    def __getitem__(self, key):
        if isinstance(key, tuple) and len(key) == 2:
            return self._get_key_data(*key)
        elif isinstance(key, str):
            return self._get_source_data(key)

        raise TypeError("Expected data[source] or data[source, key]")

    def _get_key_data(self, source, key):
        return self._get_source_data(source)[key]

    def _get_source_data(self, source):
        if source not in self.data:
            raise SourceNameError(source)

        return MockSourceData._wrap(self.data[source])

    def select_trains(self, selected_trains):
        if isinstance(selected_trains, by_id):
            ix = np.flatnonzero(np.isin(
                self.train_ids, selected_trains.value))
        elif isinstance(selected_trains, slice):
            ix = range(*selected_trains.indices(len(self.train_ids)))
        else:
            ix = selected_trains

        new_train_ids = [self.train_ids[i] for i in ix]
        new_data = {}
        for name, source in self.data.items():
            new_data[name] = source.select_trains(selected_trains)

        return self.__class__.mock(new_train_ids, new_data)
