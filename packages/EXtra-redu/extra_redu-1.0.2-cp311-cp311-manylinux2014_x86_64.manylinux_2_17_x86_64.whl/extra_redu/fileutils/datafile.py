import re
from datetime import datetime
from pathlib import Path

import h5py
import numpy as np

from . import h5utils
from .h5utils import escape_key


class DataFile:
    """European XFEL HDF5 data file.

    This class implements writing data in a file in the European XFEL
    file format.

    Please refer to
    https://extra-data.readthedocs.io/en/latest/data_format.html for
    details of the file format.
    """
    filename_format = '{prefix}-R{run:04d}-{aggregator}-S{sequence:05d}.h5'
    aggregator_pattern = re.compile(r'^\w{2,}\d{2}$')
    instrument_source_pattern = re.compile(r'^[\w\/-]+:[\w.]+$')

    def __init__(self, name, mode='r', max_trains=500):
        now = datetime.now()
        self.__sources = {}
        self.__meta = {
            "creationDate": now,
            "daqLibrary": "1.x",
            "dataFormatVersion": "1.2",
            "dataSources": {
                "dataSourceId": lambda: self.source_ids,
                "deviceId": lambda: self.source_names,
                "root": lambda: self.source_roots,
            },
            "karaboFramework": "2.x",
            "proposalNumber": np.uint32(0),
            "runNumber": np.uint32(0),
            "sequenceNumber": np.uint32(0),
            "updateDate": now,
        }
        self.__index = {
            "train_ids": np.array([], np.uint64),
        }
        self._file = h5py.File(name, mode)

        file_index, max_trains = self.read_index(max_trains)
        self.__index.update(file_index)

        self._max_trains = max_trains
        self._num_trains = len(self.__index["train_ids"])

        file_meta = self.read_metadata()
        self.__meta.update(file_meta)

    @classmethod
    def from_details(cls, folder, aggregator, run, sequence,
                     prefix="CORR", mode="w", max_trains=500):
        """Open or create a file based on European XFEL details.

        This methis is a wrapper to construct the filename based its
        components.

        Parameters
        ----------
        folder: str or Path
            Parent location for this file.
        aggregator: str
            Name of the data aggregator, must satisfy
            `DataFile.aggregator_pattern`.
        run: int
            Run number.
        sequence: int
            Sequence number.
        prefix: str
            First filename component, 'CORR' by default.
        max_trains: int
            The maximum number of trains in this file.

        Returns
        -------
        file: DataFile
            Opened file object.
        """
        if not isinstance(folder, Path):
            folder = Path(folder)

        if not cls.aggregator_pattern.match(aggregator):
            raise ValueError(f'invalid aggregator format, must satisfy '
                             f'{cls.aggregator_pattern.pattern}')

        filename = cls.filename_format.format(
            prefix=prefix, aggregator=aggregator, run=run, sequence=sequence)

        datafile = DataFile((folder / filename).resolve(), mode, max_trains)

        datafile.__meta["runNumber"] = np.uint32(run)
        datafile.__meta["sequenceNumber"] = np.uint32(sequence)

        return datafile

    def close(self):
        """Close the file."""
        self._file.close()

    def create_source(self, name):
        """Creates a data source.

        Creates CONTROL ("slow data") or INSTRUMENT ("fast data")
        depending on the name.

        Parameters
        ----------
        name: str
            Source name. For CONTROL source, name is <device ID>.
            For INSTRUMENT source, <device ID>:<channel>.<group>

        Returns
        -------
        source: ControlSource or InstrumentSource
            Created data source
        """
        source = self.__sources.get(name)
        if source is None:
            if ':' in name:
                source = InstrumentSource(self, name)
            else:
                source = ControlSource(self, name)

            self.__sources[name] = source
        else:
            raise ValueError(f"The source with the name `{name}` is "
                             "already exist.")

        return source

    def print_sources(self):
        """Prints data source names."""
        for name, src in self.__sources.items():
            print(src.name)

    def __getitem__(self, index):
        """Returns a source or key data.

        Parameters
        ----------
        index: str or (str, str)
            The source name or tuple of source name and key.

        Returns
        -------
        item: ControlSource, InstrumentSource or h5py.Dataset
            Data source or dataset
        """
        if isinstance(index, str):
            return self.__sources[index]
        else:
            source_name, key = index
            return self.__sources[source_name][key]

    @property
    def source_ids(self):
        """Source IDs of data sources."""
        return [src.h5path for src in self.__sources.values()]

    @property
    def source_roots(self):
        """Root sections of data sources."""
        return [src.root for src in self.__sources.values()]

    @property
    def source_names(self):
        """Data source names."""
        return [escape_key(src.name) for src in self.__sources.values()]

    @property
    def device_ids(self):
        """Device IDs of data sources."""
        return [src.device_id for src in self.__sources.values()]

    def write_metadata(self):
        """Create and write METADATA datasets."""
        group = self._file.require_group("METADATA")
        h5utils.write_dict(group, self.__meta)

    def read_metadata(self):
        """Reads METADATA datasets."""

        if "METADATA" not in self._file:
            return {}

        meta = h5utils.read_dict(self._file["METADATA"])
        data_sources = meta.pop("dataSources", [])
        self.create_sources(data_sources["deviceId"])
        return meta

    def create_sources(self, source_names):
        """Creates multiple data sources from a list of names.

        Parameters
        ----------
        source_names: sequence of str
            The list of data source names
        """
        for name in source_names:
            device_id, _, channel = name.partition(':')
            if channel:
                channel = channel.replace('/', '.')
                self.create_source(f"{device_id}:{channel}")
            else:
                self.create_source(device_id)

    def create_index(self):
        """Creates global INDEX datasets.

        These datasets are agnostic of any source and describe the
        trains contained in this file. The method only creates datasets.
        To write index data use `DataFile.write_index()`
        """
        index = self._file.require_group("INDEX")
        max_trains = self._max_trains
        index.create_dataset("trainId", dtype=np.uint64, shape=max_trains,
                             maxshape=max_trains, chunks=max_trains)
        index.create_dataset("timestamp", dtype=np.uint64, shape=max_trains,
                             maxshape=max_trains, chunks=max_trains)
        index.create_dataset("flag", dtype=np.int32, shape=max_trains,
                             maxshape=max_trains, chunks=max_trains)
        index.create_dataset("origin", dtype=np.int32, shape=max_trains,
                             maxshape=max_trains, chunks=max_trains)

    def write_index(self, train_ids, timestamps=None, flags=None,
                    origins=None, write_metadata=True):
        """Writes global INDEX datasets.

        These datasets are agnostic of any source and describe the
        trains contained in this file. The method writes index data
        according the current state of the instance. If parameters are
        given, they override the the instance state.

        Parameters
        ----------
        train_ids: array or sequence
            Train IDs contained in this file.
        timestamps: array or sequence
            Timestamp of each train, 0 if omitted.
        flags: array or sequence
            Whether the time server is the initial origin of each train,
            1 if omitted.
        origins: array or sequence
            Which source is the initial origin of each train, -1 (time server)
            if omitted.
        write_metadata: bool
            Writes metadata if True.
        """
        num_trains = len(train_ids)
        if num_trains > self._max_trains:
            raise ValueError(
                f"The length of train_ids ({num_trains}) exceeds the maximum "
                f"number of trains in the file ({self._max_trains})")

        self._num_trains = num_trains

        if write_metadata:
            self.write_metadata()

        if "INDEX" not in self._file:
            self.create_index()
        index_group = self._file["INDEX"]

        args = locals()
        defaults = {"timestamps": 0, "flags": 1, "origins": -1}
        for name, default_value in defaults.items():
            value = args[name]
            if value is None:
                value = self.__index.get(name)
            if value is None:
                value = default_value
            elif len(value) != num_trains:
                raise ValueError(f"{name} and train_ids must be same length")
            args[name] = value

        args_to_keys = {
            "train_ids": "trainId", "timestamps": "timestamp",
            "flags": "flag", "origins": "origin"
        }
        for name, key in args_to_keys.items():
            ds = index_group[key]
            ds.resize((num_trains,))
            ds[:] = args[name]
            self.__index[name] = np.empty(num_trains, ds.dtype)
            self.__index[name][:] = args[name]

        for source_name, source in self.__sources.items():
            if isinstance(source, ControlSource):
                source.set_index()

    def read_index(self, max_trains=500):
        """Reads global INDEX datasets.

        These datasets are agnostic of any source and describe the
        trains contained in this file. The method reads data from
        file and returns them as a dict.

        Parameters
        ----------
        max_trains: int
            Default value for the maximum number of trains in the
            file, which method returns if there is no INDEX data
            in the file.

        Returns
        -------
        index: dict
            The dictionary of index data
        max_train: int
            The maximum number of trains in a file
        """
        if "INDEX" not in self._file:
            return {}, max_trains

        index_group = self._file["INDEX"]

        args_to_keys = {
            "train_ids": "trainId", "timestamps": "timestamp",
            "flags": "flag", "origins": "origin"
        }
        index = {}
        for name, key in args_to_keys.items():
            if key in index_group:
                index[name] = index_group[key][:]

        flag = [tid != 0 for tid in index["train_ids"]]
        for name, value in index.items():
            index[name] = [a for a, f in zip(value, flag) if f]

        max_trains = index_group["trainId"].maxshape[0]
        return index, max_trains

    def write_schema(self):
        """Creates the file structure."""
        for source_name, source in self.__sources.items():
            source.create_group()
            source.create_index()

    def write_data(self):
        """Writes data and indices of data sources"""
        for source_name, source in self.__sources.items():
            source.write_index()
            source.write_keys()


