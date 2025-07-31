import matplotlib.pyplot as plt
import numpy as np
from extra_redu.fileutils import (
    ChannelData, exdf_constant, exdf_constant_string)


class SpiHitfinder:
    """SPI lit-pixel hit hinder.

    The SPI hit finder split the images into two classes (hits and misses)
    splitting the number of lit-pixel in the region of interest.
    The threshold value can be fixed or determined by statistical analysis of
    the distribution of the number of lit-pixels in neighboring images.

    Features
    --------
    - makes the mask of hits and misses
    - selects the images for the future analysis, including all hits and
      random fraction of misses
    - draw hit-rate plot, hit-scores plot and hit-scores histogram
    """
    MODES = (
        "adaptive",
        "fixed",
    )
    FRACTION_BASE = ("hit", "miss")

    def __init__(self, modules, mode="adaptive", snr=4.0, min_scores=100,
                 fixed_threshold=0, hitrate_window_size=200, xgm_norm=True,
                 xgm_min=200, miss_fraction=1, miss_fraction_base="hit",
                 num_px_per_module=65536):
        """SPI hit finder constructor.

        Creates an instance of the `SpiHitfinder` class with a given
        parameters.

        Parameters
        ----------
        modules: sequence of int
            The list of modules to use in hit finding
        mode: str
            The method to define threshold value (fixed or adaptive),
            default: adaptive
        snr: float
            Coefficient of the standard deviation of the number of lit-pixels
            for calculation of the adaptive threshold.
        min_scores: int
            The minimum size of the sample to calculate adaptive threshold.
            If this is smaller then size of one train, entire train is used.
        fixed_threshold: float
            The fixed threshold value.
        hitrate_window_size: int
            The number of trains to compute running avarage of hit-rate.
        xgm_norm: bool
            Normalize scores with XGM pulse energy.
        xgm_min: float
            Minimum pulse energy used for normalization.
        miss_fraction: float
            The fraction of misses to select for future analyis.
        miss_fraction_base: str
            The base to compute the number of misses by the fraction.
        num_px_per_module: int
            The number of pixels per module. This is only used for
            normalization.
        """
        if mode not in self.MODES:
            raise ValueError(
                "Parameter 'mode' can take only values: "
                + ','.join(self.MODES))
        if miss_fraction_base not in self.FRACTION_BASE:
            raise ValueError(
                "Parameter 'miss_fraction_base' can take only values: "
                + ','.join(self.FRACTION_BASE)
            )

        self.modules = modules
        self.mode = mode
        self.fixed_threshold = fixed_threshold
        self.snr = snr
        self.min_scores = min_scores
        self.hitrate_window_size = hitrate_window_size
        self.xgm_norm = xgm_norm
        self.xgm_min = xgm_min
        self.miss_fraction = miss_fraction
        self.miss_fraction_base = miss_fraction_base
        self.num_px_per_module = num_px_per_module

        self._compute_threshold = getattr(self, "_compute_threshold_" + mode)
        self._read_threshold = getattr(self, "_read_threshold_" + mode)

        # exdf channels
        self._channels = {}
        self.data_keys = {}
        self.threshold_keys = {}

    @classmethod
    def from_datacollection(cls, run, source_name, force_recompute=False):
        control_source = run[source_name]
        run_values = control_source.run_values()

        num_modules = run_values["numModules.value"]
        hitfinder = cls(
            modules=run_values["modules.value"][:num_modules].tolist(),
            mode=run_values["mode.value"],
            snr=run_values["snr.value"],
            min_scores=run_values["minScores.value"],
            fixed_threshold=run_values["fixedThreshold.value"],
            hitrate_window_size=run_values["hitrateWindowSize.value"],
            xgm_norm=bool(run_values["xgmNormalization.value"]),
            xgm_min=run_values.get("xgmMinimalEnergy.value", 0),
            miss_fraction=run_values["missFraction.value"],
            miss_fraction_base=run_values["missFractionBase.value"],
        )
        hitfinder.max_modules = len(run_values["modules.value"])

        inst_source = run[f"{source_name}:output"]
        hitfinder._read_hitscore(inst_source)
        if force_recompute:
            hitfinder._compute()
        else:
            hitfinder._read_or_compute(inst_source)
        return hitfinder

    @exdf_constant
    def _modules(self):
        modules = np.zeros(self.max_modules, np.int8)
        modules[:len(self.modules)] = self.modules
        return modules

    @exdf_constant
    def _num_modules(self):
        return len(self.modules)

    @exdf_constant_string(max(map(len, MODES)))
    def _mode(self):
        return self.mode

    @exdf_constant
    def _snr(self):
        return self.snr

    @exdf_constant
    def _min_scores(self):
        return self.min_scores

    @exdf_constant
    def _fixed_threshold(self):
        return self.fixed_threshold

    @exdf_constant
    def _hitrate_window_size(self):
        return self.hitrate_window_size

    @exdf_constant
    def _xgm_normalization(self):
        return self.xgm_norm

    @exdf_constant
    def _xgm_minimal_energy(self):
        return self.xgm_min

    @exdf_constant
    def _miss_fraction(self):
        return self.miss_fraction

    @exdf_constant_string(max(map(len, FRACTION_BASE)))
    def _miss_fraction_base(self):
        return self.miss_fraction_base

    def _read_hitscore(self, src):
        """Reads hitscore from files."""
        self.train_ids = list(src.train_ids)
        self.count = src.data_counts("data")
        self.first = np.cumsum(self.count) - self.count

        self.trainId = src['data.trainId'].ndarray()
        self.pulseId = src['data.pulseId'].ndarray()
        self.hitscore = src['data.hitscore'].ndarray()

        self.num_events = np.sum(self.count)
        self.num_trains = len(self.train_ids)

    def _read_or_compute(self, src):
        """Reads or computes the hit-finding results."""
        try:
            self._read_threshold(src)
        except KeyError:
            self._compute_threshold()
        try:
            self.hit_mask = src['data.hitFlag'].ndarray().astype(bool)
            self.data_keys["hitFlag"] = self.hit_mask
        except KeyError:
            self._select_hits()
        try:
            self.miss_mask = src['data.missFlag'].ndarray().astype(bool)
            self.data_keys["missFlag"] = self.miss_mask
        except KeyError:
            self._select_hits()
        try:
            self.data_mask = src['data.dataFlag'].ndarray().astype(bool)
        except KeyError:
            self.data_mask = self.hit_mask | self.miss_mask
        # channel keys
        self.data_keys["dataFlag"] = self.data_mask

        self._compute_hitrate()
        self._make_channels()

    def _compute(self):
        """Computes the hit-finding results."""
        self._compute_threshold()
        self._select_hits()
        self._compute_hitrate()
        self._select_misses()

        self.data_mask = self.hit_mask | self.miss_mask
        # channel keys
        self.data_keys["dataFlag"] = self.data_mask

        self._make_channels()

    def _read_litpixels(self, src, litfrm_src=None):
        """Reads the number of lit-pixes computed per module."""
        lit_px_mod = src["litPixels"].ndarray(self.modules, fill_value=0)
        unmasked_px_mod = src["unmaskedPixels"].ndarray(
            self.modules, fill_value=0)

        lit_px = np.sum(lit_px_mod, axis=1)
        unmasked_px = np.sum(unmasked_px_mod, axis=1)
        total_px = len(self.modules) * self.num_px_per_module

        self.trainId = np.copy(src.trainId)
        self.pulseId = np.copy(src.pulseId)
        self.train_ids = list(src.train_ids)
        self.count = np.copy(src.count)
        self.first = np.copy(src.first)

        self.num_events = src.num_events
        self.num_trains = len(self.train_ids)
        self.max_modules = src.num_sources

        score = np.zeros(self.num_events, float)
        score = np.divide(lit_px, unmasked_px, where=unmasked_px > 0)

        hitscore = score * total_px

        if self.xgm_norm and litfrm_src is not None:
            en = litfrm_src.get_array(
                "energyPerFrame", self.trainId, self.pulseId)
            mu, _ = self._moving_stats(en, np.isfinite(en))
            mask = np.isnan(mu)
            mu[mask] = np.interp(
                np.flatnonzero(mask), np.flatnonzero(~mask), mu[~mask])
            mu = np.repeat(mu, self.count)
            self.good_mask = en > self.xgm_min
            np.multiply(
                hitscore,
                np.divide(mu, en, where=self.good_mask),
                where=self.good_mask, out=hitscore
            )
        else:
            self.good_mask = np.ones(len(hitscore), dtype=bool)

        self.hitscore = hitscore.astype(int)
        # channel keys
        self.data_keys.update({
            "pulseId": self.pulseId,
            "trainId": self.trainId,
            "hitscore": self.hitscore,
        })

    def _make_channels(self):
        self._channels = {
            "output.data": ChannelData(
                self.data_keys, self.train_ids, self.count, self.pulseId),
            "output.threshold": ChannelData(
                self.threshold_keys, self.train_ids),
        }

    def _read_threshold_adaptive(self, src):
        """Reads adaptive threshold from files."""
        self.threshold = src['threshold.value'].ndarray()
        self.mu = src['threshold.mu'].ndarray()
        self.sig = src['threshold.sig'].ndarray()

        # channel keys
        self.threshold_keys.update({
            "value": self.threshold,
            "mu": self.mu,
            "sig": self.sig,
        })

    def _moving_stats(self, scores, mask=None):
        """Computes adaptive threshold."""
        mu = np.zeros(self.num_trains, float)
        sig = np.zeros(self.num_trains, float)
        if mask is None:
            mask = np.ones_like(scores, dtype=bool)

        w0, wN = 0, 0
        dist = np.cumsum(mask)
        for trn_no, (evt0, nevt) in enumerate(zip(self.first, self.count)):
            evtN = evt0 + nevt
            d0, dN = dist[evt0], dist[evtN - 1]
            extent = max(0, (self.min_scores - (dN - d0 + 1)) // 2)

            if extent > 0:
                if d0 - dist[0] < extent:
                    w0 = 0
                else:
                    w0 += np.argmax((d0 - extent) < dist[w0:evt0])

                if (dist[-1] - dN) < extent:
                    wN = len(mask)
                else:
                    wN += np.argmax(dist[wN:] >= (extent + dN))
            else:
                w0, wN = evt0, evtN

            chunk = scores[w0:wN]
            chunk_mask = mask[w0:wN] & np.isfinite(chunk)
            q1, mu[trn_no], q3 = np.quantile(
                chunk[chunk_mask], [0.24, 0.5, 0.75])
            sig[trn_no] = (q3 - q1) / 1.34896

        return mu, sig

    def _compute_threshold_adaptive(self):
        """Computes adaptive threshold."""
        self.mu, self.sig = self._moving_stats(self.hitscore)
        self.threshold = self.mu + self.snr * self.sig

        # channel keys
        self.threshold_keys.update({
            "value": self.threshold,
            "mu": self.mu,
            "sig": self.sig,
        })

    def _read_threshold_fixed(self, src):
        """Reads fixed threshold from files."""
        self.threshold = src['threshold.value'].ndarray()

        # channel keys
        self.threshold_keys.update({
            "value": self.threshold,
        })

    def _compute_threshold_fixed(self):
        """Prepares hit-finder to use fixed threshold."""
        self.threshold = np.full(
            self.num_trains, self.fixed_threshold, float)

        # channel keys
        self.threshold_keys.update({
            "value": self.threshold,
        })

    def _compute_hitrate(self):
        """Computes hit-rate."""
        def running_mean(x, wnd):
            half = wnd // 2
            cumsum = np.cumsum(np.pad(x, (half, wnd - half)))
            return (cumsum[wnd:] - cumsum[:-wnd]) / wnd

        trn_id, trn_no, num_pulses = np.unique(
            self.trainId, return_inverse=True, return_counts=True)

        num_hits = np.bincount(trn_no, weights=self.hit_mask)
        num_hits_smooth = running_mean(
            num_hits, self.hitrate_window_size)
        num_pulses_smooth = running_mean(
            num_pulses, self.hitrate_window_size)

        self.hitrate_smooth = num_hits_smooth / num_pulses_smooth
        self.hitrate = num_hits / num_pulses

    def _select_hits(self):
        """Select hits."""
        threshold = np.repeat(self.threshold, self.count)
        self.hit_mask = self.good_mask & (self.hitscore > threshold)
        # channel keys
        self.data_keys["hitFlag"] = self.hit_mask

    def _select_misses(self):
        """Select misses."""
        rate = np.repeat(self.hitrate_smooth, self.count)
        mis_mask = self.good_mask & ~self.hit_mask
        if self.miss_fraction_base == "miss":
            num_misses = np.sum(mis_mask)
            rate = 1. - rate
        else:
            num_misses = np.sum(self.hit_mask)

        num_select = int(num_misses * self.miss_fraction + 0.5)
        rate = rate[mis_mask]
        if self.train_ids:
            np.random.seed(self.train_ids[0])
        ix = np.random.choice(
            np.flatnonzero(mis_mask),
            size=num_select,
            replace=False,
            p=rate / np.sum(rate)
        )
        self.miss_mask = np.zeros(self.num_events, bool)
        self.miss_mask[ix] = True

        # channel keys
        self.data_keys["missFlag"] = self.miss_mask

    def find_hits(self, src, litfrm_src=None):
        """Finds hits in a data source.

        Parameters
        ----------
        src: extra_redu.fileutils.StackedPulseSource
            The data source to read the nubmers of lit-pixels.
        """
        self._read_litpixels(src, litfrm_src)
        self._compute()

    @property
    def overall_hitrate(self):
        return np.sum(self.hit_mask) / np.size(self.hit_mask)

    def plot_hitscore_hist(self, num_bins=1000, ax=None, **kwargs):
        """Plots the hitscore histogram.

        Parameters
        ----------
        num_bins: int
            The number of intervals to bin hit-scores. The geometry space
            is used for binning.
        ax: matplotlib.axes.Axes
            The axes to draw the plot, default: None. If None, a new
            image is created.

        Returns
        -------
        ax: matplotlib.axes.Axes
            The axes
        """
        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=(16, 6), **kwargs)

        min_score = np.min(self.hitscore[self.hitscore > 0])
        max_score = np.max(self.hitscore)

        bins = np.geomspace(min_score, max_score, num_bins)

        drop_mask = ~(self.miss_mask | self.hit_mask)
        miss, _ = np.histogram(self.hitscore[self.miss_mask], bins)
        hit, _ = np.histogram(self.hitscore[self.hit_mask], bins)
        drop, _ = np.histogram(self.hitscore[drop_mask], bins)

        x = 0.5 * (bins[1:] + bins[:-1])
        ax.bar(x, drop, width=bins[1:]-bins[:-1], bottom=hit + miss,
               color="lightgrey")
        ax.bar(x, miss, width=bins[1:]-bins[:-1], bottom=hit)
        ax.bar(x, hit, width=bins[1:]-bins[:-1])

        ax.axvline(np.mean(self.mu), color="C1", ls="--", label="<mu>")
        q1, q3 = np.quantile(self.threshold, [0.25, 0.75])
        ax.axvline(q3, color="C2", ls="--", label="IQR(threshold)")
        ax.axvline(q1, color="C2", ls="--")
        ax.loglog()
        ax.legend(loc="upper right")
        ax.set_xlim(bins[0] * 0.9, bins[-1] * 1.2)
        ax.set_ylim(0.5, np.max(miss + hit + drop) * 1.5)

        ax.set_xlabel("Hit score")
        ax.set_ylabel("The number of frames")

        return ax

    def plot_hitrate(self, ax=None, **kwargs):
        """Plots the hitrate.

        Parameters
        ----------
        ax: matplotlib.axes.Axes
            The axes to draw the plot, default: None. If None, a new
            image is created.

        Returns
        -------
        ax: matplotlib.axes.Axes
            The axes
        """
        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=(16, 6), **kwargs)

        ax.plot(self.hitrate * 100, label="on average per 1 train")
        if self.hitrate_window_size > 1:
            ax.plot(self.hitrate_smooth * 100,
                    label=f"on average per {self.hitrate_window_size} trains")
        ax.set_xlim(0, self.num_trains)
        ax.legend(loc="upper right")
        ax.set_ylabel("Hit rate, %")
        ax.set_xlabel("Train no.")

        return ax

    def plot_hitscore(self, trains_per_plot=300, logy=True, **kwargs):
        """Plots the hitscores.

        Parameters
        ----------
        trains_per_plot: int
            The maximum number of trains to draw in one plot.
        """
        trn0 = 0
        evt0 = 0
        while trn0 < self.num_trains:
            trnN = min(trn0 + trains_per_plot, self.num_trains)
            trn_no = np.array(self.train_ids[trn0:trnN]) - self.train_ids[0]

            num_scores = np.sum(self.count[trn0:trnN])
            evtN = evt0 + num_scores

            evt_trn_no = self.trainId[evt0:evtN] - self.train_ids[0]
            hit = self.hit_mask[evt0:evtN]
            miss = self.miss_mask[evt0:evtN]
            drop = ~(hit | miss)
            score = self.hitscore[evt0:evtN]

            fig, ax = plt.subplots(1, 1, figsize=(16, 4), **kwargs)
            ax.scatter(evt_trn_no[drop], score[drop], s=1, c="lightgrey",
                       label="Not selected")

            # if self.mode == "adaptive":
            #    ax.plot(trn_no, self.mu[trn0:trnN], c="C3", lw=2)

            ax.plot(trn_no, self.threshold[trn0:trnN], c="C2", lw=2,
                    label="Threshold")

            ax.scatter(evt_trn_no[miss], score[miss], s=3, c="C0",
                       label="Miss")
            ax.scatter(evt_trn_no[hit], score[hit], s=3, c="C1",
                       label="Hit")

            ax.set_xlim(trn0, trn0 + trains_per_plot)
            if logy:
                ax.semilogy()
            ax.legend(loc="upper right")
            ax.set_ylabel("Hit score")
            ax.set_xlabel("Train no.")
            plt.show()

            trn0 = trnN
            evt0 = evtN
