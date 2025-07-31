from unittest import mock

import h5py
import numpy as np


class MockH5Dataset:
    def __init__(self, parent, name, shape=None, dtype=None,
                 data=None, **kwargs):
        self.name = name
        self.data = data
        self.dtype = dtype
        self.shape = shape
        self._dtype = np.asarray(data).dtype if dtype is None else dtype
        self._shape = np.shape(data) if shape is None else shape
        self.maxshape = kwargs.get("maxshape", self._shape)
        self.parent = parent
        self.__update_parent()

    @classmethod
    def mock(cls, parent, name, shape=None, dtype=None,
             data=None, **kwargs):
        dataset = cls(parent, name, shape, dtype, data, **kwargs)
        mock_ds = mock.MagicMock(spec=h5py.Dataset, wraps=dataset)
        mock_ds.dtype = dataset.dtype
        mock_ds.shape = dataset.shape
        mock_ds.maxshape = dataset.maxshape
        mock_ds.__setitem__.side_effect = dataset.__setitem__
        mock_ds.__getitem__.side_effect = dataset.__getitem__
        return mock_ds

    def set_parent(self, parent):
        self.parent = parent

    def resize(self, size, axis=None):
        if axis is None:
            self._shape = size
        else:
            shape = list(self._shape)
            shape[axis] = size
            self._shape = tuple(shape)
        self.shape = self._shape
        if self.data is not None:
            self.data = np.resize(self.data, self.shape)
        self.__update_parent()

    def __getitem__(self, index):
        data = self.data
        if data is None:
            data = np.empty(self.shape, self.dtype)
        isstr = isinstance(data, str) or isinstance(data, bytes)
        if index == slice(None):
            if isstr:
                return [data]
            try:
                return data[:]
            except (TypeError, IndexError):
                return [data]
        if index == ():
            return data
        return data[index]

    def __setitem__(self, index, data):
        if self.data is None:
            self.data = np.empty(self.shape, self.dtype)
        self.data[index] = data
        self.__update_parent()

    def __update_parent(self):
        data = self.data
        if isinstance(data, np.ndarray):
            data = data.tolist()
        self.parent.data[self.name] = (
            self.shape, self.dtype, data)


class MockH5Group:
    def __init__(self, data):
        self.data = data

    @classmethod
    def mock(cls, data, spec=h5py.Group):
        group = cls(data)
        return MockH5Group._wrap(group, spec)

    @staticmethod
    def _wrap(group, spec=h5py.Group):
        mock_grp = mock.MagicMock(spec=spec, wraps=group)
        mock_grp.__getitem__.side_effect = group.__getitem__
        mock_grp.__contains__.side_effect = group.__contains__
        return mock_grp

    def __contains__(self, name):
        return name in self.data

    def require_group(self, name):
        return MockH5Group.mock(self.data.setdefault(name, {}))

    def __getitem__(self, name):
        entry = self.data[name]
        if isinstance(entry, dict):
            return MockH5Group.mock(entry)

        return MockH5Dataset.mock(self, name, *entry)

    def create_dataset(self, name, shape=None, dtype=None,
                       data=None, **kwargs):
        if name in self.data:
            raise Exception()

        return MockH5Dataset.mock(self, name, shape, dtype, data, **kwargs)

    def items(self):
        return ((name, self[name]) for name in self.data)


class MockH5File(MockH5Group):
    @classmethod
    def mock(cls, data):
        file = cls(data)
        return MockH5File._wrap(file)

    @staticmethod
    def _wrap(file):
        mock_file = mock.MagicMock(spec=h5py.File, wraps=file)
        mock_file.__getitem__.side_effect = file.__getitem__
        mock_file.__contains__.side_effect = file.__contains__
        return mock_file

    def close(self):
        pass


class MockH5Context:
    def __init__(self, file_content={}):
        self.file_content = file_content

    def __call__(self, cls, filename, mode):
        data = self.file_content.setdefault(filename, {})
        if mode == "w":
            data.clear()

        file = MockH5File.mock(data)
        file.filename = str(filename)
        file.mode = mode
        return file
