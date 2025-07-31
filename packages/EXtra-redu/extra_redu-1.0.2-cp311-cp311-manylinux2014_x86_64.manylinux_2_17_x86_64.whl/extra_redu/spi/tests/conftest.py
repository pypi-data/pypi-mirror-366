import numpy as np
import pytest

num_cells = 31
num_trains = 50


@pytest.fixture(scope="session")
def geom():
    from extra_redu.spi.tests.mock.agipd import AGIPDGeometry

    return AGIPDGeometry(downsample=8)


@pytest.fixture(scope="session")
def mask(geom):
    np.random.seed(seed=2)
    mask = geom.random_mask(num_cells, num_trains)
    return mask


@pytest.fixture(scope="session")
def spi_data(geom):
    from extra_redu.spi.tests.mock.models import spi_ball_scattering

    num_pulses = num_trains * num_cells
    model_param = dict(
        photon_en=6.0,  # keV
        L=1.7,  # m
        R=35,  # nm
        flow_size=12,  # um
        beam_size=1.5,  # um
        pulse_energy=1.8,  # mJ
        pulse_energy_rmsd=0.010,  # mJ
        # gas parameters
        gas_ambient=0.02,
        gas_shape=4e-5,
    )

    np.random.seed(seed=10)
    adu = spi_ball_scattering(geom, num_pulses, **model_param)
    return adu


@pytest.fixture(scope="session")
def spi_run(geom, mask, spi_data):
    from extra_redu.fileutils.tests.mock.extra_data import (
        MockDataCollection, MockSourceData)

    train_ids = list(range(10001, 10001 + num_trains))
    detector_id = "SPB_DET_AGIPD1M-1"
    source_names = [f"{detector_id}/CORR/{modno}CH0:output"
                    for modno in range(16)]

    cellId = np.tile(
        np.arange(num_cells, dtype=np.int32) + 1, num_trains)[:, None]
    pulseId = cellId.astype(np.uint64) * 4
    trainId = np.repeat(
        np.array(train_ids, dtype=np.uint64), num_cells)[:, None]
    count = np.full(num_trains, num_cells)
    data = {}
    for modno, source_id in enumerate(source_names):
        module_data = {
            "image.data": spi_data[:, modno],
            "image.mask": mask[:, modno],
            "image.cellId": cellId,
            "image.pulseId": pulseId,
            "image.trainId": trainId,
        }
        data[source_id] = MockSourceData(
            source_id, train_ids, count, module_data)

    return MockDataCollection.mock(train_ids, data=data)


@pytest.fixture(scope="session")
def litpx_counter(spi_run):
    from extra_redu.fileutils import StackedPulseSource
    from extra_redu.spi import LitPixelCounter

    detector_id = "SPB_DET_AGIPD1M-1"
    sources_ptrn = detector_id + r"/CORR/(?P<key>\d+)CH0:output"
    src = StackedPulseSource.from_datacollection(
        spi_run, sources_ptrn, "image")

    litpx_counter = LitPixelCounter(src)
    litpx_counter(src)

    return litpx_counter


@pytest.fixture()
def spi_ref():
    hit_ix = np.array([
           4,   54,  182,  198,  322,  398,  414,  420,  456,  535,  568,  # noqa: E131, E501
         626,  645,  652,  681,  703,  708,  728,  751,  752,  776,  884,  # noqa: E131, E501
         941,  956,  967,  991,  999, 1014, 1020, 1046, 1092, 1102, 1111,  # noqa: E131, E501
        1149, 1176, 1222, 1250, 1344, 1387, 1452, 1460, 1479, 1544, 1546,  # noqa: E131, E501
    ])
    miss_ix = np.array([
          66,   80,   98,  102,  112,  127,  177,  180,  188,  196,  210,  # noqa: E131, E501
         241,  407,  416,  459,  468,  471,  523,  557,  574,  666,  669,  # noqa: E131, E501
         684,  713,  767,  778,  787,  804,  808,  809,  902,  922, 1075,  # noqa: E131, E501
        1090, 1112, 1194, 1229, 1252, 1254, 1281, 1284, 1381, 1395, 1497,  # noqa: E131, E501
    ])
    data_ix = np.sort(np.concatenate([hit_ix, miss_ix]))

    data_hitscore = np.array([
        58254, 45197,  14563, 12787,  7943,      0,  6393,  5577, 13797,  # noqa: E131, E501
         6096, 55606,   5825, 28493, 39042,   6898, 13797, 55775, 48289,  # noqa: E131, E501
            0, 71493,      0, 96879, 62086,  12192,     0,     0, 15887,  # noqa: E131, E501
        78643,  6721, 113975, 12192, 73156, 103638, 61352, 10922, 12787,  # noqa: E131, E501
        47051,  5825,  97367, 48289, 31207,  49152, 45875, 45875,     0,  # noqa: E131, E501
        55775,  5577,  22310,  5957,  5825,  11155, 42674,     0, 18078,  # noqa: E131, E501
        65536, 55188,  60963, 53773, 85196,  62086, 26886, 36157,     0,  # noqa: E131, E501
         7943, 52428,  45590, 48289,     0,  58254, 29789, 18289, 36578,  # noqa: E131, E501
         6721, 62686,  22310, 12483, 11397,      0, 53620,  5698, 90394,  # noqa: E131, E501
            0, 62086,  61352, 96579, 15123, 103638, 71493,  # noqa: E131, E501
    ])
    return type("SpiHitfinderReference", (), dict(
        hit_ix=hit_ix, miss_ix=miss_ix, data_ix=data_ix,
        data_hitscore=data_hitscore,
    ))


@pytest.fixture()
def spi_adaptive_threshold():
    threshold = np.array([
        42257.264974498874, 41659.026331396040, 42873.295101411460, 44938.767761831354,  # noqa: E131, E501
        30208.283477642035, 31272.332819357136, 31602.542758866093, 39601.475269837510,  # noqa: E131, E501
        44222.196892420834, 47632.517020519510, 47809.517020519510, 43913.182066184320,  # noqa: E131, E501
        44814.617245878310, 48256.604554619870, 48256.604554619870, 41217.661843197726,  # noqa: E131, E501
        35684.712252401850, 37852.699679753290, 51741.434942474200, 37799.909619262250,  # noqa: E131, E501
        47142.819475744276, 40639.347882813425, 43999.333649626380, 47525.886846162970,  # noqa: E131, E501
        43159.333649626380, 49433.167832997286, 25530.706084687463, 41126.009132961706,  # noqa: E131, E501
        41723.921598861340, 43736.182066184320, 44814.617245878310, 34214.853872612980,  # noqa: E131, E501
        26249.203890404460, 26139.252520460206, 27017.202941525324, 28868.433044715930,  # noqa: E131, E501
        33054.537895860514, 28867.517257739295, 35325.917328905230, 35139.817933815680,  # noqa: E131, E501
        37411.197366860400, 41579.184794211830, 44602.818764084920, 43266.256078756970,  # noqa: E131, E501
        41823.909619262250, 55549.971415016030, 45365.477642035345, 36249.250741311830,  # noqa: E131, E501
        39464.862886964780, 46933.743861938085,  # noqa: E131, E501
    ])
    return threshold
