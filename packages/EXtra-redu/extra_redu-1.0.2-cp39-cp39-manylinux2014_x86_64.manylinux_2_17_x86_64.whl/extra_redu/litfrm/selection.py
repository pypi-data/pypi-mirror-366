import numpy as np
from enum import IntEnum
from .utils import (
    find_runs, find_ranges_of_patterns, compress_ranges_of_patterns,
    expand_ranges_of_cells, find_ranges,
)


def row_selection(ptrn, rowsize=32):
    """Expand cell selection to row selection"""
    single = ptrn.ndim == 1
    nfrm = ptrn.size if single else ptrn.shape[1]
    nrow = nfrm // rowsize + bool(nfrm % rowsize)
    padded_size = nrow * rowsize
    npad = padded_size - nfrm
    ptrn_cm = np.pad(ptrn, (0, npad)).reshape(-1, nrow, rowsize)
    ptrn_cm[:, :] = np.any(ptrn_cm, axis=2, keepdims=True)
    ptrn_cm = ptrn_cm.reshape(-1, padded_size)[:, :nfrm]
    return ptrn_cm.ravel() if single else ptrn_cm


class SelType(IntEnum):
    CELL = 0
    ROW = 1
    SUPER_CELL = 2
    SUPER_ROW = 3


class FrameSelection:

    def __init__(self, r, guess_missed=True, crange=None,
                 energy_threshold=-1000, select_litframes=False):
        self.tid = r.meta.trainId
        if energy_threshold != -1000:
            self.energy = r.output.energyPerFrame
            self.missed_xgm_intensity = 10000

        self.dev = r.meta.litFrmDev
        self._find_pattern_ranges(r, guess_missed, select_litframes)
        self._make_selection(guess_missed, crange, energy_threshold)

    def _find_pattern_ranges(self, r, guess_missed=True,
                             select_litframes=False):
        """Find unique patterns and their train ranges"""
        self.ranges = []
        self.datafrm = []
        self.npls = []
        self.npls_ix = []
        self.run_slice = []

        # find run of trains with fixed number of frames
        nfrm_uniq, run_starts, ntrn_in_run = find_runs(r.output.nFrame)

        self.nfrmrun = len(nfrm_uniq)
        self.nfrm_uniq = nfrm_uniq
        self.tid_type = r.meta.trainId.dtype

        self.ntrain = np.zeros(self.nfrmrun, dtype=int)
        for i in range(self.nfrmrun):
            nfrm = nfrm_uniq[i]
            i0 = run_starts[i]
            iN = i0 + ntrn_in_run[i]

            if select_litframes:
                datafrm = r.output.nPulsePerFrame[i0:iN, :nfrm] > 0
            else:
                datafrm = r.output.dataFramePattern[i0:iN, :nfrm]
            tid = r.meta.trainId[i0:iN]

            # find unique patterns
            npls_uniq, npls_first, npls_ix = np.unique(
                r.output.nPulsePerFrame[i0:iN, :nfrm],
                return_index=True, return_inverse=True, axis=0
            )
            # make ranges of the same patterns
            ranges = find_ranges_of_patterns(npls_uniq.shape[0], npls_ix, tid)
            ranges = compress_ranges_of_patterns(ranges, tid)

            # compress data frame patterns
            ptrn = datafrm[npls_first, :]

            # accumulate normalised number of trains in the frame run
            if guess_missed:
                ntrn_nrm = 0
                for _, range_list in ranges:
                    ntrn_nrm += sum(ntrn + missed
                                    for _, _, _, ntrn, missed in range_list)
                self.ntrain[i] = ntrn_nrm
            else:
                self.ntrain[i] = ntrn_in_run

            self.ranges.append(ranges)
            self.datafrm.append(ptrn)
            self.npls.append(npls_uniq)
            self.npls_ix.append(npls_ix)
            self.run_slice.append(slice(i0, iN))

    def _make_selection(self, guess_missed=True,
                        crange=None, energy_threshold=-1000):
        """Make frame selection from lit frame patterns"""
        ntrain = np.sum(self.ntrain)
        nframe = np.sum(self.ntrain * self.nfrm_uniq)
        self.trains = np.zeros(ntrain, dtype=self.tid_type)
        self.cell_flags = np.zeros(nframe, dtype=bool)
        self.row_flags = np.zeros(nframe, dtype=bool)
        self.cell_super = np.zeros(nframe, dtype=bool)
        self.row_super = np.zeros(nframe, dtype=bool)
        self.empty_trains = np.zeros(ntrain, dtype=bool)
        self.first = np.zeros(ntrain, dtype=int)
        self.count = np.zeros(ntrain, dtype=int)
        self.flags = [self.cell_flags, self.row_flags,
                      self.cell_super, self.row_super]
        one = self.tid_type.type(1)

        i0 = 0
        k0 = 0
        for i in range(self.nfrmrun):
            ntrn_in_run = self.ntrain[i]
            nfrm = self.nfrm_uniq[i]
            s = self.run_slice[i]

            if crange is None:
                cell_mask = np.ones(nfrm, bool)
            else:
                cell_mask = np.zeros(nfrm, bool)
                cell_mask[crange] = True

            ptrn = self.datafrm[i] & cell_mask[None, :]

            # make row selection for common mode correction
            ptrn_cm = row_selection(ptrn)

            # find empty pattern
            ptrn_empty = np.sum(ptrn, axis=1) == 0

            # find the super pattern
            superptrn = np.any(ptrn, axis=0)
            superptrn_cm = row_selection(superptrn)

            iN = i0 + ntrn_in_run * nfrm
            kN = k0 + ntrn_in_run
            if guess_missed:
                # make normalised trains
                ranges = self.ranges[i]

                tid_nrm = np.zeros(ntrn_in_run, dtype=self.tid_type)
                ptrn_ix = np.zeros(ntrn_in_run, dtype=int)
                j0 = 0
                for ptrn_id, range_list in ranges:
                    for t0, tN, step, ntrn, missed in range_list:
                        # make train list
                        jN = j0 + ntrn + missed
                        tid_nrm[j0:jN] = np.arange(
                            t0, tN + one, step, dtype=self.tid_type)
                        ptrn_ix[j0:jN] = ptrn_id
                        j0 = jN

                sorted_ix = np.argsort(tid_nrm)
                self.trains[k0:kN] = tid_nrm[sorted_ix]

                ix = ptrn_ix[sorted_ix]
            else:
                # use original trains
                self.trains[k0:kN] = self.tid[s]
                ix = self.npls_ix[i]

            # expand and stack patterns in pulse resolved format
            self.cell_flags[i0:iN] = ptrn[ix, :].ravel()
            self.row_flags[i0:iN] = ptrn_cm[ix, :].ravel()
            self.empty_trains[k0:kN] = ptrn_empty[ix]

            # apply energy threshold
            if energy_threshold != -1000:
                tid = self.tid[s]
                en = self.energy[s, :nfrm]
                xgm_flag = np.ones([ntrn_in_run, nfrm], bool)
                xgm_ix = np.flatnonzero(np.in1d(tid, self.trains[k0:kN]))
                xgm_flag[xgm_ix, :] = ((en > energy_threshold) |
                                       (en == self.missed_xgm_intensity))

                self.cell_flags[i0:iN] = (
                    self.cell_flags[i0:iN] & xgm_flag.ravel())

            self.cell_super[i0:iN] = np.tile(superptrn, ntrn_in_run)
            self.row_super[i0:iN] = np.tile(superptrn_cm, ntrn_in_run)

            self.first[k0:kN] = np.arange(i0, iN, nfrm, dtype=int)
            self.count[k0:kN] = np.full(ntrn_in_run, nfrm, dtype=int)

            i0 = iN
            k0 = kN

    def litframes_on_trains(self, train_sel, nfrm, frame_idx, selection_types):
        """Return lit-frame selection for requested trains"""
        ntrain = len(train_sel)
        _, ix_avl, ix_sel = np.intersect1d(
            self.trains, train_sel, assume_unique=True, return_indices=True)

        train_idx = np.full(ntrain, -1, dtype=int)
        train_idx[ix_sel] = ix_avl

        nsel = len(selection_types)
        nfrm_total = np.sum(nfrm)
        flags = [np.zeros(nfrm_total, dtype=bool) for _ in range(nsel)]
        count = [np.zeros(ntrain, dtype=int) for _ in range(nsel)]

        j0 = 0
        for trn_no, trn_ix in enumerate(train_idx):
            jN = j0 + nfrm[trn_no]
            if trn_ix == -1 or self.empty_trains[trn_ix]:
                for i in range(nsel):
                    count[i][trn_no] = 0
            else:
                fix = frame_idx[j0:jN]
                # what to do if frame index is out of range?
                # clean or raise exception
                i0 = self.first[trn_ix]
                iN = i0 + self.count[trn_ix]
                for i, sel_type in enumerate(selection_types):
                    flags_trn = self.flags[sel_type][i0:iN][fix]
                    flags[i][j0:jN] = flags_trn
                    count[i][trn_no] = np.sum(flags_trn)
            j0 = jN

        return zip(flags, count)

    def filter_trains(self, train_sel, drop_empty=True):
        """Filters out trains that will not be processed"""
        good_trains = (self.trains[~self.empty_trains]
                       if drop_empty else self.trains)
        return train_sel[np.in1d(train_sel, good_trains)]

    def report(self):
        """Generate litframe report"""
        one = self.tid_type.type(1)

        rep = []
        ptrn_no = 0
        serial = 0
        for i in range(self.nfrmrun):
            nfrm = self.nfrm_uniq[i]
            ranges = self.ranges[i]
            datafrm = self.datafrm[i]
            npls_uniq = self.npls[i]

            # find the super pattern
            superptrn = np.any(datafrm, axis=0)
            superptrn_int = expand_ranges_of_cells(
                find_ranges(np.flatnonzero(superptrn)))

            for ptrn_id, range_list in ranges:
                for t0, tN, step, count, missed in range_list:
                    trains = ((t0, tN + one, step) if step > 1
                              else (t0, tN + one))

                    ptrn = datafrm[ptrn_id, :]
                    ndata = ptrn.sum()
                    npls = npls_uniq[ptrn_id, :].sum()

                    frmint = expand_ranges_of_cells(
                        find_ranges(np.flatnonzero(ptrn)))
                    rep.append(dict(
                        source=self.dev, pattern_no=ptrn_no,
                        range_serial=serial, train_range=trains,
                        nmissed_trains=missed, npulse_exposed=npls,
                        ndataframe=ndata, nframe_total=nfrm,
                        litframe_slice=frmint,
                        super_pattern_slice=superptrn_int,
                    ))
                    serial += 1

                ptrn_no += 1

        return rep
