import numpy as np
import h5py

from collections import namedtuple
from extra_data.exceptions import PropertyNameError
from extra_redu.base import (
    AgipdLitFrameFinderBase, ReferenceDelay, AGIPDGEN, EVENT_PULSE,
    AGIPD_MAX_CELL, DESTINATION, SA1, SA2, SA3
)


# Exceptions
class LitFrameFinderError(RuntimeError):
    pass


class SourceNotFound(LitFrameFinderError):
    pass


class BunchPatternNotFound(SourceNotFound):
    pass


class DetectorNotFound(SourceNotFound):
    pass


class TriggerNotFound(SourceNotFound):
    pass


class NoReferenceDelay(LitFrameFinderError):
    pass


AttributeValue = namedtuple('AttributeValue', ['value'])
AVal = AttributeValue


def mangle_device_id(device_id):
    return ''.join(c if c.isalnum() else '_' for c in device_id)


class ExtraDataProxy:
    def __init__(self, dc, dev_id, node=None, data_selector_id=None):

        if dev_id in dc.control_sources:
            self._mangled_dev_id = None
            self._src = dc._get_source_data(dev_id)
            self._src_path = "RUN/" + dev_id
            self._check_path = self._check_device_path
            self._read_run_value = self._get_run_value_from_device
        elif data_selector_id in dc.control_sources:
            self._mangled_dev_id = mangle_device_id(dev_id)
            self._src = dc._get_source_data(data_selector_id)
            self._src_path = '/'.join([
                "RUN", data_selector_id, self._mangled_dev_id])
            self._check_path = self._check_data_selector_path
            self._read_run_value = self._get_run_value_from_data_selector
        else:
            raise SourceNotFound(f"{dev_id} is not found")

        if not self._check_path(self._src, self._src_path, node):
            path = self._src_path
            if node is not None:
                path += '/' + node.replace('.', '/')
            raise SourceNotFound(f"{path} is not found")

        self._dc = dc
        self._dev_id = dev_id
        self._data_selector_id = data_selector_id
        self._node = node
        self._cache_run_value = dict()
        if self._mangled_dev_id and self._node is None:
            self._cache_run_value['deviceId'] = AVal(dev_id)

    def _check_device_path(self, src, src_path, key):
        path = src_path
        if key is not None:
            path += '/' + key.replace('.', '/')
        return path in src.files[0].file

    def _check_data_selector_path(self, src, path, key):
        if path not in src.files[0].file:
            return False
        if key is None:
            return True
        grp = src.files[0].file[path]
        key_name = key.replace('.', '_')
        return any(ds_name.startswith(key_name) for ds_name in grp)

    def get(self, name):
        try:
            return self._cache_run_value[name]
        except KeyError:
            v = self._read_run_value(name)
            self._cache_run_value[name] = v
            return v

    def get_value(self, name):
        return self.get(name).value

    def __getattr__(self, name):
        return self.get(name)

    def _get_run_value_from_device(self, name):
        key = name if self._node is None else self._node + '.' + name
        if not self._check_device_path(self._src, self._src_path, key):
            raise AttributeError(
                f"'{self._dev_id}' does not have property '{name}'")

        path = self._src_path + '/' + key.replace('.', '/')
        grp = self._src.files[0].file[path]
        if isinstance(grp, h5py.Group) and ('value' not in grp):
            return ExtraDataProxy(
                self._dc, self._dev_id, key, self._data_selector_id)
        try:
            # replace to self._src.run_value(key)
            return AVal(self._dc.get_run_value(self._dev_id, key))
        except Exception:
            raise AttributeError(
                f"'{self._dev_id}' does not have property '{name}'")

    def _get_run_value_from_data_selector(self, name):
        key = name if self._node is None else self._node + '.' + name
        if not self._check_data_selector_path(self._src, self._src_path, key):
            raise AttributeError(
                f"'{self._dev_id}' does not have property '{name}'")

        key_path = key.replace('.', '_')
        path = self._src_path + '/' + key_path
        if path not in self._src.files[0].file:
            return ExtraDataProxy(
                self._dc, self._dev_id, key, self._data_selector_id)
        try:
            mangled_key = self._mangled_dev_id + '/' + key_path
            # replace to self._src.run_value(key)
            return AVal(self._dc.get_run_value(
                self._data_selector_id, mangled_key))
        except Exception:
            raise AttributeError(
                f"'{self._dev_id}' does not have property '{name}'")


