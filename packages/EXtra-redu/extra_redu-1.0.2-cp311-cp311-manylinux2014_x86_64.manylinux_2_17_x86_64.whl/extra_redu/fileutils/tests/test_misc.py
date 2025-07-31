import numpy as np
import pytest
from extra_redu.fileutils.misc import get_wavelenght, get_xgm_sources

from .mock.extra_data import MockDataCollection, MockSourceData


@pytest.fixture
def xgm():
    xgm = [
        'SA1_XTD2_XGM/XGM/DOOCS:output',
        'SPB_XTD9_XGM/XGM/DOOCS:output',
        'SA1_XTD2_XGM/XGM/DOOCS',
        'SPB_XTD9_XGM/XGM/DOOCS',
    ]
    return xgm


@pytest.fixture
def run():
    train_ids = [range(10100, 10200)]
    ones = np.ones(len(train_ids), int)
    # XGM sources
    xgm_data = {
        "pulseEnergy.wavelengthUsed": 0.13776022048133363,
    }
    data = {
        "SA1_XTD2_XGM/XGM/DOOCS": MockSourceData(
            "SA1_XTD2_XGM/XGM/DOOCS", train_ids, ones, xgm_data),
        "SPB_XTD9_XGM/XGM/DOOCS":  MockSourceData(
            "SPB_XTD9_XGM/XGM/DOOCS", train_ids, ones, xgm_data),
    }
    # other sources
    sources = [
        "SA1_XTD2_XGM/XGM/DOOCS:output",
        "SPB_XTD9_XGM/XGM/DOOCS:output",
        "SA1_XTD2_ATT/MDL/MAIN",
        "SPB_IRU_AGIPD1M1/MDL/DATA_SELECTOR",
        "SPB_IRU_AGIPD1M1/MDL/FPGA_COMP",
        "SPB_IRU_AGIPD1M1/REDU/LITFRM",
    ]
    data.update({
        source_id: MockSourceData(source_id, train_ids, ones, {})
        for source_id in sources
    })
    return MockDataCollection.mock(train_ids, data=data)


def test_get_xgm_sources(run, xgm):
    SA1_XGM = [xgm[0], xgm[2]]
    assert sorted(get_xgm_sources(run.all_sources)) == sorted(xgm)
    assert sorted(get_xgm_sources(run.all_sources, 'SA1')) == sorted(SA1_XGM)
    assert sorted(get_xgm_sources(run.all_sources, 'SPB')) == sorted(xgm)


def test_get_wavelenght(run, xgm):
    assert get_wavelenght(run, xgm) == 0.13776022048133363
    assert get_wavelenght(run, xgm, True) == 9
