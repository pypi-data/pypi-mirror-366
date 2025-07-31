from logging import getLogger

import numpy as np
from exdf.data_reduction import ReductionMethod
from extra_data import by_id

from . import FrameSelection, SelType, make_litframe_finder


class LitFrames(ReductionMethod):
    log = getLogger('exdf.data_reduction.builtins.LitFrames')

    @staticmethod
    def arguments(ap):
        group = ap.add_argument_group(
            'LFF lit-frame selection',
            'Allows to remove dark frames')

        group.add_argument(
            '--lff-source',
            action='store', type=str,
            help='LitFrameFinder source to use',
        )
        group.add_argument(
            '--lff-det-sources',
            action='store', type=str,
            help='Detector sources to filter',
        )
        group.add_argument(
            '--lff-super-selection',
            action='store_true',
            help='save a cell for all trains '
            'if it illuminated in any train',
        )
        group.add_argument(
            '--lff-row-selection',
            action='store_true',
            help='save a whole row of cells for AGIPD '
            'if it has at least one lit frame',
        )
        group.add_argument(
            '--lff-report-max-lines',
            action='store', type=int, default=20,
            help='Maximum number of lines in report',
        )

    def __init__(self, data, args):
        if not args.lff_source:
            return

        if not args.lff_det_sources:
            raise ValueError(
                "With the LFF enabled you must pass --lff-det-sources, "
                "e.g. like --lff-det-sources 'MID_DET_AGIPD1M-1/DET/*'"
            )

        inst = args.lff_source.partition('_')[0].upper()
        dev = make_litframe_finder(inst, data, args.lff_source)

        r = dev.read_or_process()
        sel = FrameSelection(r, guess_missed=True)

        self.log.info('For lit-frame selection use source ' + r.meta.litFrmDev)
        self.print_report(sel, max_lines=args.lff_report_max_lines)

        sel_type = SelType(
            (args.lff_super_selection << 1) | args.lff_row_selection)

        # loop over sources
        det = data.select(args.lff_det_sources, "image.cellId")
        for src in det.instrument_sources:
            self.log.info("select frames in " + src)

            # read frame ids
            cid_key = det[src]["image.cellId"].drop_empty_trains()
            train_sel = sel.filter_trains(
                np.asarray(cid_key.train_ids), drop_empty=True)
            cid_key = cid_key.select_trains(by_id[train_sel])

            nfrm = cid_key.data_counts(labelled=False).astype(int)
            cell_id = np.squeeze(cid_key.ndarray())

            # get lit-frame selection
            (frame_sel, counts), = sel.litframes_on_trains(
                 train_sel, nfrm, cell_id, [sel_type])

            # select frames for every train
            train_masks = np.split(frame_sel, np.cumsum(nfrm))
            for train_id, mask in zip(train_sel, train_masks):
                if (len(mask) > 0) and not np.all(mask):
                    self.select_xtdf(src, by_id[[train_id]], mask)

    def print_report(self, sel, max_lines=20):
        report = sel.report()
        nrec = len(report)
        s = slice(max_lines - 1) if nrec > max_lines else slice(None)
        self.log.info(
            " # trains                     Ntrn Nmis   Np  Nd  Nf lit frames")
        for rec in report[s]:
            frmintf = ', '.join([
                ':'.join([str(n) for n in slc])
                for slc in rec['litframe_slice']
            ])
            t0, tN, st = (rec['train_range'] + (1,))[:3]
            ntrain = max((int(tN) - int(t0)) // int(st), 1)
            trsintf = ':'.join([str(n) for n in rec['train_range']])
            self.log.info((
                "{pattern_no:2d} {trsintf:25s} {ntrain:5d} "
                "{nmissed_trains:4d} {npulse_exposed:4d} "
                "{ndataframe:3d} {nframe_total:3d} [{frmintf}]").format(
                frmintf=frmintf, ntrain=ntrain, trsintf=trsintf, **rec)
            )
        if nrec > max_lines:
            self.log.info(f"... {nrec - max_lines + 1} more lines skipped")