Trigger = namedtuple('Trigger', ['deviceId', 'name'])
Motor = namedtuple('Motor', ['deviceId', 'positionProperty',
                             'unitConversionCoef'])
ReferenceListNode = namedtuple('ReferenceListNode', ['dynamic', 'static'])


class AgipdLitFrameFinderOffline(AgipdLitFrameFinderBase):

    data_selector_id = None

    alignMethod = AVal('by first pulse')
    referenceFrame = AVal(1)

    missedIntensityTD = AVal(10000)
    missedIntensitySigmaTD = AVal(0)

    useDistanceDelay = AVal(False)
    referenceDelay = ReferenceListNode(**dict([
        (event_name, ReferenceDelay(-1, 0, 1, 4.5, 0.0))
        for event_name in ReferenceListNode._fields
    ]))

    def __init__(self, dev_id, dc, ref_delays={}, align_method=None, **kwargs):
        self.dev_id = dev_id
        self.dc = dc
        self._reference = ref_delays

        for a, v in kwargs.items():
            setattr(self, a, AVal(v))

        if dev_id in dc.control_sources:
            try:
                self._configure(dc, dev_id)
            except (PropertyNameError, AttributeError):
                self._configure_v03(dc, dev_id)

        try:
            self._detector = ExtraDataProxy(
                dc, self.detector_control_id,
                data_selector_id=None  # classId missed in the data selector
            )
        except SourceNotFound:
            raise(DetectorNotFound(
                f"Source '{self.detector_control_id}' is not found."))

        if align_method is not None:
            self.alignMethod = AVal(align_method)

        # inst = self.instrumentName.value
        inst = self._detector.deviceId.value[:3]
        self.dst = DESTINATION[inst]

        self._get_event_pulse = {}
        for event_name, event_code in self.dst.event_code.items():
            ref = getattr(self.referenceDelay, event_name)
            if ref.delay == -1:
                continue
            self._reference[event_code] = ref
            self._get_event_pulse[event_code] = EVENT_PULSE[event_name]

        agipd_class = AGIPDGEN.get(self._detector.classId.value)
        if agipd_class is None:
            raise ValueError(
                f"Unknown class '{agipd_class}' of AgipdComposite device")
        self._agipd = agipd_class(self._detector, self)

        self.shutters_are_open = True
        self.actual_position = None

    def _configure_v03(self, dc, dev_id):
        litfrm = ExtraDataProxy(dc, dev_id)

        self.detector_control_id = litfrm.DetectorCtrl.value
        self.alignMethod = litfrm.alignMethod
        self.instrumentName = litfrm.instrumentName
        self.referenceFrame = litfrm.referenceFrame

        self.trigger = Trigger(
            deviceId=litfrm.Timer.value,
            name=litfrm.trigger,
        )
        self.motor = Motor(
            deviceId='',
            positionProperty='',
            unitConversionCoef=1,
        )

    def _configure(self, dc, dev_id):
        litfrm = ExtraDataProxy(dc, dev_id)

        self.detector_control_id = litfrm.detectorId.value
        self.alignMethod = litfrm.alignMethod
        self.instrumentName = litfrm.instrumentName
        self.referenceFrame = litfrm.referenceFrame

        self.trigger = Trigger(
            deviceId=litfrm.trigger.deviceId.value,
            name=litfrm.trigger.name,
        )
        self.motor = Motor(
            deviceId=litfrm.motor.deviceId.value,
            positionProperty=litfrm.motor.positionProperty,
            unitConversionCoef=litfrm.motor.unitConversionCoef,
        )
        reference_delays = {}
        for event_name in ReferenceListNode._fields:
            reference_delays[event_name] = ReferenceDelay(**dict([
                (key, litfrm.get(f"referenceDelay.{event_name}.{key}").value)
                for key in ReferenceDelay._fields
            ]))
        self.referenceDelay = ReferenceListNode(**reference_delays)
        try:
            self.useDistanceDelay = litfrm.useDistanceDelay
            self.detectorDistance = litfrm.detectorDistance
        except AttributeError:
            self.useDistanceDelay = AVal(True)
            self.detectorDistance = AVal(0.0)

    def _read_run_values(self, dc):
        if self.alignMethod.value == "by reference delay":
            self._read_trigger_and_motor_values(dc)

    def _read_trigger_and_motor_values(self, dc):
        try:
            _timer = ExtraDataProxy(dc, self.trigger.deviceId,
                                    data_selector_id=self.data_selector_id)
        except SourceNotFound:
            raise TriggerNotFound(
                f"Source {self.trigger.deviceId} is not found.")

        key = self.trigger.name.value
        self.trigger_event = _timer.get_value(key + '.event')
        self.trigger_delay = _timer.get_value(key + '.delay')

        self.ref = self._reference.get(self.trigger_event)
        if self.ref is None:
            raise(NoReferenceDelay("Reference delay for marco event "
                                   f"{self.trigger_event} is not set."))

        if self.useDistanceDelay:
            self.actual_position = self.detectorDistance.value * .001
            try:
                _motor = ExtraDataProxy(dc, self.motor.deviceId,
                                        data_selector_id=self.data_selector_id)
                key = self.motor.positionProperty.value
                unit_coef = self.motor.unitConversionCoef.value
                self.actual_position += unit_coef * _motor.get_value(key)
            except SourceNotFound:
                pass

    def _read_pp_decoder(self, dc):
        pp_src = dc[self.pp_decoder_id]
        trainId = pp_src['sase1/nPulses'].train_id_coordinates()
        bunch_pattern = np.zeros([trainId.size, 2700], dtype=np.uint32)
        n1 = pp_src['sase1/nPulses'].ndarray()
        p1 = pp_src['sase1/pulseIds'].ndarray()
        n2 = pp_src['sase2/nPulses'].ndarray()
        p2 = pp_src['sase2/pulseIds'].ndarray()
        n3 = pp_src['sase3/nPulses'].ndarray()
        p3 = pp_src['sase3/pulseIds'].ndarray()
        for i in range(trainId.size):
            bunch_pattern[i, p1[i, :n1[i]]] |= SA1.code
            bunch_pattern[i, p2[i, :n2[i]]] |= SA2.code
            bunch_pattern[i, p3[i, :n3[i]]] |= SA3.code
        return trainId, bunch_pattern

    def process(self, force=False):
        if not force and hasattr(self, 'r'):
            return self.r

        dc = self.dc
        self._read_run_values(dc)

        # bunch pattern
        if self.bunch_pattern_id in dc.instrument_sources:
            bp_keydata = dc[self.bunch_pattern_id, 'data.bunchPatternTable']
            bunch_pattern = bp_keydata.ndarray()
            trainId = bp_keydata.train_id_coordinates()
            bpsrc = "timeserver"
        elif self.pp_decoder_id in dc.control_sources:
            trainId, bunch_pattern = self._read_pp_decoder(dc)
            bpsrc = "pp_decoder"
        elif self._agipd.exp_type.value == 'XRay':
            raise(BunchPatternNotFound(
                f"Neither source '{self.bunch_pattern_id}' nor source "
                f"'{self.pp_decoder_id}' are found."))
        else:
            # only for dark runs
            bpsrc = "none"
            trainId = np.array(dc.train_ids, np.uint64)
            bunch_pattern = None

        # XGM
        if self.xgm_id not in dc.instrument_sources:
            xgm_flag = np.zeros(trainId.size, bool)
        else:
            xgm_en_keydata = dc[self.xgm_id, 'data.intensityTD']
            xgm_sig_keydata = dc[self.xgm_id, 'data.intensitySigmaTD']

            xgm_trainId = xgm_en_keydata.train_id_coordinates()
            xgm_sel = np.isin(xgm_trainId, trainId)
            xgm_trainId = xgm_trainId[xgm_sel]

            xgm_intensityTD = xgm_en_keydata.ndarray()[xgm_sel]
            xgm_intensitySigmaTD = xgm_sig_keydata.ndarray()[xgm_sel]

            xgm_flag = np.isin(trainId, xgm_trainId)
            xgm_map = np.roll(np.cumsum(xgm_flag), 1)
            xgm_map[0] = 0

        Output = namedtuple('Output', [
            'nFrame', 'detectorPulseId', 'nPulsePerFrame', 'energyPerFrame',
            'energySigma', 'dataFramePattern', 'masterPulseId', 'xgmPulseId'
        ])
        Result = namedtuple('Results', [
            'nPulse', 'nFrame', 'litFrames', 'nLitFrame', 'dataFrames',
            'nDataFrame', 'output', 'meta'
        ])
        Meta = namedtuple('Meta', ['litFrmDev', 'trainId'])
        n = trainId.shape[0]
        r = Result(
            nPulse=AVal(np.zeros(n, np.uint16)),
            nFrame=AVal(np.zeros(n, np.uint16)),
            nLitFrame=AVal(np.zeros(n, np.uint16)),
            litFrames=AVal(np.zeros([n, AGIPD_MAX_CELL], np.uint16)),
            nDataFrame=AVal(np.zeros(n, np.uint16)),
            dataFrames=AVal(np.zeros([n, AGIPD_MAX_CELL], np.uint16)),
            output=Output(
                nFrame=np.zeros(n, np.uint16),
                nPulsePerFrame=np.zeros([n, AGIPD_MAX_CELL], np.uint16),
                energyPerFrame=np.zeros([n, AGIPD_MAX_CELL], np.float32),
                energySigma=np.zeros([n, AGIPD_MAX_CELL], np.float32),
                dataFramePattern=np.zeros([n, AGIPD_MAX_CELL], bool),
                detectorPulseId=np.zeros([n, AGIPD_MAX_CELL], np.uint16),
                masterPulseId=np.zeros([n, 2700], np.uint16),
                xgmPulseId=np.zeros([n, 2700], np.uint16),
            ),
            meta=Meta(litFrmDev=f"offline/{bpsrc}", trainId=trainId),
        )

        Data = namedtuple('Data', ['data'])
        BunchPatternTable = namedtuple(
            'BunchPatternTable', ['bunchPatternTable'])
        XGM = namedtuple('XGM', ['intensityTD', 'intensitySigmaTD'])

        for no, tid in enumerate(trainId):
            if bunch_pattern is not None:
                bp = Data(Data(BunchPatternTable(AVal(bunch_pattern[no]))))

                if xgm_flag[no]:
                    xgm_no = xgm_map[no]
                    xgm = Data(Data(XGM(
                        intensityTD=AVal(xgm_intensityTD[xgm_no]),
                        intensitySigmaTD=AVal(xgm_intensitySigmaTD[xgm_no]),
                    )))
                else:
                    xgm = None

                (npulse, ncell,
                 agipd_pulse_ids, frames) = self.process_train(bp, xgm)
            else:
                (npulse, ncell,
                 agipd_pulse_ids, frames) = self.make_dark_run()

            # send pipeline (fast) data
            r.output.nFrame[no] = ncell
            r.output.detectorPulseId[no, :ncell] = agipd_pulse_ids
            r.output.nPulsePerFrame[no, :ncell] = frames.npulse
            r.output.energyPerFrame[no, :ncell] = frames.energy
            r.output.energySigma[no, :ncell] = frames.energy_std
            r.output.dataFramePattern[no, :ncell] = frames.hasdata
            nmaster = frames.master_ids.size
            r.output.masterPulseId[no, :nmaster] = frames.master_ids
            nxgm = frames.xgm_ids.size
            r.output.xgmPulseId[no, :nxgm] = frames.xgm_ids

            litframes = np.flatnonzero(frames.npulse)
            dataframes = np.flatnonzero(frames.hasdata)

            # update attributes (slow data)
            r.nPulse.value[no] = npulse
            r.nFrame.value[no] = ncell
            r.litFrames.value[no, :frames.nlit] = litframes
            r.nLitFrame.value[no] = frames.nlit
            r.dataFrames.value[no, :frames.ndata] = dataframes
            r.nDataFrame.value[no] = frames.ndata

        self.r = r
        return r

    def read(self):
        dc = self.dc
        inst_src = dc[self.dev_id + ':output']
        trainId = inst_src['data.nFrame'].train_id_coordinates()

        Output = namedtuple('Output', [
            'nFrame', 'detectorPulseId', 'nPulsePerFrame', 'energyPerFrame',
            'energySigma', 'dataFramePattern', 'masterPulseId', 'xgmPulseId'
        ])
        Result = namedtuple('Results', [
            'nPulse', 'nFrame', 'litFrames', 'nLitFrame', 'dataFrames',
            'nDataFrame', 'output', 'meta'
        ])
        Meta = namedtuple('Meta', ['litFrmDev', 'trainId'])
        out = Output(
            nFrame=inst_src['data.nFrame'].ndarray(),
            nPulsePerFrame=inst_src['data.nPulsePerFrame'].ndarray(),
            energyPerFrame=inst_src['data.energyPerFrame'].ndarray(),
            energySigma=inst_src['data.energySigma'].ndarray(),
            dataFramePattern=inst_src['data.dataFramePattern'].ndarray(),
            detectorPulseId=inst_src['data.detectorPulseId'].ndarray(),
            masterPulseId=inst_src['data.masterPulseId'].ndarray(),
            xgmPulseId=inst_src['data.xgmPulseId'].ndarray(),
        )

        n = trainId.size
        litframes = np.zeros([n, 352], dtype=np.uint16)
        dataframes = np.zeros([n, 352], dtype=np.uint16)
        for no, tid in enumerate(trainId):
            a = np.flatnonzero(out.nPulsePerFrame[no])
            litframes[no, :a.size] = a
            a = np.flatnonzero(out.dataFramePattern[no])
            dataframes[no, :a.size] = a

        r = Result(
            nPulse=AVal(out.nPulsePerFrame.sum(1)),
            nFrame=AVal(out.nFrame),
            nLitFrame=AVal((out.nPulsePerFrame != 0).sum(1)),
            litFrames=AVal(litframes),
            nDataFrame=AVal(out.dataFramePattern.sum(1)),
            dataFrames=AVal(dataframes),
            output=out,
            meta=Meta(litFrmDev=self.dev_id, trainId=trainId),
        )

        self.r = r
        return r

    def read_or_process(self):
        channel = self.dev_id + ':output'
        if channel in self.dc.instrument_sources:
            r = self.read()
            if len(r.meta.trainId):
                return r

        return self.process(force=True)


