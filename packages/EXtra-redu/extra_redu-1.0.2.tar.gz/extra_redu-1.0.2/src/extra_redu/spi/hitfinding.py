import multiprocessing as mp
import time
from argparse import ArgumentParser
import pathlib

import psutil
from extra_data import open_run, PropertyNameError
from extra_redu.fileutils import PulseSource, StackedPulseSource, exdf_save
from extra_redu.spi import LitPixelCounter, SpiHitfinder
from extra_redu.litfrm import make_litframe_finder, LitFrameFinderError


def make_report(notebook_filename, parameters, clean=True):
    import importlib_resources
    import nbformat
    import papermill as pm
    from nbconvert import PDFExporter
    from traitlets.config import Config

    report_ref = importlib_resources.files("extra_redu.spi") / "hitfinding_report.ipynb"
    with importlib_resources.as_file(report_ref) as report_path:
        pm.execute_notebook(
           report_path.absolute(),
           notebook_filename,
           parameters=parameters,
        )

    notebook = nbformat.reads(notebook_filename.read_text(), as_version=4)

    c = Config()
    c.TemplateExporter.exclude_input = True
    pdf_exporter = PDFExporter(config=c)

    (body, resources) = pdf_exporter.from_notebook_node(notebook)

    notebook_filename.with_suffix(".pdf").write_bytes(body)
    if clean:
        notebook_filename.unlink()


def hitfinding(proposal, run, detector_id, legacy, adu_threshold,
               num_proc=None, trains=slice(0, 100), output_dir='.',
               sequence_size=3500, litframe_finder_id=None,
               litframe_reprocess=False, **hitfinder_options):
    if num_proc is None:
        num_proc = min(psutil.cpu_count(logical=False), 32)

    # 1. read litframe finder data
    dc = open_run(proposal, run, data="raw")
    try:
        litfrm = make_litframe_finder(detector_id[:3], dc, litframe_finder_id)
        if litframe_reprocess:
            r = litfrm.process()
        else:
            r = litfrm.read_or_process()
        litfrm_src = PulseSource(
            r.meta.trainId, r.output.nFrame,
            r.output.detectorPulseId.ravel(),
            {
                "energyPerFrame": r.output.energyPerFrame.ravel(),
            }
        )
    except LitFrameFinderError:
        litfrm_src = None

    # 2.1 read lit-pixel counts
    dc = open_run(proposal, run, data="proc")
    dc = dc.select_trains(trains)
    try:
        litpx_counter = StackedPulseSource.from_datacollection(
            dc, f"{detector_id}/CORR/(?P<key>\\d+)CH0:output", "litpx")
    except (PropertyNameError, ValueError):
        litpx_counter = None

    sources = {}

    # 2.2 count lit-pixels
    if litpx_counter is None:
        source_pattern = detector_id + (r"/DET/(?P<key>\d+)CH0:xtdf" if legacy
                                        else r"/CORR/(?P<key>\d+)CH0:output")
        src = StackedPulseSource.from_datacollection(dc, source_pattern, "image")

        litpx_counter = LitPixelCounter(src, threshold=adu_threshold)
        with mp.Pool(num_proc) as pool:
            chunks = src.split_trains(trains_per_part=1)
            results = pool.imap_unordered(litpx_counter, chunks)
            for _ in results:
                pass

        sources[f"{detector_id}/REDU/LITPX_COUNTER"] = litpx_counter

    # 3. hit finding
    hitfinder = SpiHitfinder(**hitfinder_options)
    hitfinder.find_hits(litpx_counter, litfrm_src)
    sources[f"{detector_id}/REDU/SPI_HITFINDER"] = hitfinder

    # 4. write results in file
    exdf_save(str(output_dir), "REDU00", run, sources, sequence_size=sequence_size)

    return num_proc, hitfinder.overall_hitrate


def parse_slice(s):
    return slice(*[int(a) if a else None for a in s.split(':')])


def main(argv=None):
    parser = ArgumentParser(
        description="The program find hits on "
                    "single particle diffraction images"
    )
    parser.add_argument("-p", "--proposal", type=int, required=True,
                        help="proposal no.")
    parser.add_argument("-r", "--run", type=int, required=True,
                        help="run no.")
    parser.add_argument("-d", "--detector-id", required=True,
                        help="Detector Id")
    parser.add_argument("--litframe-finder-id",
                        help="Litframe finder Id")
    parser.add_argument("--litframe-reprocess", action="store_true",
                        help="Redo lit-frame finding offline")
    parser.add_argument("-l", "--legacy", action="store_true",
                        help="Use legacy naming for corrected detector "
                             "sources")
    parser.add_argument("-t", "--adu-threshold", type=float, default=0.7,
                        help="Pixel intensity threshold, indicates "
                             "that pixel is illuminated")
    parser.add_argument("-m", "--modules", nargs='*', type=int,
                        default=[3, 4, 8, 15],
                        help="List of modules")
    parser.add_argument("-M", "--mode", choices=SpiHitfinder.MODES,
                        default="adaptive",
                        help="The method to estimate threshold of "
                             "the lit-pixel number")
    parser.add_argument("--snr", type=float, default=4.0,
                        help="Sigma factor to estimate adaptive threshold")
    parser.add_argument("--min-scores", type=int, default=100,
                        help="The minimum number of scores to "
                        "estimate the adaptive threshold")
    parser.add_argument("-T", "--fixed-threshold", type=int, default=0,
                        help="The value of the fixed threshold of "
                             "the lit-pixel number")
    parser.add_argument("--hitrate-window-size", type=int, default=200,
                        help="The window size in trains of "
                             "hitrate running average")
    parser.add_argument("--xgm-norm", action="store_true",
                        help="Normalize scores with XGM pulse energy")
    parser.add_argument("--xgm-min", type=float, default=200,
                        help="Minimum pulse energy valid for normalization")
    parser.add_argument("-f", "--miss-fraction", type=float, default=1,
                        help="The fraction of misses to select")
    parser.add_argument("-b", "--miss-fraction-base",
                        choices=SpiHitfinder.FRACTION_BASE, default="hit",
                        help="The base to caclulate the fraction of misses")
    parser.add_argument("-n", "--num_proc", type=int,
                        help="The number of processes")
    parser.add_argument("-o", "--output-dir", type=str, default=pathlib.Path(),
                        help="Output directory, default is current")
    parser.add_argument("-s", "--trains", type=parse_slice,
                        default=slice(None), help="Trains slice")
    parser.add_argument("--report-dir", type=pathlib.Path,
                        help="Report directory, no report if not given")
    parser.add_argument("-c", "--sequence-size", type=int, default=3500,
                        help="Number of trains in sequence file")

    args = parser.parse_args(argv)

    if args.num_proc is None:
        print("cpu req:   auto")
    else:
        print(f"cpu req:   {args.num_proc}")

    kwargs = dict(args._get_kwargs())
    report_dir = kwargs.pop("report_dir", None)

    tm0 = time.perf_counter()
    num_proc, hitrate = hitfinding(**kwargs)
    tm1 = time.perf_counter()
    print(f"cpu used:  {num_proc}")
    print(f"comp time: {tm1 - tm0:.1f}s")
    print(f"hitrate:   {100 * hitrate:.2g}%")

    if report_dir is not None:
        notebook_filename = report_dir / f"hitfinding-p{args.proposal:06d}-r{args.run:04d}.ipynb"
        make_report(notebook_filename, dict(
            detector_id=args.detector_id,
            result_dir=str(args.output_dir),
        ))


if __name__ == "__main__":
    main()
