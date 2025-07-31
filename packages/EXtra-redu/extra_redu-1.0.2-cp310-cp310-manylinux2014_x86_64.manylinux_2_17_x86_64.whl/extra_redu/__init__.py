# coding: utf-8

__version__ = "0.0.8"

from .lossy.rounding import errb_round
from .litfrm.agipd_offline import (
    AgipdLitFrameFinderOffline, AgipdLitFrameFinderMID,
    AgipdLitFrameFinderSPB, AgipdLitFrameFinderHED,
    LitFrameFinderError, BunchPatternNotFound, DetectorNotFound,
    TriggerNotFound, NoReferenceDelay, make_litframe_finder,
    AgipdLitFrameFinderBase, DESTINATION, AGIPD_MAX_CELL,
    ReferenceDelay,
)
from .litfrm.selection import FrameSelection, SelType
