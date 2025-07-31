import pytest
import numpy as np
import h5py
from copy import deepcopy
from unittest.mock import MagicMock
from extra_redu import AgipdLitFrameFinderMID, LitFrameFinderError


def make_fast_data():
    bp = np.zeros([5, 2700], np.uint32)
    bp[:, np.arange(1164, 2549, 8)] = 34603049  # SA1
    bp[:, np.arange(200, 633, 48)] = 67634217  # SA2
    bp[:, np.arange(1166, 2551, 4)] = 135266345  # SA3

    bp_tid = np.arange(1354949955, 1354949960)

    en = 900 + 100*np.cos(np.linspace(0, np.pi, 10))
    cf = np.linspace(1, 0.9, 4)
    xgm_en = np.ones([4, 1000], np.float32)
    xgm_en[:, :10] = np.outer(cf, en)

    sig = 900 + 100*np.sin(np.linspace(0, np.pi, 10))
    cf = np.linspace(.1, 0.09, 4)
    xgm_sig = np.ones([4, 1000], np.float32)
    xgm_sig[:, :10] = np.outer(cf, sig)

    xgm_tid = np.arange(1354949956, 1354949960)

    r = {
        'MID_RR_UTC/TSYS/TIMESERVER:outputBunchPattern': {
            'data.bunchPatternTable': {
                'tid': bp_tid,
                'data': bp,
            },
        },
        'SA2_XTD1_XGM/XGM/DOOCS:output': {
            'data.intensityTD': {
                'tid': xgm_tid,
                'data': xgm_en,
            },
            'data.intensitySigmaTD': {
                'tid': xgm_tid,
                'data': xgm_sig,
            },
        },
    }
    return r


fast = make_fast_data()
slow1 = {
    'MID_EXP_AGIPD1M1/MDL/FPGA_COMP': {
        'classId': 'AgipdComposite',
        'deviceId': 'MID_EXP_AGIPD1M1/MDL/FPGA_COMP',
        'bunchStructure.nPulses': 352,
        'bunchStructure.firstPulse': 0,
        'bunchStructure.repetitionRate': 2.2,
        'patternType': 'XRay',
        'patternTypeIndex': 0,
        'integrationTime': 20,
        't0Delay': 0,
    },
    'MID_EXP_AGIPD1M1/REDU/LITFRM': {
        'detectorId': 'MID_EXP_AGIPD1M1/MDL/FPGA_COMP',
        'alignMethod': 'by first pulse',
        'instrumentName': 'MID',
        'referenceFrame': 1,
        'trigger.deviceId': 'MID_EXP_SYS/TSYS/UTC-2-S4',
        'trigger.name': 'backTrg3',
        'motor.deviceId': 'MID_AGIPD_MOTION/MDL/DOWNSAMPLER',
        'motor.positionProperty': 't4EncoderPosition',
        'motor.unitConversionCoef': 1e-3,
        'referenceDelay.dynamic.delay': 6381852,
        'referenceDelay.dynamic.pulse': 0,
        'referenceDelay.dynamic.frame': 1,
        'referenceDelay.dynamic.repetitionRate': 2.2,
        'referenceDelay.dynamic.position': 6455.7,
        'referenceDelay.static.delay': 1944251,
        'referenceDelay.static.pulse': 100,
        'referenceDelay.static.frame': 1,
        'referenceDelay.static.repetitionRate': 2.2,
        'referenceDelay.static.position': 6455.7,
    },
}
slow2 = deepcopy(slow1)
slow2.update({
    'MID_EXP_SYS/TSYS/UTC-2-S4': {
        'backTrg3.delay': 6381900,
        'backTrg3.event': 181,
    },
    'MID_AGIPD_MOTION/MDL/DOWNSAMPLER': {
        't4EncoderPosition': 132820.05,
    }
})
slow2['MID_EXP_AGIPD1M1/REDU/LITFRM']['alignMethod'] = 'by reference delay'


def log_get_run_value(src, key, slow):
    return slow[src][key]


def log_keydata(item):
    src, key = item
    keydata = MagicMock()
    r = fast[src][key]
    keydata.ndarray.return_value = r['data']
    keydata.train_id_coordinates.return_value = r['tid']
    return keydata


