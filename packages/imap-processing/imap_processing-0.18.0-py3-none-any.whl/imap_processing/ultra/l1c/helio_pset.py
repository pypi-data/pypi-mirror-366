"""Calculate Pointing Set Grids."""

import numpy as np
import pandas as pd
import xarray as xr

from imap_processing.spice.time import sct_to_et
from imap_processing.ultra.l1c.ultra_l1c_pset_bins import (
    build_energy_bins,
    get_helio_background_rates,
    get_helio_exposure_times,
    get_helio_sensitivity,
    get_spacecraft_histogram,
)
from imap_processing.ultra.utils.ultra_l1_utils import create_dataset


def calculate_helio_pset(
    de_dataset: xr.Dataset,
    extendedspin_dataset: xr.Dataset,
    cullingmask_dataset: xr.Dataset,
    name: str,
    ancillary_files: dict,
) -> xr.Dataset:
    """
    Create dictionary with defined datatype for Pointing Set Grid Data.

    Parameters
    ----------
    de_dataset : xarray.Dataset
        Dataset containing de data.
    extendedspin_dataset : xarray.Dataset
        Dataset containing extendedspin data.
    cullingmask_dataset : xarray.Dataset
        Dataset containing cullingmask data.
    name : str
        Name of the dataset.
    ancillary_files : dict
        Ancillary files.

    Returns
    -------
    dataset : xarray.Dataset
        Dataset containing the data.
    """
    pset_dict: dict[str, np.ndarray] = {}

    v_mag_helio_spacecraft = np.linalg.norm(
        de_dataset["velocity_dps_helio"].values, axis=1
    )
    vhat_dps_helio = (
        de_dataset["velocity_dps_helio"].values / v_mag_helio_spacecraft[:, np.newaxis]
    )
    intervals, _, energy_bin_geometric_means = build_energy_bins()
    counts, latitude, longitude, n_pix = get_spacecraft_histogram(
        vhat_dps_helio,
        de_dataset["energy_heliosphere"].values,
        intervals,
        nside=128,
    )

    healpix = np.arange(n_pix)

    # calculate background rates
    background_rates = get_helio_background_rates()

    efficiencies = ancillary_files["l1c-90sensor-efficiencies"]
    geometric_function = ancillary_files["l1c-90sensor-gf"]

    df_efficiencies = pd.read_csv(efficiencies)
    df_geometric_function = pd.read_csv(geometric_function)
    mid_time = sct_to_et(np.median(de_dataset["event_times"].data))
    sensitivity = get_helio_sensitivity(
        mid_time,
        df_efficiencies,
        df_geometric_function,
    )

    # Calculate exposure
    constant_exposure = ancillary_files["l1c-90sensor-dps-exposure"]
    df_exposure = pd.read_csv(constant_exposure)
    exposure_pointing = get_helio_exposure_times(mid_time, df_exposure)

    # For ISTP, epoch should be the center of the time bin.
    pset_dict["epoch"] = de_dataset.epoch.data[:1].astype(np.int64)
    pset_dict["counts"] = counts[np.newaxis, ...]
    pset_dict["latitude"] = latitude[np.newaxis, ...]
    pset_dict["longitude"] = longitude[np.newaxis, ...]
    pset_dict["energy_bin_geometric_mean"] = energy_bin_geometric_means
    pset_dict["background_rates"] = background_rates[np.newaxis, ...]
    pset_dict["helio_exposure_factor"] = exposure_pointing[np.newaxis, ...]
    pset_dict["pixel_index"] = healpix
    pset_dict["energy_bin_delta"] = np.diff(intervals, axis=1).squeeze()[
        np.newaxis, ...
    ]
    pset_dict["sensitivity"] = sensitivity[np.newaxis, ...]

    dataset = create_dataset(pset_dict, name, "l1c")

    return dataset
