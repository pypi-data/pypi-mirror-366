import os
import sys
import csv
import argparse
import numpy as np

from extra_data import RunDirectory
from extra_data.exceptions import SourceNameError
from extra_data.read_machinery import find_proposal
from extra_redu import (
    make_litframe_finder, BunchPatternNotFound, DetectorNotFound,
    ReferenceDelay, FrameSelection,
)
from extra_redu.base import DESTINATION


def get_npulse_xgm(dc, xgm_id, dst):
    dev_id = xgm_id.partition(':')[0]
    if dev_id not in dc.control_sources:
        raise SourceNameError(dev_id)
    keydata = dc[dev_id, f"pulseEnergy.numberOf{dst}BunchesActual"]
    location = dc.get_run_value(dev_id, 'location')
    return keydata.train_id_coordinates(), keydata.ndarray(), location


def get_npulse_pp(dc, pp_id, dst):
    if pp_id not in dc.control_sources:
        raise SourceNameError(pp_id)
    keydata = dc[pp_id, f"{dst}.nPulses"]
    return keydata.train_id_coordinates(), keydata.ndarray()


def get_npulse_bp(dc, ts_id, dst):
    dev_id, _, channel = ts_id.partition(':')
    if not channel:
        channel = "outputBunchPattern"
    src = dev_id + ':' + channel
    if src not in dc.instrument_sources:
        raise SourceNameError(dev_id)
    bp = dc[src, 'data.bunchPatternTable'].ndarray()
    tid = dc[src, 'data.trainId'].ndarray()
    return tid, np.sum(dst.get_instrument_pulse_mask(bp), 1)


def get_most_frequently(trains, tid, npulse):
    ix = np.flatnonzero(np.in1d(tid, trains))
    npulse_uniq, count = np.unique(npulse[ix], return_counts=True)
    return npulse_uniq[np.argmax(count)]


def parse_slice(optval):
    """Parses modules cmdline option"""
    rng = set()
    for t in optval.split(','):
        a, _, b = t.partition('-')
        if b == '':
            rng.add(int(a))
        else:
            rng.update(range(int(a), int(b) + 1))

    return sorted(rng)


def parse_delay(optstr):
    event_name, _, params = optstr.partition(',')
    types = [int, int, int, float, float]
    args = [type_cast(tk) for tk, type_cast in zip(params.split(','), types)]
    return (event_name, ReferenceDelay(*args))