class Source:
    source_name_pattern = re.compile(r"^$")

    def __init__(self, file, name):
        """Creares the instance of data source.

        To create the data source, use constructor
        `DataFile.create_source()`.
        """
        match = self.source_name_pattern.match(name)
        if not match:
            raise ValueError(f"invalid source format, must satisfy "
                             f"{self.source_name_pattern.pattern}")

        self._file = file
        for key, value in match.groupdict().items():
            setattr(self, '_' + key, value)

        self._keys = {}
        self._group = None

    @property
    def device_id(self):
        """Device ID of the data source."""
        return self._source

    @property
    def name(self):
        """Data source name."""
        raise NotImplementedError

    @property
    def h5path(self):
        """h5 path of the data source group."""
        raise NotImplementedError

    @property
    def h5path_index(self):
        """h5 path of the data source index group."""
        raise NotImplementedError

    @property
    def num_entries(self):
        """The number of entries in the source."""
        raise NotImplementedError

    def __getitem__(self, key):
        """Returns the key dataset."""
        return self._file[f"{self.h5path}/{escape_key(key)}"]

    def create_group(self):
        """Creates the h5 group for the source."""
        if self._group is None:
            self._group = self._file._file.require_group(self.h5path)
        return self._group

    def create_index(self):
        """Creates the index datasets for data source."""
        index_group = self._file._file.require_group(self.h5path_index)
        max_trains = self._file._max_trains
        first = np.cumsum(self._count) - self._count
        index_group.create_dataset(
            "first", dtype=np.uint64, data=first,
            maxshape=max_trains, chunks=max_trains)
        index_group.create_dataset(
            "count", dtype=np.uint64, data=self._count,
            maxshape=max_trains, chunks=max_trains)

    def write_index(self):
        """Writes the index data for data source."""
        index_group = self._file._file.require_group(self.h5path_index)
        ds = index_group["count"]
        ds.resize((self._file._num_trains,))
        ds[:] = self._count

        ds = index_group["first"]
        ds.resize((self._file._num_trains,))
        ds[:] = np.cumsum(self._count) - self._count

    def write_key(self, name):
        """Writes the data in the key dataset."""
        raise NotImplementedError

    def write_keys(self):
        """Writes data for all keys."""
        raise NotImplementedError

    def add_key(self, name, data, shape=None, dtype=None):
        """Add key in the source and creates h5 dataset.

        The method checks shape and data type and creates the
        datasets for the key. The data is stored in the instance
        to write later after creation of whole file structure.

        Parameters
        ----------
        name: str
            The key name
        data: array, sequence or scalar
            The data to write in the key dataset. For fast data,
            is array or sequence. The first dimention must be
            equal the number of entries in the data source.
            For slow data, can be array, sequence or scalar.
            The first dimention either the number of trains or
            one.
        shape: tuple
            The shape of one entry data. Must match data shape,
            except the first dimention. By default, it is taken
            from data.
        dtype: numpy.dtype or type
            The type of data items. By default, it is taken
            from data.
        """
        raise NotImplementedError


