import json
import subprocess
from pathlib import Path
from typing import Optional

import click
import nibabel
import numpy as np
import pydicom
import simple_mri as sm
from loguru import logger

VOLUME_LABELS = [
    "IR-modulus",
    "IR-real",
    "IR-corrected-real",
    "SE-modulus",
    "SE-real",
    "T1map-scanner",
]


@click.command("dcm2nii-mixed")
@click.argument("dcmpath", type=Path, required=True)
@click.argument("outpath", type=Path, required=True)
@click.option("--subvolume", "subvolumes", type=str, multiple=True, default=None)
def dcm2nii_mixed_cli(*args, **kwargs):
    dcm2nii_mixed(*args, **kwargs)


def dcm2nii_mixed(
    dcmpath: Path,
    outpath: Path,
    subvolumes: Optional[list[str]] = None,
):
    subvolumes = subvolumes or VOLUME_LABELS
    assert all([volname in VOLUME_LABELS for volname in subvolumes]), (
        f"Invalid subvolume name in {subvolumes}, not in {VOLUME_LABELS}"
    )
    outdir, form = outpath.parent, outpath.stem
    outdir.mkdir(exist_ok=True, parents=True)

    vols = extract_mixed_dicom(dcmpath, subvolumes)
    meta = {}
    for vol, volname in zip(vols, subvolumes):
        output = outpath.with_name(outpath.stem + "_" + volname + ".nii.gz")

        nii = vol["nifti"]
        descrip = vol["descrip"]
        nibabel.nifti1.save(nii, output)
        try:
            if volname == "SE-modulus":
                meta["TR_SE"] = descrip["TR"]
                meta["TE"] = descrip["TE"]
                meta["ETL"] = descrip["ETL"]
            elif volname == "IR-corrected-real":
                meta["TR_IR"] = descrip["TR"]
                meta["TI"] = descrip["TI"]
        except KeyError as e:
            print(volname, descrip)
            raise e

    with open(outpath.parent / f"{form}_meta.json", "w") as f:
        json.dump(meta, f)

    try:
        cmd = f"dcm2niix -w 0 --terse -b o -f '{form}' -o '{outdir}' '{dcmpath}' >> /tmp/dcm2niix.txt "
        subprocess.run(cmd, shell=True).check_returncode()
    except (ValueError, subprocess.CalledProcessError) as e:
        print(str(e))
        pass

    pass


def extract_mixed_dicom(dcmpath: Path, subvolumes: list[str]):
    dcm = pydicom.dcmread(dcmpath)
    frames_total = int(dcm.NumberOfFrames)
    frames_per_volume = dcm[0x2001, 0x1018].value  # [Number of Slices MR]
    num_volumes = frames_total // frames_per_volume
    assert num_volumes * frames_per_volume == frames_total, (
        "Subvolume dimensions do not match"
    )

    D = dcm.pixel_array.astype(np.single)
    frame_fg_sequence = dcm.PerFrameFunctionalGroupsSequence

    vols_out = []
    for volname in subvolumes:
        vol_idx = VOLUME_LABELS.index(volname)

        # Find volume slices representing current subvolume
        subvol_idx_start = vol_idx * frames_per_volume
        subvol_idx_end = (vol_idx + 1) * frames_per_volume
        frame_fg = frame_fg_sequence[subvol_idx_start]
        logger.info(
            (
                f"Converting volume {vol_idx + 1}/{len(VOLUME_LABELS)}: {volname} between indices"
                + f"{subvol_idx_start, subvol_idx_end} / {frames_total}."
            )
        )
        mri = extract_single_volume(D[subvol_idx_start:subvol_idx_end], frame_fg)

        nii_oriented = nibabel.nifti1.Nifti1Image(mri.data, mri.affine)
        nii_oriented.set_sform(nii_oriented.affine, "scanner")
        nii_oriented.set_qform(nii_oriented.affine, "scanner")

        # Include meta-data
        description = {
            "TR": float(
                frame_fg.MRTimingAndRelatedParametersSequence[0].RepetitionTime
            ),
            "TE": float(frame_fg.MREchoSequence[0].EffectiveEchoTime),
        }
        if hasattr(frame_fg.MRModifierSequence[0], "InversionTimes"):
            description["TI"] = frame_fg.MRModifierSequence[0].InversionTimes[0]
        if hasattr(frame_fg.MRTimingAndRelatedParametersSequence[0], "EchoTrainLength"):
            description["ETL"] = frame_fg.MRTimingAndRelatedParametersSequence[
                0
            ].EchoTrainLength
        vols_out.append({"nifti": nii_oriented, "descrip": description})
    return vols_out


def extract_single_volume(
    D: np.ndarray,
    frame_fg: pydicom.Dataset,
) -> sm.SimpleMRI:
    # Find scaling values (should potentially be inside scaling loop)
    pixel_value_transform = frame_fg.PixelValueTransformationSequence[0]
    slope = float(pixel_value_transform.RescaleSlope)
    intercept = float(pixel_value_transform.RescaleIntercept)
    private = frame_fg[0x2005, 0x140F][0]
    scale_slope = private[0x2005, 0x100E].value

    # Loop over and scale values.
    volume = np.zeros_like(D, dtype=np.single)
    for idx in range(D.shape[0]):
        volume[idx] = (intercept + slope * D[idx]) / (scale_slope * slope)

    A_dcm = dicom_standard_affine(frame_fg)
    C = sm.change_of_coordinates_map("LPS", "RAS")
    mri = sm.data_reorientation(sm.SimpleMRI(volume, C @ A_dcm))

    return mri


def dicom_standard_affine(
    frame_fg: pydicom.Dataset,
) -> np.ndarray:
    # Get the original data shape
    df = float(frame_fg.PixelMeasuresSequence[0].SpacingBetweenSlices)
    dr, dc = (float(x) for x in frame_fg.PixelMeasuresSequence[0].PixelSpacing)
    plane_orientation = frame_fg.PlaneOrientationSequence[0]
    orientation = np.array(plane_orientation.ImageOrientationPatient)

    # Find orientation of data array relative to LPS-coordinate system.
    row_cosine = orientation[:3]
    col_cosine = orientation[3:]
    frame_cosine = np.cross(row_cosine, col_cosine)

    # Create DICOM-definition affine map to LPS.
    T_1 = np.array(frame_fg.PlanePositionSequence[0].ImagePositionPatient)

    # Create DICOM-definition affine map to LPS.
    M_dcm = np.zeros((4, 4))
    M_dcm[:3, 0] = row_cosine * dc
    M_dcm[:3, 1] = col_cosine * dr
    M_dcm[:3, 2] = frame_cosine * df
    M_dcm[:3, 3] = T_1
    M_dcm[3, 3] = 1.0

    # Reorder from "natural index order" to DICOM affine map definition order.
    N_order = np.eye(4)[[2, 1, 0, 3]]
    return M_dcm @ N_order


def repetition_time(shared_fg: pydicom.Dataset, frame_fg: pydicom.Dataset) -> float:
    if hasattr(frame_fg, "MRTimingAndRelatedParametersSequence"):
        return shared_fg.MRTimingAndRelatedParametersSequence[0].RepetitionTime
    elif hasattr(shared_fg, "MRTimingAndRelatedParametersSequence"):
        logger.warning(
            "Repetition time not found in frame functional group, using shared functional group."
        )
        return shared_fg.MRTimingAndRelatedParametersSequence[0].RepetitionTime
    raise ValueError("Can't find repetition time in shared or frame functional groups")