class AgipdLitFrameFinderConfigureMID:
    dev_id = "MID_EXP_AGIPD1M1/REDU/LITFRM"
    data_selector_id = 'MID_EXP_AGIPD1M1/MDL/DATA_SELECTOR'

    detector_control_id = "MID_EXP_AGIPD1M1/MDL/FPGA_COMP"
    bunch_pattern_id = "MID_RR_UTC/TSYS/TIMESERVER:outputBunchPattern"
    xgm_id = "SA2_XTD1_XGM/XGM/DOOCS:output"
    pp_decoder_id = "MID_RR_SYS/MDL/PULSE_PATTERN_DECODER"

    trigger = Trigger(
        deviceId="MID_EXP_SYS/TSYS/UTC-2-S4",
        name=AVal("backTrg3")
    )
    motor = Motor(
        deviceId="MID_AGIPD_MOTION/MDL/DOWNSAMPLER",
        positionProperty=AVal("t4EncoderPosition"),
        unitConversionCoef=AVal(1e-3),
    )

    instrumentName = AVal("MID")


class AgipdLitFrameFinderMID(AgipdLitFrameFinderConfigureMID,
                             AgipdLitFrameFinderOffline):
    def __init__(self, dc, dev_id=AgipdLitFrameFinderConfigureMID.dev_id,
                 ref_delays={}, align_method=None, **kwargs):
        super().__init__(self.dev_id, dc, ref_delays, align_method, **kwargs)