class ControlSource(Source):
    source_name_pattern = re.compile(r"^(?P<source>[\w\/-]+)$")
    root = "CONTROL"

    def __init__(self, file, name):
        super().__init__(file, name)
        self._run_group = None
        self._run_keys = {}
        self.set_index()

    @property
    def name(self):
        return self._source

    @property
    def h5path(self):
        return f"{self.root}/{self._source}"

    @property
    def h5path_index(self):
        return f"INDEX/{self._source}"

    @property
    def h5path_run(self):
        return f"RUN/{self._source}"

    @property
    def num_entries(self):
        return self._file._num_trains

    def set_index(self):
        self._count = np.ones(self.num_entries, int)

    def create_run_group(self):
        """Creates the h5 group for the source in RUN section."""
        if self._run_group is None:
            self._run_group = self._file._file.require_group(self.h5path_run)
        return self._run_group

    def write_run_key(self, name):
        """Writes the data in the run key dataset."""
        data, ts, ds_value, ds_timestamp = self._run_keys[name]
        ds_value[:] = data
        ds_timestamp[:] = ts

    def write_key(self, name):
        """Writes the data in the key dataset."""
        data, ts, ds_value, ds_timestamp = self._keys[name]
        ds_value[:] = data
        ds_timestamp[:] = ts

    def write_keys(self):
        """Writes data for all keys."""
        for keys in (self._run_keys, self._keys):
            for data, ts, ds_value, ds_timestamp in keys.values():
                ds_value[:] = data
                ds_timestamp[:] = ts

    def add_key(self, name, run_data, run_timestamp=0,
                data=None, timestamp=None, shape=None, dtype=None):
        if np.ndim(run_data) == 0:
            # scalar: repeat along run
            if shape is None:
                shape = ()
            run_dtype = np.asarray(run_data).dtype
            if dtype is None:
                dtype = run_dtype
            data_shape = ()
        else:
            if len(run_data) != 1:
                raise ValueError(
                    "The length of the data in RUN section is always one")
            data_shape = np.shape(run_data)[1:]
            if shape is None:
                shape = data_shape
            elif data_shape != tuple(shape):
                raise ValueError(
                    f"The data shape {data_shape} except the first dimentions "
                    f"and the value of shape argument {tuple(shape)} must be "
                    "equal")

            run_data = np.asarray(run_data)
            run_dtype = run_data.dtype
            if dtype is None:
                dtype = run_dtype

        if data is not None:
            len_data = 1 if np.ndim(data) == 0 else len(data)
            if len_data != self.num_entries and len_data != 1:
                raise ValueError(
                    "The length of the data must be one or equal to the "
                    f"number of entries in the source ({self.num_entries})")
            control_data_shape = np.shape(data)[1:]
            if control_data_shape != shape:
                raise ValueError(
                    f"The data shape in RUN section {data_shape} and in "
                    f"CONTROL section {control_data_shape} must be equal "
                    "except first dimention")
            data = np.asarray(data)
            if data.dtype != run_dtype:
                raise ValueError(
                    f"The data type in RUN section {dtype} and in CONTROL "
                    f"section {data.dtype} must be the same")
            if timestamp is None:
                timestamp = 0
            else:
                len_ts = 1 if np.ndim(timestamp) == 0 else len(timestamp)
                if np.ndim(timestamp) > 1:
                    raise ValueError(
                        "The timestamp must be a scalar or a vector")
                if len_ts != len_data:
                    raise ValueError(
                        f"The timestamp ({len_ts}) must be "
                        f"the same length as data ({len_data})")

        h5key = escape_key(name)
        run_group = self.create_run_group()
        ds_run_value = run_group.create_dataset(
            f"{h5key}/value", shape=(1,) + shape, dtype=dtype,
            chunks=(1,) + shape)
        ds_run_timestamp = run_group.create_dataset(
            f"{h5key}/timestamp", shape=(1,), chunks=(1,), dtype="u8")
        self._run_keys[name] = (run_data, run_timestamp,
                                ds_run_value, ds_run_timestamp)

        if data is not None:
            group = self.create_group()
            ds_value = group.create_dataset(
                f"{h5key}/value", dtype=dtype,
                shape=(self.num_entries,) + shape,
                chunks=(self.num_entries,) + shape,
            )
            ds_timestamp = group.create_dataset(
                f"{h5key}/timestamp", dtype="u8",
                shape=(self.num_entries,),
                chunks=(self.num_entries,),
            )
            self._keys[name] = (data, timestamp, ds_value, ds_timestamp)