def log_get_source_data(dev_id, slow):
    print(f"get_source_data({dev_id})")
    src_keys = slow[dev_id]
    src_path = "RUN/" + dev_id

    node = MagicMock(spec=h5py.Group)
    node.__contains__.return_value = False

    leaf = MagicMock(spec=h5py.Group)
    leaf.__contains__.side_effect = lambda a: a == "value"

    filekeys = {src_path: node}
    for key in src_keys.keys():
        path = src_path
        parts = key.split('.')
        for name in parts[:-1]:
            path += '/' + name
            filekeys[path] = node
        path += '/' + parts[-1]
        filekeys[path] = leaf

    srcfile = MagicMock()
    srcfile.file = filekeys

    srcdata = MagicMock()
    srcdata.files = [srcfile]
    return srcdata


def test_agipdlitframefinder_offline_alignment_by_first_pulse():
    run = MagicMock()
    run.control_sources = []

    errmsg = "Source 'MID_EXP_AGIPD1M1/MDL/FPGA_COMP' is not found."
    with pytest.raises(LitFrameFinderError, match=errmsg):
        dev = AgipdLitFrameFinderMID(run)
        dev.process()

    run.control_sources = [
        'MID_EXP_AGIPD1M1/REDU/LITFRM',
        'MID_EXP_AGIPD1M1/MDL/FPGA_COMP',
    ]
    run.get_run_value.side_effect = (
        lambda src, key: log_get_run_value(src, key, slow1))

    run._get_source_data.side_effect = (
        lambda src: log_get_source_data(src, slow1))

    dev = AgipdLitFrameFinderMID(run)

    run.instrument_sources = [dev.bunch_pattern_id, dev.xgm_id]
    run.__getitem__.side_effect = log_keydata

    r = dev.process()

    assert dev._detector.bunchStructure.nPulses.value == 352
    assert dev._detector.bunchStructure.firstPulse.value == 0
    assert dev._detector.bunchStructure.repetitionRate.value == 2.2
    assert dev._detector.patternType.value == 'XRay'
    assert dev._detector.patternTypeIndex.value == 0
    assert dev._detector.integrationTime.value == 20
    assert dev._detector.t0Delay.value == 0

    tid_orig = fast[dev.bunch_pattern_id]['data.bunchPatternTable']['tid']

    lit_ix = np.arange(1, 218, 24, dtype=np.uint16)
    litframe = np.repeat(np.pad(lit_ix, [0, 342])[None, ...], 5, axis=0)

    det_pid = np.arange(0, 703, 2, dtype=np.uint16)
    det_pid = np.repeat(det_pid[None, ...], 5, axis=0)

    npulse = np.zeros([5, 352], dtype=np.uint16)
    npulse[:, lit_ix] = 1

    pid = np.pad(2 * (lit_ix - 1) + 200, [0, 2690])
    pid = np.repeat(pid[None, ...], 5, axis=0)
    xgm_pid = np.arange(10, dtype=np.uint16)
    xgm_pid = np.repeat(np.pad(xgm_pid, [0, 2690])[None, ...], 5, axis=0)

    xgm_data = fast['SA2_XTD1_XGM/XGM/DOOCS:output']
    xgm_en = np.zeros([5, 352], dtype=np.float32)
    xgm_en[1:, lit_ix] = xgm_data['data.intensityTD']['data'][:, :10]
    xgm_en[0, lit_ix] = dev.missedIntensityTD.value

    xgm_sig = np.zeros([5, 352], dtype=np.float32)
    xgm_sig[1:, lit_ix] = xgm_data['data.intensitySigmaTD']['data'][:, :10]
    xgm_sig[0, lit_ix] = dev.missedIntensitySigmaTD.value

    np.testing.assert_array_equal(r.meta.trainId, tid_orig)
    np.testing.assert_array_equal(r.nPulse.value, [10] * 5)
    np.testing.assert_array_equal(r.nFrame.value, [352] * 5)
    np.testing.assert_array_equal(r.nLitFrame.value, [10] * 5)
    np.testing.assert_array_equal(r.litFrames.value, litframe)
    np.testing.assert_array_equal(r.nDataFrame.value, [10] * 5)
    np.testing.assert_array_equal(r.dataFrames.value, litframe)

    np.testing.assert_array_equal(r.output.nFrame, [352] * 5)
    np.testing.assert_array_equal(r.output.detectorPulseId, det_pid)
    np.testing.assert_array_equal(r.output.nPulsePerFrame, npulse)
    np.testing.assert_array_equal(r.output.dataFramePattern, npulse != 0)
    np.testing.assert_array_equal(r.output.masterPulseId, pid)
    np.testing.assert_array_equal(r.output.xgmPulseId, xgm_pid)
    np.testing.assert_array_equal(r.output.energyPerFrame, xgm_en)


