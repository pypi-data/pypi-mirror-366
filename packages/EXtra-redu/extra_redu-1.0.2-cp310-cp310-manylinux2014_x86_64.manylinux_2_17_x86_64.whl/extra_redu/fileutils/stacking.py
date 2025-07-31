import re

import numpy as np
from extra_data.read_machinery import by_id, select_train_ids, split_trains


def find_sources(pattern, all_sources, *, key_type=int):
    """Looks for sources that match the pattern.

    This looks for the sources that match the regex pattern
    and return the sorted list. The pattern is sorted by the
    parameter `key` in the regex pattern or by the source name.
    The substring of `key` group is casted to the `key_type`
    before sorting.

    Parameters
    ----------
    pattern: str
        Regex pattern to match source. The pattern may include
        `key` parameter group which is used to sort sources.
    key_type: object
        The type to cast the string, which match the group `key`.

    Return
    ------
    sources: list of str
        The sorted list of sources that match the pattern.
    """
    source_re = re.compile(pattern)
    sources = {}
    for source_name in all_sources:
        match = source_re.match(source_name)
        if match is None:
            continue
        if "key" in match.groupdict():
            key = key_type(match.group("key"))
        else:
            key = source_name
        sources[key] = source_name

    return [name for key, name in sorted(sources.items())]


class StackedPulseKey:
    def __init__(self, source, key):
        """Creates the intance of StackedPulseKey

        Datasets from different sources identified by the key are
        expected to have the same shape and data type. If the datasets
        have different data types, they are casted to a common data type
        resolved with `numpy.result_type`. If the shape of the datasets
        does not match each other, a `ValueError` is raised.

        Parameters
        ----------
        source: StackedPulseSource
            The stacked source
        key: str
            The key
        """
        self.stack = source
        self.key = f"{source.index_group}.{key}"

    @property
    def dtype(self):
        if not hasattr(self, "_dtype"):
            self._dtype = np.result_type(
                *[np.dtype(src[self.key].dtype) for src in self.stack.sources])

        return self._dtype

    @property
    def shape(self):
        if not hasattr(self, "_shape"):
            shapes = set(src[self.key].shape[1:]
                         for src in self.stack.sources)
            if len(shapes) != 1:
                raise ValueError("Shapes mismatch")

            self._shape = (
                (self.stack.num_events, self.stack.num_sources)
                + shapes.pop()
            )
        return self._shape

    @property
    def default_fill_value(self):
        if not hasattr(self, "_default_fill_value"):
            if np.issubdtype(self.dtype, np.floating):
                self._default_fill_value = np.nan
            elif np.issubdtype(self.dtype, np.integer):
                self._default_fill_value = -1
            else:
                self._default_fill_value = None

        return self._default_fill_value

    def ndarray(self, source_ix=slice(None), fill_value=None):
        """Reads data from a key as a numpy array.

        This reads data from the datasets specified by the key from
        all stacked sources and returns them as a single array.

        Parameters
        ----------
        key: str
            The key of dataset
        source_ix: slice or sequence
            The slicing of the stacked sources by its index
        fill_value:
            The value to fill missed data. If `None` then it is
            set to -1 for integers, `nan` for floats and `None`
            for others

        Return
        ------
        data: numpy.ndarray
            Data from the same key of several different sources
            is stacked in one array.
        """
        if isinstance(source_ix, slice):
            source_ix = range(*source_ix.indices(self.stack.num_sources))
        sources = [self.stack.sources[i] for i in source_ix]
        num_sources = len(sources)

        if fill_value is None:
            fill_value = self.default_fill_value

        shape = (self.stack.num_events, num_sources) + self.shape[2:]
        arr = np.full(shape, fill_value, dtype=self.dtype)

        for src_no, src in enumerate(sources):
            sel = self.stack.mask[:, source_ix[src_no]]
            arr[sel, src_no] = src[self.key].ndarray()

        return arr