def main():
    parser = argparse.ArgumentParser(
        description='Generate litframe report for a proposal.')
    parser.add_argument('proposal', type=int, help='proposal Id')
    parser.add_argument('-o', '--csv', type=str,
                        help='the name of output CSV-file')
    parser.add_argument('-r', '--runs', type=parse_slice,
                        help='the slice of runs, e.g. 1-3,5,7-10')
    parser.add_argument('-d', '--delay', type=parse_delay, action='append',
                        help="the reference delay as: static|dynamic,<delay>,"
                        "<pulse>,<cell>,<rep.rate>,<distance>")
    parser.add_argument('-a', '--align-method', type=str,
                        choices=['by reference delay', 'by first pulse'],
                        help="force alignment method")
    parser.add_argument('-p', '--process', action='store_true',
                        default=False, help="force reprocessing")

    args = parser.parse_args()

    propno = args.proposal
    csvname = f"litfrm_p{propno:06}.csv" if args.csv is None else args.csv
    align_method = args.align_method
    reprocess = args.process or (align_method is not None)

    propdir = find_proposal(f"p{propno:06d}")
    inst = propdir.split('/')[4]
    dst = DESTINATION[inst]
    
    ref_delays = dict(
        (dst.event_code[evname], d) for evname, d in args.delay
    ) if args.delay else {}
    
    print(f"Proposal No: {propno}")
    print(f"Proposal directory: {propdir}")
    print(f"Instrument: {inst}")
    print(f"Align method: {align_method}")
    if args.delay:
        print("Default reference delays:")
        for event, ref in ref_delays.items():
            print(f"  {event:3d}:{ref}")
    print()

    runs = sorted([
        int(fn[1:]) for fn in os.listdir(os.path.join(propdir, "raw"))
        if fn[0] == 'r' and fn[1:].isdigit()
    ])
    if args.runs is not None:
        runs = [runno for runno in runs if runno in args.runs]

    f = open(csvname, 'w', newline='')
    fieldnames = ['runno', 'source', 'runtype', 'pattern_no', 'range_serial',
                  'train_range', 'nmissed_trains', 'npulse_bp', 'npulse_pp',
                  'npulse_xgm', 'npulse_exposed', 'ndataframe', 'nframe_total',
                  'litframe_slice', 'super_pattern_slice', 'xgm_location',
                  'exception']
    fieldlabels = ['Run No', 'Source', 'AGIPD Run Type', 'Pattern No',
                   'Train Range Serial', 'Train Range',
                   'Number of missed trains', 'Number of pulses at Timeserver',
                   'Number of pulses at PPD', 'Number of pulses at XGM',
                   'Number of Exposed Pulses', 'Number of Frames with Data',
                   'Total Number of Frames', 'Frame Slice',
                   'Common Frame Slice', 'XGM Location', 'Exception']
    writer = csv.DictWriter(
        f, fieldnames=fieldnames, delimiter=';', quotechar='"',
        quoting=csv.QUOTE_NONNUMERIC
    )
    writer.writerow(dict(zip(fieldnames, fieldlabels)))

    for runno in runs:
        rundir = os.path.join(propdir, "raw", f"r{runno:04}")
        dc = RunDirectory(rundir)

        try:
            litfrm = make_litframe_finder(inst, dc, ref_delays=ref_delays,
                                          align_method=align_method)
            if reprocess:
                r = litfrm.process()
            else:
                r = litfrm.read_or_process()

            runtype = litfrm._detector.patternType.value

            try:
                tid_xgm, npulse_xgm, xgm_loc = get_npulse_xgm(
                    dc, litfrm.xgm_id, dst.xgm_key)
            except SourceNameError:
                tid_xgm, npulse_xgm = None, None
            try:
                tid_pp, npulse_pp = get_npulse_pp(
                    dc, litfrm.pp_decoder_id, dst.pp_key)
            except SourceNameError:
                tid_pp, npulse_pp = None, None
            try:
                tid_bp, npulse_bp = get_npulse_bp(
                    dc, litfrm.bunch_pattern_id, dst)
            except SourceNameError:
                tid_bp, npulse_bp = None, None

            sel = FrameSelection(r)
            for r in sel.report():
                frmintf = ', '.join([
                    ':'.join([str(n) for n in slc])
                    for slc in r['litframe_slice']
                ])
                supperptrn_intf = ', '.join([
                    ':'.join([str(n) for n in slc])
                    for slc in r['super_pattern_slice']
                ])
                trsintf = ':'.join([str(n) for n in r['train_range']])
                recfrm = r.copy()
                tid = range(*r['train_range'])
                if tid_xgm is not None:
                    recfrm['npulse_xgm'] = get_most_frequently(
                        tid, tid_xgm, npulse_xgm)
                    recfrm['xgm_location'] = xgm_loc
                if tid_pp is not None:
                    recfrm['npulse_pp'] = get_most_frequently(
                        tid, tid_pp, npulse_pp)
                if tid_bp is not None:
                    recfrm['npulse_bp'] = get_most_frequently(
                        tid, tid_bp, npulse_bp)
                recfrm['litframe_slice'] = frmintf
                recfrm['super_pattern_slice'] = supperptrn_intf
                recfrm['runno'] = runno
                recfrm['runtype'] = runtype
                writer.writerow(recfrm)
                if r['range_serial'] == 0:
                    print("{runno:4d} {source:30s} {runtype:6s}".format(
                        **recfrm), end='')
                else:
                    print(" "*42, end='')
                print(
                    ("{pattern_no:2d} {trsintf:25s} {npulse_exposed:4d} "
                     "{ndataframe:3d} {nframe_total:3d} [{litframe_slice}]"
                     ).format(trsintf=trsintf, **recfrm))
        except BunchPatternNotFound:
            runtype = litfrm._detector.patternType.value
            errmsg = f"BunchPattern not found ({runtype})"
            writer.writerow(dict(runno=runno, exception=errmsg))
            print(f"{runno:4d} - skip: {errmsg}")
        except DetectorNotFound:
            errmsg = "Detector not found"
            writer.writerow(dict(runno=runno, exception=errmsg))
            print(f"{runno:4d} - skip: {errmsg}")

    f.close()


if __name__ == "__main__":
    sys.exit(main())
