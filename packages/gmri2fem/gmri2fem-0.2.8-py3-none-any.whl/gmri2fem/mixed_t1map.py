import json
from pathlib import Path
from typing import Optional

import click
import nibabel
import numpy as np
import scipy
import skimage
from numpy.lib.stride_tricks import sliding_window_view
from simple_mri import load_mri

from gmri2fem.masking import create_csf_mask


def T1_lookup_table(
    TRse: float, TI: float, TE: float, ETL: int, T1_low: float, T1_hi: float
) -> tuple[np.ndarray, np.ndarray]:
    TRfree = estimate_se_free_relaxation_time(TRse, TE, ETL)
    T1_grid = np.arange(int(T1_low), int(T1_hi + 1))
    Sse = 1 - np.exp(-TRfree / T1_grid)
    Sir = 1 - (1 + Sse) * np.exp(-TI / T1_grid)
    fractionCurve = Sir / Sse
    return fractionCurve, T1_grid


def estimate_se_free_relaxation_time(TRse, TE, ETL):
    """Compute free relaxation time following spin echo image from effective echo
    time TE and echo train length ETL, corrected for 20 dummy echoes."""
    return TRse - TE * (1 + 0.5 * (ETL - 1) / (0.5 * (ETL + 1) + 20))


def estimate_T1_mixed(
    SE_nii_path: Path,
    IR_nii_path: Path,
    meta_path: Path,
    T1_low: float,
    T1_hi: float,
) -> nibabel.nifti1.Nifti1Image:
    SE = load_mri(SE_nii_path, dtype=np.single)
    IR = load_mri(IR_nii_path, dtype=np.single)
    with open(meta_path, "r") as f:
        meta = json.load(f)

    nonzero_mask = SE.data != 0
    F_data = np.nan * np.zeros_like(IR.data)
    F_data[nonzero_mask] = IR.data[nonzero_mask] / SE.data[nonzero_mask]

    TR_se, TI, TE, ETL = meta["TR_SE"], meta["TI"], meta["TE"], meta["ETL"]
    F, T1_grid = T1_lookup_table(TR_se, TI, TE, ETL, T1_low, T1_hi)
    interpolator = scipy.interpolate.interp1d(
        F, T1_grid, kind="nearest", bounds_error=False, fill_value=np.nan
    )
    T1_volume = interpolator(F_data).astype(np.single)
    nii = nibabel.nifti1.Nifti1Image(T1_volume, IR.affine)
    nii.set_sform(nii.affine, "scanner")
    nii.set_qform(nii.affine, "scanner")
    return nii


def outlier_filter(
    vol: np.ndarray, window_size: int, threshold: float = 3
) -> np.ndarray:
    v = sliding_window_view(vol, [window_size] * vol.ndim)
    m = np.nanmedian(v, axis=(-2, -1))
    s = np.nanstd(v, axis=(-2, -1))
    med = np.zeros_like(vol)
    med[-window_size // 2 : window_size // 2, -window_size // 2 : window_size // 2] = m

    std = np.zeros_like(vol)
    std[-window_size // 2 : window_size // 2, -window_size // 2 : window_size // 2] = s

    return np.abs(vol - med) / std > threshold


def mask_csf(se: Path) -> np.ndarray:
    SE_mri = load_mri(se, np.single)
    mask = create_csf_mask(SE_mri.data, use_li=True)
    mask = skimage.morphology.binary_erosion(mask)
    return mask


def process_mixed_t1map(
    se: Path,
    ir: Path,
    meta: Path,
    output: Path,
    t1_low: float,
    t1_high: float,
    postprocessed: Optional[Path] = None,
):
    T1map_nii = estimate_T1_mixed(se, ir, meta, T1_low=t1_low, T1_hi=t1_high)
    nibabel.nifti1.save(T1map_nii, output)
    if postprocessed is not None:
        mixed_t1_postprocessing(se, output, postprocessed)


def mixed_t1_postprocessing(se: Path, t1: Path, output: Path):
    T1map_nii = nibabel.nifti1.load(t1)
    mask = mask_csf(se)
    masked_T1map = T1map_nii.get_fdata(dtype=np.single)
    masked_T1map[~mask] = np.nan
    masked_T1map_nii = nibabel.nifti1.Nifti1Image(
        masked_T1map, T1map_nii.affine, T1map_nii.header
    )
    nibabel.nifti1.save(masked_T1map_nii, output)


@click.command()
@click.option("--SE", type=Path, required=True)
@click.option("--IR", type=Path, required=True)
@click.option("--meta", type=Path, required=True)
@click.option("--output", type=Path, required=True)
@click.option("--t1_low", type=float, default=1.0)
@click.option("--t1_high", type=float, default=20000.0)
@click.option("--postprocessed", type=Path, required=True)
def mixed_t1map(**kwargs):
    process_mixed_t1map(**kwargs)


if __name__ == "__main__":
    mixed_t1map()
