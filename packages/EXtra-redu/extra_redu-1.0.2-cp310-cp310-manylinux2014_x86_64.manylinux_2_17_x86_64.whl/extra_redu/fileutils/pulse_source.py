import numpy as np


class PulseSource:
    evt_id_dtype = np.dtype([('tid', np.uint64), ('pid', np.uint64)])

    def __init__(self, train_ids, count, pulse_ids, data):
        self.train_ids = train_ids
        self.pulseId = pulse_ids
        self.trainId = np.repeat(train_ids, count)
        self.data = data
        self.evt_id = self._make_event_id(self.trainId, self.pulseId)

    def _make_event_id(self, tid, pid):
        num_events = len(tid)
        evt_id = np.zeros(num_events, dtype=self.evt_id_dtype)
        evt_id['tid'] = tid
        evt_id['pid'] = pid
        return evt_id

    def get_array(self, key, tid, pid, fill_value=np.nan):
        sel_id = self._make_event_id(tid, pid)
        ix = np.searchsorted(self.evt_id, sel_id)
        evt_id = np.concatenate([self.evt_id, np.zeros(1, self.evt_id_dtype)])
        found = evt_id[ix] == sel_id
        arr = self.data[key]
        res = np.full(len(tid), fill_value, dtype=arr.dtype)
        res[found] = arr[ix[found]]
        return res
