"""Core orchestration logic for the TD‑MION Orbitrap workflow.

Expose a single public function::

    run_pipeline(cfg: dict, *, max_workers: int | None = None) -> None

which executes the full thermogram → spectrum → KMD processing described in the
YAML configuration already loaded by the caller.

Version 0.2.1 adds a per‑sample CSV summary of integrated areas so CLI users
no longer have to scrape log files for numeric results.
"""
from __future__ import annotations

###############################################################################
# Standard library
###############################################################################

import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Tuple

###############################################################################
# Third‑party
###############################################################################

import pandas as pd

###############################################################################
# Local imports – kept late to reduce CLI start‑up overhead
###############################################################################

from td_mion_orbitrap.thermo import load_and_index, extract_thermogram
from td_mion_orbitrap.blank import (
    extract_combined_thermogram,
    subtract_blank,
    normalize_thermogram,
)
from td_mion_orbitrap.spectrum import (
    extract_raw_spectrum,
    extract_combined_spectrum,
    remove_blank_spectrum,
    extract_peaks,
)
from td_mion_orbitrap.integration import integrate_thermogram
from td_mion_orbitrap.kmd import compute_kmd, plot_kmd

###############################################################################
# Logging helpers
###############################################################################

logger = logging.getLogger(__name__)

###############################################################################
# Internal utility functions (picklable → usable with ProcessPoolExecutor)
###############################################################################

def _build_scan_range(n_scans: int, start: int | None, end: int | None) -> list[int] | None:
    """Return a list of scan indices or *None* if no averaging requested."""
    if start is None and end is None:
        return None  # no averaging – use default behaviour elsewhere
    s = start or 0
    e = end if end is not None else n_scans - 1
    e = min(e, n_scans - 1)
    if s > e:
        raise ValueError(f"start_index {s} > end_index {e}")
    return list(range(s, e + 1))

"""
def _find_full_ms1_scan(specs: List[Tuple[float, Any, Any]], min_span: float = 200.0) -> int:
    Return index of the first scan whose m/z range spans ≥ *min_span* Da.

    for i, (_rt, mzs, _vals) in enumerate(specs):
        if mzs.max() - mzs.min() >= min_span:
            return i
    raise RuntimeError("No full‑range scan found in the file.")
"""

def _bin_spectrum(df: pd.DataFrame, bin_width: float) -> pd.DataFrame:
    """
    Compress a (possibly blank-corrected) spectrum by binning m/z.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain at least columns ``'mz'`` and either
        ``'intensity'`` or ``'int_blank_removed'``.
    bin_width : float
        Bin size in Daltons (e.g. 0.0005). All peaks whose m/z fall into the
        same bin are merged; the **maximum** intensity in the bin is kept
        (this preserves peak tops for KMD plots).

    Returns
    -------
    pd.DataFrame
        Two-column frame ``['mz', 'intensity']`` suitable for `compute_kmd`.
    """
    # Determine which intensity column is present
    int_col = (
        "int_blank_removed" if "int_blank_removed" in df.columns else "intensity"
    )

    # Integer bin index for every row
    df_bin = df.copy()
    df_bin["mz_bin"] = (df_bin["mz"] / bin_width).round().astype(int)

    # Keep highest intensity per bin
    binned = (
        df_bin.groupby("mz_bin", as_index=False)[["mz", int_col]]
        .max()
        .rename(columns={int_col: "intensity"})
    )

    return binned[["mz", "intensity"]]

