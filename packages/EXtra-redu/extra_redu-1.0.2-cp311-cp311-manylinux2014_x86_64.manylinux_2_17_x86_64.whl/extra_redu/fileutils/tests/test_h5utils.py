import datetime

import pytest
from extra_redu.fileutils.h5utils import (
    escape_key, h5_to_python, python_to_h5, read_dict, write_dict)

from .mock.h5py import MockH5Group


def test_escape_key():
    assert (
        escape_key("SPB_DET_AGIPD1M-1/CORR/15CH0:output.image.data")
        == "SPB_DET_AGIPD1M-1/CORR/15CH0:output/image/data")
    assert (
        escape_key("SPB_DET_AGIPD1M-1/REDU/LITPX_COUNTER"
                   ":output.data.litPixels")
        == "SPB_DET_AGIPD1M-1/REDU/LITPX_COUNTER:output/data/litPixels")


def test_python_to_h5():
    val = datetime.datetime(2024, 7, 18, 11, 40, 10)
    assert python_to_h5(val) == b"20240718T114010Z"
    val = datetime.datetime(2024, 12, 8, 7, 5, 5)
    assert python_to_h5(val) == b"20241208T070505Z"
    assert python_to_h5("stringValue") == b"stringValue"
    assert python_to_h5(1) == 1
    assert python_to_h5(1.) == 1.


def test_h5_to_python():
    val = datetime.datetime(2024, 7, 18, 11, 40, 10)
    assert h5_to_python(b"20240718T114010Z") == val
    val = datetime.datetime(2024, 12, 8, 7, 5, 5)
    assert h5_to_python(b"20241208T070505Z") == val
    assert h5_to_python(b"stringValue") == "stringValue"
    assert h5_to_python(1) == 1
    assert h5_to_python(1.) == 1.


@pytest.fixture
def dict_data():
    dict_data = {
        "groupA": {
            "stringA": "abc",
            "timeA": datetime.datetime(2024, 8, 5, 9, 5, 5),
            "floatA": 1.0,
            "intA": 2,
        },
        "groupB": {
            "groupC": {
                "stringC": lambda: "abc",
                "timeC": lambda: datetime.datetime(2024, 8, 5, 9, 5, 5),
            },
            "groupD": {
                "groupE": {},
            },
            "floatB": [1.0, 2.0, 3.0],
            "intB": [1, 2, 3, 4],
        },
        "stringZ": ["abc", "bcd"],
    }
    return dict_data


@pytest.fixture
def h5group_content():
    content = {
        'groupA': {
            'floatA': ((1,), None, 1.0),
            'intA': ((1,), None, 2),
            'stringA': ((1,), None, b'abc'),
            'timeA': ((1,), None, b'20240805T090505Z')
        },
        'groupB': {
            'floatB': ((3,), None, [1.0, 2.0, 3.0]),
            'groupC': {
                'stringC': ((1,), None, b'abc'),
                'timeC': ((1,), None, b'20240805T090505Z')
            },
            'groupD': {
                'groupE': {}
            },
            'intB': ((4,), None, [1, 2, 3, 4])},
        'stringZ': ((2,), None, [b'abc', b'bcd'])
    }
    return content


@pytest.fixture
def dict_resolved(dict_data):
    import copy
    dict_resolved = copy.deepcopy(dict_data)
    dict_resolved["groupB"]["groupC"].update({
        "stringC": "abc",
        "timeC": datetime.datetime(2024, 8, 5, 9, 5, 5),
    })
    return dict_resolved


def test_write_dict(dict_data, h5group_content):
    data = {}
    mock_grp = MockH5Group.mock(data)
    write_dict(mock_grp, dict_data)
    assert data == h5group_content


def test_read_dict(h5group_content, dict_resolved):
    mock_grp = MockH5Group.mock(h5group_content)
    d = read_dict(mock_grp)
    assert d == dict_resolved
