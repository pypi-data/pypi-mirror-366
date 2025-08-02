"""Command‑line interface for the TD‑MION Orbitrap data‑analysis toolkit.

This CLI wraps the pure‑Python pipeline and utility functions, exposing them
through the `td‑mion` console script (defined in ``pyproject.toml``).

Run `td‑mion --help` for an overview.
"""
from __future__ import annotations

import logging
from pathlib import Path

import click
import yaml
import numpy as np
import pandas as pd

from td_mion_orbitrap.pipeline import run_pipeline
from td_mion_orbitrap.kmd import compute_kmd, plot_kmd
from td_mion_orbitrap.spectrum import (
    extract_raw_spectrum,
    extract_combined_spectrum,
    extract_peaks,
)

################################################################################
# Root command group
################################################################################


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase output verbosity (-v INFO, -vv DEBUG, -vvv TRACE).",
)
def cli(verbose: int) -> None:
    """TD‑MION-Orbitrap data‑analysis command suite."""

    level = logging.WARNING - 10 * verbose  # each -v steps one level down
    level = max(level, logging.DEBUG)
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")

################################################################################
# Sub‑commands
################################################################################


@cli.command()
@click.argument(
    "config",
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=Path),
)
@click.option(
    "-j",
    "--workers",
    type=int,
    default=None,
    show_default=True,
    help="Parallel workers (default: logical cores).",
)
def process(config: Path, workers: int | None) -> None:
    """Run the full thermogram → spectra → KMD pipeline described in CONFIG (YAML)."""

    with config.open("r", encoding="utf-8-sig") as fh:
        cfg = yaml.safe_load(fh)

    run_pipeline(cfg, max_workers=workers)


@cli.command()
@click.argument(
    "mzml",
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=Path),
)
@click.option("-s", "--scan", "scan_index", type=int, default=0, show_default=True,
              help="Single scan index (ignored when --start/--end used)")
@click.option("--start", "start_index", type=int, help="Start scan for averaging (inclusive)")
@click.option("--end", "end_index", type=int, help="End scan for averaging (inclusive)")
@click.option("--nominal", "nominal_base", type=float, default=14.000, show_default=True)
@click.option("--exact", "exact_base", type=float, default=14.01565, show_default=True)
@click.option("--bin", "bin_width", type=float, default=0.0005, show_default=True, help="m/z bin width for KMD plot")
@click.option(
    "--peaks/--profile",
    default=False,
    show_default=True,
    help="Use pre‑picked peaks instead of full profile spectrum.",
)
@click.option(
    "-o",
    "--output",
    "output_file",
    type=click.Path(dir_okay=False, writable=True, path_type=Path),
    help="Write PNG to OUTPUT instead of displaying.",
)
@click.option("-v", "--verbose", count=True)
def kmd(
    mzml: Path,
    scan_index: int,
    start_index: int | None,
    end_index: int | None,
    nominal_base: float,
    exact_base: float,
    bin_width: float,
    peaks: bool,
    output_file: Path | None,
    verbose: int,
) -> None:
    """Generate a Kendrick‑Mass‑Defect plot from one scan of an mzML file."""

    import pymzml  # local import keeps CLI startup fast
    
    lvl = logging.WARNING - 10 * verbose
    logging.getLogger().setLevel(max(lvl, logging.DEBUG))

    run = pymzml.run.Reader(str(mzml))
    specs = list(run)

    if start_index is not None or end_index is not None:
        n_scans = len(specs)
        s = start_index or 0
        e = end_index if end_index is not None else n_scans - 1
        scan_indices = list(range(s, e + 1))
        tuples = [(s.scan_time_in_minutes(), s.mz, s.i) for s in specs]
        raw_df = extract_combined_spectrum(tuples, scan_indices)
    else:
        tuples = [(s.scan_time_in_minutes(), s.mz, s.i) for s in specs]
        raw_df = extract_raw_spectrum(tuples, scan_index=scan_index)
    
    df = extract_peaks(raw_df) if peaks else raw_df
    df["mz_bin"] = (df["mz"] / bin_width).round().astype(int)
    df = df.groupby("mz_bin", as_index=False)[["mz", "intensity"]].max()
    #intensity_col = "int_blank_removed" if "int_blank_removed" in df.columns else "intensity"

    kmd_df = compute_kmd(df, intensity_col="intensity", nominal_base=nominal_base, exact_base=exact_base)
    plot_kmd(kmd_df, output_file=str(output_file) if output_file else None)

    if output_file is None:
        # Display interactively only when no file path is supplied
        import matplotlib.pyplot as plt

        plt.show()

################################################################################
# Module entry‑point
################################################################################


def main() -> None:  # pragma: no cover
    """Entry‑point for ``python -m td_mion_orbitrap.cli``."""

    cli()


if __name__ == "__main__":
    main()