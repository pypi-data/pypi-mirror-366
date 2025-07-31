import numpy as np
import sharedmem
from extra_redu.fileutils import (
    ChannelData, StackedPulseKeyProxy, exdf_constant)


class LitPixelCounter:
    def __init__(self, src, threshold=0.7, max_modules=16):
        self.threshold = threshold
        self.num_events = src.num_events
        self.num_sources = src.num_sources
        self.num_modules = self.num_sources

        s = [self.num_events, self.num_modules]
        self.total_intensity = sharedmem.empty(s, int)
        self.num_lit_px = sharedmem.empty(s, int)
        self.num_unmasked_px = sharedmem.empty(s, int)

        self.trainId = np.copy(src.trainId)
        self.pulseId = np.copy(src.pulseId)
        self.train_ids = list(src.train_ids)
        self.num_trains = len(src.train_ids)
        self.count = np.copy(src.count)
        self.first = np.copy(src.first)
        self.mask = np.copy(src.mask)

        self.data_keys = {
            "pulseId": self.pulseId,
            "trainId": self.trainId,
            "litPixels": self.num_lit_px,
            "unmaskedPixels": self.num_unmasked_px,
            "totalIntensity": self.total_intensity,
        }
        self.modules = [
            int(s.source.split('/')[-1].split(':')[0][:-3])
            for s in src.sources]
        self.max_modules = max(max_modules, len(self.modules))

        # exdf channels
        self._channels = {
            "output.data": ChannelData(
                self.data_keys, self.train_ids, self.count, self.pulseId)
        }

    def __call__(self, src):
        self.process(src)

    def __getitem__(self, name):
        return StackedPulseKeyProxy(self.data_keys[name])

    @exdf_constant
    def _modules(self):
        modules = np.zeros(self.max_modules, np.int8)
        modules[:len(self.modules)] = self.modules
        return modules

    @exdf_constant
    def _num_modules(self):
        return len(self.modules)

    @exdf_constant
    def _threshold(self):
        return self.threshold

    def process(self, src):
        """Computes number of lit-pixels."""
        image = src["data"].ndarray(fill_value=0)
        mask = src["mask"].ndarray(fill_value=1) == 0

        ix = np.flatnonzero(np.isin(self.trainId, src.train_ids))

        self.total_intensity[ix] = np.sum(
            image, axis=(-2, -1), initial=0, where=mask)

        self.num_lit_px[ix] = np.sum(
            image > self.threshold, axis=(-2, -1),
            initial=0, where=mask)

        self.num_unmasked_px[ix] = np.sum(mask, axis=(-2, -1))
