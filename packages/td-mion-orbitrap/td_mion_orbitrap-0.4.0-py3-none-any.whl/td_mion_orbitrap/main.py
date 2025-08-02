import sys, os
# Ensure this script's directory is on the import path (for multiprocessing child processes)
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import yaml
import logging
import pandas as pd
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

from td_mion_orbitrap.thermo import load_and_index, extract_thermogram
from td_mion_orbitrap.blank import extract_combined_thermogram, normalize_thermogram, subtract_blank
from td_mion_orbitrap.spectrum import extract_raw_spectrum, remove_blank_spectrum, extract_peaks
from td_mion_orbitrap.integration import integrate_thermogram
from td_mion_orbitrap.kmd import compute_kmd, plot_kmd

logging.basicConfig(
    filename='pipeline.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

def find_full_ms1_scan(specs, min_span=200.0):
    """
    Return the index of the first scan whose mz-array spans at least min_span Da.
    """
    for i, (rt, mzs, vals) in enumerate(specs):
        if mzs.max() - mzs.min() >= min_span:
            return i
    raise RuntimeError("No full‐range scan found")

def process_sample(sample_path: Path, cfg: dict, blank_norms: dict, blank_specs_list: list) -> list:
    """
    Process one sample. Return a list of log messages (level, message).
    """
    logs = []
    def log(level, msg, *args):
        logs.append((level, msg % args if args else msg))

    sample_name = sample_path.stem
    log('INFO', '=== Processing sample %s ===', sample_name)

    # Load sample
    sample_specs = load_and_index(str(sample_path))
    log('INFO', 'Indexed sample: %s', sample_path.name)

    tol_ppm = cfg['tol_ppm']
    # Charger baseline
    baseline = sum(
        extract_thermogram(sample_specs, mz, tol_ppm)['intensity'].mean()
        for mz in cfg['charger_mzs']
    )
    log('INFO', 'Sample charger baseline = %.1f', baseline)

    # Compounds
    for cmpd in cfg['compounds']:
        name  = cmpd['name']
        mzs   = cmpd['mz'] if isinstance(cmpd['mz'], list) else [cmpd['mz']]
        sample_df = extract_combined_thermogram(sample_specs, mzs, tol_ppm)
        blank_norm = blank_norms[name]
        sample_norm = normalize_thermogram(sample_df, sample_specs, cfg['charger_mzs'], tol_ppm)
        final_df = subtract_blank(sample_norm, blank_norm, on='RT')
        log('INFO', 'Subtracted blank for %s', name)

        out_csv = sample_path.parent / f"{sample_name}_{name.replace(' ', '_')}.csv"
        final_df.to_csv(out_csv, index=False)
        log('INFO', 'Wrote thermogram CSV: %s', out_csv.name)

        total = integrate_thermogram(final_df)
        log('INFO', "Integrated signal for %s in %s: %.6f", name, str(sample_name), total)

    # Spectrum outputs
    full_idx = find_full_ms1_scan(sample_specs, min_span=500.0)
    df_raw   = extract_raw_spectrum(sample_specs, scan_index=full_idx)
    df_blank = extract_raw_spectrum(blank_specs_list[0], scan_index=full_idx)
    df_corr  = remove_blank_spectrum(df_raw, df_blank, tol_ppm)
    peaks    = extract_peaks(df_corr)

    base = sample_path.parent
    df_raw.to_csv(base / f"{sample_name}_spectrum.csv", index=False)
    df_corr.to_csv(base / f"{sample_name}_spectrum_bckgremoved.csv", index=False)
    peaks.to_csv(base / f"{sample_name}_spectrum_peaksonly.csv", index=False)
    log('INFO', 'Exported spectra & peaks for %s', sample_name)

    # KMD
    kmd_cfg = cfg.get('kmd', {})
    if kmd_cfg:
        scan_idx  = kmd_cfg.get('scan_index', 0)
        use_peaks = kmd_cfg.get('use_peaks', False)
        nb = kmd_cfg.get('nominal_base', 14.0)
        eb = kmd_cfg.get('exact_base', 14.01565)
        outdir = Path(kmd_cfg.get('output_dir', str(base)))
        outdir.mkdir(parents=True, exist_ok=True)

        df_kmd_raw   = extract_raw_spectrum(sample_specs, scan_index=scan_idx)
        df_kmd_blank = extract_raw_spectrum(blank_specs_list[0], scan_index=scan_idx)
        df_kmd_corr  = remove_blank_spectrum(df_kmd_raw, df_kmd_blank, tol_ppm)
        spec_kmd = extract_peaks(df_kmd_corr) if use_peaks else df_kmd_corr

        kmd_df = compute_kmd(spec_kmd, nominal_base=nb, exact_base=eb)
        kmd_file = outdir / f"{sample_name}_kmd.png"
        plot_kmd(kmd_df, output_file=str(kmd_file))
        log('INFO', 'Saved KMD plot: %s', kmd_file.name)

    return logs


def main(config_file: str):
    # Load config
    with open(config_file, encoding='utf-8-sig') as f:
        cfg = yaml.safe_load(f)

    sample_dir = Path(cfg['sample_dir'])
    blank_dir  = Path(cfg['blank_dir'])

    # Index blanks and cache norms
    blank_paths = sorted(blank_dir.glob("*.mzML.gz"))
    blank_specs = [load_and_index(str(p)) for p in blank_paths]
    blank_norms = {}
    for cmpd in cfg['compounds']:
        name = cmpd['name']
        mzs  = cmpd['mz'] if isinstance(cmpd['mz'], list) else [cmpd['mz']]
        dfs = [extract_combined_thermogram(s, mzs, cfg['tol_ppm']) for s in blank_specs]
        avg = pd.concat(dfs).groupby('RT', as_index=False)['intensity'].mean()
        blank_norms[name] = normalize_thermogram(avg, blank_specs[0], cfg['charger_mzs'], cfg['tol_ppm'])

    logging.info('\n=== Starting parallel processing ===\n')
    sample_paths = sorted(sample_dir.glob("*.mzML.gz"))
    futures = []
    with ProcessPoolExecutor() as executor:
        for sp in sample_paths:
            futures.append(executor.submit(process_sample, sp, cfg, blank_norms, blank_specs))

        # Gather logs as tasks complete
        for future in as_completed(futures):
            try:
                for level, msg in future.result():
                    getattr(logging, level.lower())(msg)
            except Exception as e:
                logging.error('Error in sample task: %s', e)

    logging.info('\n=== Pipeline complete ===\n')

if __name__ == '__main__':
    main('config.yaml')
