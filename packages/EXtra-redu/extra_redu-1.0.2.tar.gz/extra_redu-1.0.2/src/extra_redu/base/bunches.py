from euxfel_bunch_pattern import (
    DESTINATION_MASK, PHOTON_LINE_DEFLECTION, DESTINATION_T4D, DESTINATION_T5D
)


class ParamDecoder:
    """Decodes Bunch Pattern"""

    @classmethod
    def get_instrument_pulse_mask(cls, bunch):
        return (bunch & cls.mask) == cls.code

    @classmethod
    def get_xgm_pulse_mask(cls, bunch):
        xgm_pulses = (bunch & cls.mask_xgm) == cls.code_xgm
        inst_pulses = (bunch & cls.mask) == cls.code
        return inst_pulses[xgm_pulses]

    @classmethod
    def get_xgm_pulse_mask_in_file(cls, bunch, xgm_maxlen=1000):
        xgm_pulses = (bunch & cls.mask_xgm) == cls.code_xgm
        inst_pulses = (bunch & cls.mask) == cls.code
        return inst_pulses[xgm_pulses]


class SA1(ParamDecoder):
    """SASE 1 Bunch Pattern Decoder"""
    mask = PHOTON_LINE_DEFLECTION | DESTINATION_MASK
    code = DESTINATION_T4D
    mask_xgm = DESTINATION_MASK
    code_xgm = DESTINATION_T4D
    event_code = {"dynamic": 180, "static": 16}
    xgm_key = "Sa1"
    pp_key = "sase1"


class SA2(ParamDecoder):
    """SASE 2 Bunch Pattern Decoder"""
    mask = DESTINATION_MASK
    code = DESTINATION_T5D
    mask_xgm = DESTINATION_MASK
    code_xgm = DESTINATION_T5D
    event_code = {"dynamic": 181, "static": 16}
    xgm_key = ""
    pp_key = "sase2"


class SA3(ParamDecoder):
    """SASE 3 Bunch Pattern Decoder"""
    mask = PHOTON_LINE_DEFLECTION | DESTINATION_MASK
    code = PHOTON_LINE_DEFLECTION | DESTINATION_T4D
    mask_xgm = DESTINATION_MASK
    code_xgm = DESTINATION_T4D
    event_code = {"dynamic": 182, "static": 16}
    xgm_key = "Sa3"
    pp_key = "sase3"


DESTINATION = {
    'SPB': SA1, 'FXE': SA1,
    'MID': SA2, 'HED': SA2,
    'SQS': SA3, 'SCS': SA3,
}