class AgipdLitFrameFinderConfigureSPB:
    dev_id = 'SPB_IRU_AGIPD1M1/REDU/LITFRM'
    data_selector_id = 'SPB_IRU_AGIPD1M1/MDL/DATA_SELECTOR'

    detector_control_id = 'SPB_IRU_AGIPD1M1/MDL/FPGA_COMP'
    bunch_pattern_id = 'SPB_EXP_SYS/TSYS/TIMESERVER:outputBunchPattern'
    xgm_id = 'SPB_XTD9_XGM/XGM/DOOCS:output'
    pp_decoder_id = 'SPB_RR_SYS/MDL/BUNCH_PATTERN'

    trigger = Trigger(
        deviceId="SPB_EXP_SYS/TSYS/UTC_1_S3",
        name=AVal("backTrg3")
    )
    motor = Motor(
        deviceId="SPB_IRU_AGIPD1M/MOTOR/Z_STEPPER",
        positionProperty=AVal("encoderPosition"),
        unitConversionCoef=AVal(1e-3),
    )

    instrumentName = AVal('SPB')


class AgipdLitFrameFinderSPB(AgipdLitFrameFinderConfigureSPB,
                             AgipdLitFrameFinderOffline):
    def __init__(self, dc, dev_id=AgipdLitFrameFinderConfigureSPB.dev_id,
                 ref_delays={}, align_method=None, **kwargs):
        super().__init__(self.dev_id, dc, ref_delays, align_method, **kwargs)