def _process_sample(
    sample_path: Path,
    cfg: dict,
    blank_norms: Dict[str, pd.DataFrame],
    blank_specs_list: List[List[Tuple[float, Any, Any]]],
) -> None:
    """Run the full per‑sample workflow and write results to disk."""

    samp_log = logging.getLogger(__name__ + f".{sample_path.stem}")
    samp_log.info("Processing sample %s", sample_path.name)

    specs = load_and_index(str(sample_path))
    n_scans = len(specs)
    
    spec_avg_cfg = cfg.get("spectrum_avg", {})
    scan_indices = _build_scan_range(n_scans, spec_avg_cfg.get("start_index"), spec_avg_cfg.get("end_index"))
    
    tol_ppm: float = cfg["tol_ppm"]

    # ════════════════════════════════════════════════════════════════════════
    # Thermograms and integrated areas
    # ════════════════════════════════════════════════════════════════════════
    integ_records: list[tuple[str, float]] = []

    for compound in cfg["compounds"]:
        name = compound["name"]
        mzs = compound["mz"] if isinstance(compound["mz"], list) else [compound["mz"]]

        sample_df = extract_combined_thermogram(specs, mzs, tol_ppm)
        sample_norm = normalize_thermogram(sample_df, specs, cfg["charger_mzs"], tol_ppm)
        final_df = subtract_blank(sample_norm, blank_norms[name], on="RT")

        outfile = sample_path.with_suffix("")
        outfile = outfile.parent / f"{outfile.name}_{name.replace(' ', '_')}.csv"
        final_df.to_csv(outfile, index=False)
        samp_log.info("Thermogram → %s", outfile.name)

        auc = integrate_thermogram(final_df)
        samp_log.info("Integrated %s: %.6f", name, auc)
        integ_records.append((name, auc))

    if integ_records:
        integ_df = pd.DataFrame(integ_records, columns=["compound", "integrated_AUC"])
        integ_csv = sample_path.parent / f"{sample_path.with_suffix('').name}_integrals.csv"
        integ_df.to_csv(integ_csv, index=False)
        samp_log.debug("Integration summary → %s", integ_csv.name)

    # ════════════════════════════════════════════════════════════════════════
    # Spectra: raw, blank‑corrected, peaks
    # ════════════════════════════════════════════════════════════════════════
    """
    full_idx = _find_full_ms1_scan(specs, min_span=500.0)

    df_raw = extract_raw_spectrum(specs, scan_index=full_idx)
    df_blank = extract_raw_spectrum(blank_specs_list[0], scan_index=full_idx)
    """
    if scan_indices is None:
        # Fallback to first full‑range scan as before
        full_idx = next(i for i, (_, mzs, _) in enumerate(specs) if mzs.max() - mzs.min() >= 500)
        df_raw = extract_raw_spectrum(specs, scan_index=full_idx)
        df_blank = extract_raw_spectrum(blank_specs_list[0], scan_index=full_idx)
    else:
        df_raw = extract_combined_spectrum(specs, scan_indices)
        df_blank = extract_combined_spectrum(blank_specs_list[0], scan_indices)
    
    df_corr = remove_blank_spectrum(df_raw, df_blank, tol_ppm)
    peaks = extract_peaks(df_corr)

    base_dir = sample_path.parent
    stem = sample_path.with_suffix("").name

    df_raw.to_parquet(base_dir / f"{stem}_spectrum.parquet", index=False, compression="zstd")
    df_corr.to_parquet(base_dir / f"{stem}_spectrum_bckgremoved.parquet", index=False, compression="zstd")
    peaks.to_csv(base_dir / f"{stem}_spectrum_peaksonly.csv", index=False)
    samp_log.info("Exported spectra for %s", stem)

    # ════════════════════════════════════════════════════════════════════════
    # Optional Kendrick plot
    # ════════════════════════════════════════════════════════════════════════
    if (kmd_cfg := cfg.get("kmd")):
        #scan_idx = kmd_cfg.get("scan_index", 0)
        #use_peaks = kmd_cfg.get("use_peaks", False)
        bin_w = float(kmd_cfg.get("bin_width", 0.0005))   # NEW YAML key
        nb = kmd_cfg.get("nominal_base", 14.0)
        eb = kmd_cfg.get("exact_base", 14.01565)
        outdir = Path(kmd_cfg.get("output_dir", str(base_dir)))
        outdir.mkdir(parents=True, exist_ok=True)
        
        spec_for_kmd = peaks if kmd_cfg.get("use_peaks", False) else df_corr
        spec_for_kmd = _bin_spectrum(spec_for_kmd, bin_w) # NEW helper
        kmd_df = compute_kmd(
            spec_for_kmd,
            intensity_col="intensity",         # <-- NEW
            nominal_base=nb,
            exact_base=eb,
        )

        plot_kmd(kmd_df, output_file=str(outdir / f"{stem}_kmd.png"))
        samp_log.info("KMD plot saved for %s", stem)
"""
        kmd_raw = extract_raw_spectrum(specs, scan_index=scan_idx)
        kmd_blank = extract_raw_spectrum(blank_specs_list[0], scan_index=scan_idx)
        kmd_corr = remove_blank_spectrum(kmd_raw, kmd_blank, tol_ppm)
        spec_for_kmd = extract_peaks(kmd_corr) if use_peaks else kmd_corr

        kmd_df = compute_kmd(spec_for_kmd, nominal_base=nb, exact_base=eb)
        kmd_png = outdir / f"{stem}_kmd.png"
        plot_kmd(kmd_df, output_file=str(kmd_png))
        samp_log.info("KMD plot → %s", kmd_png)
"""
###############################################################################
# Public API
###############################################################################


def run_pipeline(cfg: dict, *, max_workers: int | None = None) -> None:
    """Execute the workflow with the provided *cfg* dictionary."""

    sample_dir = Path(cfg["sample_dir"]).expanduser().resolve()
    blank_dir = Path(cfg["blank_dir"]).expanduser().resolve()

    logger.info("Sample dir: %s", sample_dir)
    logger.info("Blank dir:  %s", blank_dir)

    blank_paths = sorted(blank_dir.glob("*.mzML.gz")) or sorted(blank_dir.glob("*.mzML"))
    if not blank_paths:
        raise FileNotFoundError(f"No mzML blanks found in {blank_dir}")

    logger.info("Indexing %d blank file(s)…", len(blank_paths))
    blank_specs = [load_and_index(str(p)) for p in blank_paths]

    # Pre‑compute blank‑normalised thermograms per compound
    tol_ppm = cfg["tol_ppm"]
    blank_norms: Dict[str, pd.DataFrame] = {}

    for compound in cfg["compounds"]:
        name = compound["name"]
        mzs = compound["mz"] if isinstance(compound["mz"], list) else [compound["mz"]]

        blank_dfs = [extract_combined_thermogram(s, mzs, tol_ppm) for s in blank_specs]
        avg_df = pd.concat(blank_dfs).groupby("RT", as_index=False)["intensity"].mean()
        blank_norms[name] = normalize_thermogram(avg_df, blank_specs[0], cfg["charger_mzs"], tol_ppm)

    # Launch workers for each sample file
    sample_paths = sorted(sample_dir.glob("*.mzML.gz")) or sorted(sample_dir.glob("*.mzML"))
    if not sample_paths:
        raise FileNotFoundError(f"No mzML samples found in {sample_dir}")

    logger.info("Processing %d sample file(s) with %s workers…", len(sample_paths), max_workers or "default")

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_process_sample, sp, cfg, blank_norms, blank_specs): sp.name for sp in sample_paths}

        for fut in as_completed(futures):
            sample_name = futures[fut]
            try:
                fut.result()
            except Exception as exc:  # pragma: no cover – log and continue
                logger.error("%s → ERROR: %s", sample_name, exc, exc_info=True)
            else:
                logger.info("%s → done", sample_name)
                
    logger.info("Pipeline complete.")