class InstrumentSource(Source):
    source_name_pattern = re.compile(
        r"^(?P<source>[\w\/-]+):(?P<channel>[\w]+\.[\w]+)$")
    root = "INSTRUMENT"

    def __init__(self, file, name):
        super().__init__(file, name)
        self._count = np.zeros(file._num_trains, np.uint64)
        self._pulse_ids = None
        self._num_entries = 0

    @property
    def name(self):
        return f"{self._source}:{self._channel}"

    @property
    def h5path(self):
        return f"{self.root}/{self._source}:{self._channel.replace('.', '/')}"

    @property
    def h5path_index(self):
        return f"INDEX/{self._source}:{self._channel.replace('.', '/')}"

    @property
    def num_entries(self):
        return self._num_entries

    def set_index(self, count, pulse_ids=None):
        num_entries = np.sum(count, dtype=int)
        if pulse_ids is None:
            train_data = np.all(np.isin(count, [0, 1]))
            if not train_data:
                raise ValueError(
                    "For pulse resolved data, pulse_ids is required")
        else:
            if num_entries != len(pulse_ids):
                raise ValueError(
                    f"the lenght of pulse_ids ({len(pulse_ids)}) must be "
                    f"equal the sum of count ({num_entries})")
            num_trains = self._file._num_trains
            if num_trains != len(count):
                raise ValueError(
                    f"the length of count ({len(count)}) must be equal "
                    f"the number of trains in the file ({num_trains})")
            i0 = 0
            for c in count:
                iN = i0 + c
                if np.any(np.diff(pulse_ids[i0:iN]) <= 0):
                    raise ValueError(
                        "pulse_ids must monotonicaly increase inside a train")
                i0 = iN

        self._count = count
        self._pulse_ids = pulse_ids
        self._num_entries = num_entries

    def write_index(self):
        super().write_index()
        if self._pulse_ids is not None:
            self.add_key("pulseId", self._pulse_ids.astype(np.uint64))

    def write_key(self, name):
        """Writes the data in the key dataset."""
        data, ds = self._keys[name]
        ds[:] = data

    def write_keys(self):
        """Writes data for all keys."""
        for data, ds in self._keys.values():
            ds[:] = data

    def add_key(self, name, data, shape=None, dtype=None):
        if len(data) != self.num_entries:
            raise ValueError(
                "The length of the data must be equal the number of "
                f"entries in the source ({self.num_entries})")

        data_shape = np.shape(data)[1:]
        if shape is None:
            shape = data_shape
        elif data_shape != tuple(shape):
            raise ValueError(
                f"The data shape {data_shape} except first dimentions and "
                f"the value of shape argument {tuple(shape)} must be equal")

        data = np.asarray(data)
        if dtype is None:
            dtype = data.dtype

        group = self.create_group()
        ds = group.create_dataset(
            escape_key(name), shape=(self.num_entries,) + shape, dtype=dtype)
        self._keys[name] = (data, ds)