class AgipdLitFrameFinderConfigureHED:
    dev_id = 'HED_EXP_AGIPD500K2G/REDU/LITFRM'

    detector_control_id = 'HED_EXP_AGIPD500K2G/MDL/FPGA_COMP'
    bunch_pattern_id = 'HED_RR_UTC/TSYS/TIMESERVER:outputBunchPattern'
    xgm_id = 'HED_XTD6_XGM/XGM/DOOCS:output'
    pp_decoder_id = 'SA2_BR_UTC/MDL/BUNCHPATTERN_DECODER'

    trigger = Trigger(
        deviceId="HED_EXP_SYS/TSYS/UTC-1-S2",
        name=AVal("backTrg3")
    )
    motor = Motor(
        deviceId="",
        positionProperty=AVal(""),
        unitConversionCoef=AVal(1),
    )

    instrumentName = AVal('HED')


class AgipdLitFrameFinderHED(AgipdLitFrameFinderConfigureHED,
                             AgipdLitFrameFinderOffline):
    def __init__(self, dc, dev_id=AgipdLitFrameFinderConfigureHED.dev_id,
                 ref_delays={}, align_method=None, **kwargs):
        super().__init__(self.dev_id, dc, ref_delays, align_method, **kwargs)


AgipdLitFrameFinderProfiles = {
    "MID": AgipdLitFrameFinderMID,
    "SPB": AgipdLitFrameFinderSPB,
    "HED": AgipdLitFrameFinderHED,
}


def find_litframe_finder_sources(dc):
    litfrm_finder_ids = []
    for src in dc.control_sources:
        try:
            class_id = dc.get_run_value(src, 'classId')
            if class_id == 'AgipdLitFrameFinder':
                litfrm_finder_ids.append(src)
        except PropertyNameError:
            pass
    return litfrm_finder_ids


def make_litframe_finder(inst, dc, dev_id=None, ref_delays={},
                         align_method=None):
    if inst not in AgipdLitFrameFinderProfiles:
        raise IndexError("Unexpected name of AgipdLitFrameFinder profile")

    litfrm_finder_cls = AgipdLitFrameFinderProfiles[inst]
    dev_ids = find_litframe_finder_sources(dc)

    if not dev_id:
        dev_id = litfrm_finder_cls.dev_id

    if dev_ids and dev_id not in dev_ids:
        dev_id = dev_ids[0]

    return litfrm_finder_cls(dc, dev_id, ref_delays=ref_delays,
                             align_method=align_method)