def test_agipdlitframefinder_offline_alignment_by_reference_delay():
    run = MagicMock()
    run.control_sources = [
        'MID_EXP_AGIPD1M1/REDU/LITFRM',
        'MID_EXP_AGIPD1M1/MDL/FPGA_COMP',
        'MID_AGIPD_MOTION/MDL/DOWNSAMPLER',
    ]
    run.get_run_value.side_effect = (
        lambda src, key: log_get_run_value(src, key, slow2))

    run._get_source_data.side_effect = (
        lambda src: log_get_source_data(src, slow2))

    errmsg = "Source MID_EXP_SYS/TSYS/UTC-2-S4 is not found."
    with pytest.raises(LitFrameFinderError, match=errmsg):
        dev = AgipdLitFrameFinderMID(run)
        dev.process()

    run.control_sources.append('MID_EXP_SYS/TSYS/UTC-2-S4')

    dev = AgipdLitFrameFinderMID(run)

    run.instrument_sources = [dev.bunch_pattern_id, dev.xgm_id]
    run.__getitem__.side_effect = log_keydata

    r = dev.process()

    assert dev._detector.bunchStructure.nPulses.value == 352
    assert dev._detector.bunchStructure.firstPulse.value == 0
    assert dev._detector.bunchStructure.repetitionRate.value == 2.2
    assert dev._detector.patternType.value == 'XRay'
    assert dev._detector.patternTypeIndex.value == 0
    assert dev._detector.integrationTime.value == 20
    assert dev._detector.t0Delay.value == 0

    assert dev.trigger_delay == 6381900
    assert dev.trigger_event == 181
    assert dev.actual_position == pytest.approx(132.82005, 1e-5)

    tid_orig = fast[dev.bunch_pattern_id]['data.bunchPatternTable']['tid']

    lit_ix = np.arange(1, 218, 24, dtype=np.uint16)
    litframe = np.repeat(np.pad(lit_ix, [0, 342])[None, ...], 5, axis=0)

    det_pid = np.arange(0, 703, 2, dtype=np.uint16)
    det_pid = np.repeat(det_pid[None, ...], 5, axis=0)

    npulse = np.zeros([5, 352], dtype=np.uint16)
    npulse[:, lit_ix] = 1

    pid = np.pad(2 * (lit_ix - 1) + 200, [0, 2690])
    pid = np.repeat(pid[None, ...], 5, axis=0)
    xgm_pid = np.arange(10, dtype=np.uint16)
    xgm_pid = np.repeat(np.pad(xgm_pid, [0, 2690])[None, ...], 5, axis=0)

    xgm_data = fast['SA2_XTD1_XGM/XGM/DOOCS:output']
    xgm_en = np.zeros([5, 352], dtype=np.float32)
    xgm_en[1:, lit_ix] = xgm_data['data.intensityTD']['data'][:, :10]
    xgm_en[0, lit_ix] = dev.missedIntensityTD.value

    xgm_sig = np.zeros([5, 352], dtype=np.float32)
    xgm_sig[1:, lit_ix] = xgm_data['data.intensitySigmaTD']['data'][:, :10]
    xgm_sig[0, lit_ix] = dev.missedIntensitySigmaTD.value

    np.testing.assert_array_equal(r.meta.trainId, tid_orig)
    np.testing.assert_array_equal(r.nPulse.value, [10] * 5)
    np.testing.assert_array_equal(r.nFrame.value, [352] * 5)
    np.testing.assert_array_equal(r.nLitFrame.value, [10] * 5)
    np.testing.assert_array_equal(r.litFrames.value, litframe)
    np.testing.assert_array_equal(r.nDataFrame.value, [10] * 5)
    np.testing.assert_array_equal(r.dataFrames.value, litframe)

    np.testing.assert_array_equal(r.output.nFrame, [352] * 5)
    np.testing.assert_array_equal(r.output.detectorPulseId, det_pid)
    np.testing.assert_array_equal(r.output.nPulsePerFrame, npulse)
    np.testing.assert_array_equal(r.output.dataFramePattern, npulse != 0)
    np.testing.assert_array_equal(r.output.masterPulseId, pid)
    np.testing.assert_array_equal(r.output.xgmPulseId, xgm_pid)
    np.testing.assert_array_equal(r.output.energyPerFrame, xgm_en)