class StackedPulseSource:
    def __init__(self, sources, index_group, tid, pid, mask):
        self.num_sources = len(sources)
        self.index_group = index_group

        self.trainId = tid
        self.pulseId = pid
        self.mask = mask
        self.num_events = len(self.pulseId)

        train_ids, self.count = np.unique(tid, return_counts=True)
        self.first = np.cumsum(self.count) - self.count
        self.train_ids = train_ids.tolist()

        self.sources = [src.select_trains(by_id[self.train_ids])
                        for src in sources]

    @classmethod
    def from_sourcelist(cls, sources, index_group):
        """Creates the instance of `StackedPulseSource`

        Parameters
        ----------
        dc: extra_data.DataCollection
            The data collection
        sources: sequence of str
            The sequence of source names to stack
        index_group: str
            The name of index group
        """
        tid, pid, mask = cls._stack_pulse_data(sources, index_group)
        return cls(sources, index_group, tid, pid, mask)

    @classmethod
    def from_datacollection(cls, dc, source_names, index_group,
                            *, key_type=int):
        """Creates the instance of `StackedPulseSource`

        Parameters
        ----------
        dc: extra_data.DataCollection
            The data collection
        source_names: str or sequence of str
            The names of sources to stack. If this is a string,
            then it should be regex pattern, which include
            parametric group named `key` to sort sources.
            If the sequence of string is given, then strings
            are source names and the order is respected.
        index_group: str
            The name of index group
        key_type: object
            The type to cast the string, which match the group `key`.

        Return
        ------
        source: StackedPulseSource
            pulse resolved stacked source
        """
        if isinstance(source_names, str):
            src_list = find_sources(source_names, dc.all_sources,
                                    key_type=key_type)
        else:
            src_list = source_names

        sources = [dc[src_name] for src_name in src_list]
        return cls.from_sourcelist(sources, index_group)

    def _only_tids(self, train_ids):
        sel_mask = np.isin(self.trainId, train_ids)
        return self.__class__(
            self.sources,
            self.index_group,
            self.trainId[sel_mask],
            self.pulseId[sel_mask],
            self.mask[sel_mask]
        )

    def select_trains(self, train_sel):
        return self._only_tids(select_train_ids(self.train_ids, train_sel))

    def split_trains(self, parts=None, trains_per_part=None):
        for sl in split_trains(len(self.train_ids), parts, trains_per_part):
            tids = self.train_ids[sl]
            yield self._only_tids(tids)

    @staticmethod
    def _stack_pulse_data(sources, index_group):
        """Makes the common index and the mask of individual sources."""

        num_sources = len(sources)
        # read indices and pulse Ids for all sources
        first = []
        count = []
        trains = []
        pid = []
        pid_key = f"{index_group}.pulseId"
        for src in sources:
            data_key = src[pid_key]

            trains.append(np.asarray(data_key.train_ids))

            nevt = data_key.data_counts(labelled=False)
            evt0 = np.cumsum(nevt) - nevt
            count.append(nevt)
            first.append(evt0)

            pid.append(data_key.ndarray())

        # make a common train list
        train_ids = np.unique(np.concatenate(trains))

        # make a common pulse resolved index and mask for every source,
        # indicating data availability for a particular event
        evt_tid = []
        evt_pid = []
        evt_msk = []

        trn_ix = np.zeros(num_sources, int)
        for trn_id in train_ids:
            pulses = []
            for src_no, src_trn_no in enumerate(trn_ix):
                if trains[src_no][src_trn_no] == trn_id:
                    evt0 = first[src_no][src_trn_no]
                    evtN = evt0 + count[src_no][src_trn_no]
                    pulses.append(pid[src_no][evt0:evtN])
                    trn_ix[src_no] += 1
                else:
                    pulses.append([])

            pulse_ids = np.unique(np.concatenate(pulses))
            evt_msk.append(np.array([np.isin(pulse_ids, p) for p in pulses]).T)
            evt_pid.append(pulse_ids)
            evt_tid.append(np.full(len(pulse_ids), trn_id, np.uint64))

        evt_pid = np.concatenate(evt_pid, dtype=np.uint64)
        evt_tid = np.concatenate(evt_tid)
        evt_msk = np.vstack(evt_msk)

        return evt_tid, evt_pid, evt_msk

    def __getitem__(self, key):
        return StackedPulseKey(self, key)

    def data_counts(self, labelled=True):
        """Get a count of data entries in each train.

        Parameters
        ----------
        labelled: bool
            Flag, if this is True, returns a pandas series with
            an index of train IDs. Otherwise, returns a NumPy array of
            counts to match ``.train_ids``.

        Return
        ------
        count: numpy.ndarray or pandas.Series
            The count of entries per train
        """
        if labelled:
            import pandas as pd
            return pd.Series(self.count, index=self.train_ids)
        else:
            return self.count

    def train_id_coordinates(self):
        return self.trainId


class StackedPulseKeyProxy:
    def __init__(self, arr):
        self.arr = arr

    @property
    def shape(self):
        return self.arr.shape

    @property
    def dtype(self):
        return self.arr.dtype

    def ndarray(self, source_ix=slice(None), fill_value=None):
        return self.arr[:, source_ix]
