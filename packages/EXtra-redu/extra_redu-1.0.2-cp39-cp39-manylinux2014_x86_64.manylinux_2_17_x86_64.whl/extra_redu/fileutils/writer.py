import functools

import h5py
import numpy as np

from .datafile import DataFile


def exdf_translate(name):
    """Translates python member name in EXDF key name."""
    if not name:
        return name
    name = ''.join(name.replace('_', ' ').title().split())
    return name[0].lower() + name[1:]


def exdf_property(name=None, omit=False):
    if callable(name):
        func = name
        func.__exdf_property = exdf_translate(func.__name__)
        func.__exdf_omit = omit
        return func

    def exdf_property_decorator(func):
        func.__exdf_property = name
        func.__exdf_omit = omit
        return func

    return exdf_property_decorator


def exdf_constant(name=None, omit=False):
    func_or_name = name
    name = None if callable(func_or_name) else func_or_name

    def exdf_constant_decorator(func):
        @functools.wraps(func)
        def exdf_property_wrapper(self, train_ids=None):
            value = func(self)
            shape = np.shape(value)
            n = 1 if train_ids is None else len(train_ids)
            return (np.broadcast_to(value, (n,) + shape),
                    np.broadcast_to(np.uint64(0), n))

        exdf_property_wrapper.__exdf_property = (exdf_translate(func.__name__)
                                                 if name is None else name)
        exdf_property_wrapper.__exdf_omit = omit
        return exdf_property_wrapper

    return (exdf_constant_decorator(func_or_name)
            if callable(func_or_name) else exdf_constant_decorator)


def exdf_constant_string(max_len, name=None, omit=False):
    def exdf_constant_string_decorator(func):
        @functools.wraps(func)
        def exdf_property_wrapper(self, train_ids=None):
            value = np.asarray(func(self), dtype=(bytes, max_len))
            shape = np.shape(value)
            n = 1 if train_ids is None else len(train_ids)
            return (np.broadcast_to(value, (n,) + shape),
                    np.broadcast_to(np.uint64(0), n))

        exdf_property_wrapper.__exdf_property = (exdf_translate(func.__name__)
                                                 if name is None else name)
        exdf_property_wrapper.__exdf_omit = omit
        return exdf_property_wrapper

    return exdf_constant_string_decorator


class ChannelData:
    """Interface class exposes data to write as channel data."""
    def __init__(self, keys, train_ids, count=None, pulse_ids=None):
        num_trains = len(train_ids)
        self.keys = keys
        self.train_ids = train_ids
        if count is None:
            if pulse_ids is not None:
                raise ValueError(
                    "`pulse_ids` must be None for train-resolved data")
            count = np.ones(num_trains, int)
        elif pulse_ids is None:
            if not np.all(count == 1):
                raise ValueError(
                    "`pulse_ids` is required for pulse-resolved data")

        self.pulse_ids = pulse_ids
        self.count = count
        self.reset()

    def items(self):
        """Returns generator to iterate over channel items."""
        return ((name, (arr() if callable(arr) else arr)[self.pulses_selected])
                for name, arr in self.keys.items())

    def select_trains(self, train_ids):
        """Slice channel data in respect of givin list of trains."""
        num_trains = len(train_ids)

        # select trains
        all_train_ids = np.asarray(self.train_ids)
        trains_selected = np.isin(all_train_ids, train_ids)
        pulses_selected = np.repeat(trains_selected, self.count)

        # make index
        trains_available = np.isin(train_ids, all_train_ids[trains_selected])
        count = np.zeros(num_trains, int)
        count[trains_available] = self.count[trains_selected]

        self.trains_selected = trains_selected
        self.pulses_selected = pulses_selected
        self.count_selected = count

    def reset(self):
        """Reset channel data slice."""
        self.trains_selected = np.s_[:]
        self.pulses_selected = np.s_[:]
        self.count_selected = self.count


def exdf_type_cast(dtype):
    """Retruns EXDF file data type for given numpy data type"""
    # exdf type cast convention
    if dtype.type == np.bool_:
        exdf_dtype = np.uint8
    elif dtype.type == np.str_:
        exdf_dtype = h5py.string_dtype(encoding='utf-8', length=dtype.itemsize)
    elif dtype.type == np.bytes_:
        exdf_dtype = h5py.string_dtype(encoding='ascii', length=dtype.itemsize)
    else:
        exdf_dtype = dtype
    return exdf_dtype


def add_properties(source, processor, train_ids, run_values):
    """Adds properties (control data) to one data source."""
    properties = find_properties(processor)
    source.set_index()
    for name, get_prop in properties.items():
        if name in run_values:
            run_value, run_timestamp = run_values[name]
        else:
            run_values[name] = (run_value, run_timestamp) = get_prop()

        dtype = exdf_type_cast(run_value.dtype)
        arr, ts = (None, None) if get_prop.__exdf_omit else get_prop(train_ids)
        source.add_key(name, run_value, run_timestamp, arr, ts, dtype=dtype)


def add_channel_data(source, channel, train_ids):
    """Adds data (instrument data) to one channel."""
    channel.select_trains(train_ids)
    pulse_ids = (None if channel.pulse_ids is None
                 else channel.pulse_ids[channel.pulses_selected])
    source.set_index(channel.count_selected, pulse_ids)
    for key, arr in channel.items():
        if key == "pulseId":
            continue
        source.add_key(key, arr, dtype=exdf_type_cast(arr.dtype))
    channel.reset()


def find_properties(processor):
    """Looks for exdf property decorators in source"""
    all_members = ((name, getattr(processor, name)) for name in dir(processor))
    return {member.__exdf_property: member
            for name, member in all_members
            if getattr(member, "__exdf_property", None)}


def exdf_save(folder, aggregator, run, processors={}, train_ids=None,
              sequence_size=3500):
    """Writes sources in the sequence of EXDF files.

    Parameters
    ----------
    folder: str
        Output directory
    aggregator: str
        Aggregator name
    run: int
        Run number
    sources: dict
        The map of source names to data sources
    train_ids: list
        The list of train IDs to store, if None use union of train IDs
        from all sources
    sequence_size: int
        the size of on sequence file in trains
    """
    if train_ids is None:
        train_ids = set()
        for proc in processors.values():
            train_ids.update(proc.train_ids)
        train_ids = sorted(train_ids)

    run_values = {}
    num_trains = len(train_ids)
    for seqno, trn0 in enumerate(range(0, num_trains, sequence_size)):
        seq_train_ids = train_ids[trn0:trn0 + sequence_size]
        num_seq_trains = len(seq_train_ids)

        file = DataFile.from_details(
            folder, aggregator=aggregator, run=run, sequence=seqno,
            max_trains=num_seq_trains)

        slow = {}
        fast = {}
        for source_name, proc in processors.items():
            slow[source_name] = file.create_source(source_name)
            fast[source_name] = {
                ch: file.create_source(f"{source_name}:{ch}")
                for ch in proc._channels
            }

        file.write_index(seq_train_ids)
        file.write_schema()

        for source_name, proc in processors.items():
            # properties (slow)
            control_source = slow[source_name]
            add_properties(control_source, proc, seq_train_ids,
                           run_values.setdefault(source_name, {}))

            # channels (fast)
            channel_groups = fast[source_name]
            for name, ch in proc._channels.items():
                inst_source = channel_groups[name]
                add_channel_data(inst_source, ch, seq_train_ids)

        file.write_data()
        file.close()
