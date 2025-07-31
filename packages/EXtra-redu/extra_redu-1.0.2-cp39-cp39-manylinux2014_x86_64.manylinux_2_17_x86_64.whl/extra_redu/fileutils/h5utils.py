from collections.abc import Sequence
from datetime import datetime

import h5py


def escape_key(key):
    """Escapes a key name from Karabo to HDF notation."""
    return key.replace('.', '/')


def python_to_h5(value):
    """Casts a python value to type compatible with h5py."""
    if isinstance(value, datetime):
        h5value = value.strftime("%Y%m%dT%H%M%SZ").encode("ascii")
    elif isinstance(value, str):
        h5value = value.encode("ascii")
    else:
        h5value = value
    return h5value


def h5_to_python(h5value):
    """Casts a h5py value to python native type."""
    if isinstance(h5value, bytes):
        value = h5value.decode()
        try:
            value = datetime.strptime(value, "%Y%m%dT%H%M%SZ")
        except ValueError:
            pass
    else:
        value = h5value
    return value


def write_dict(group, data):
    """Writes recursively a dict to h5py file."""
    for key, entry in sorted(data.items()):
        value = entry() if callable(entry) else entry
        if isinstance(value, dict):
            write_dict(group.require_group(key), value)
        elif isinstance(value, Sequence) and not isinstance(value, str):
            value = [python_to_h5(item) for item in value]
            group.create_dataset(key, shape=(len(value),), data=value)
        else:
            value = python_to_h5(value)
            group.create_dataset(key, shape=(1,), data=value)


def read_dict(group):
    """Reads recursively h5py file into a dict."""
    data = {}
    for key, dataset in group.items():
        if isinstance(dataset, h5py.Group):
            value = read_dict(dataset)
        else:
            value = [h5_to_python(item) for item in dataset[:]]
            if len(value) == 1:
                value = value[0]
        data[key] = value
    return data
