"""
Copyright 2025 Prajwel Joseph

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from astropy.io import fits
from astropy.convolution import convolve, Gaussian2DKernel


__version__ = "0.2.0"


# To change mission elapsed time in seconds to modified julian date.
def met_to_mjd(met):
    jan2010 = 55197.0  # 2010.0(UTC) expressed with MJD format and scale UTC.
    mjd = (met / 86400.0) + jan2010  # 1 julian day = 86400 seconds.
    return mjd


def _read_columns(events_list):
    hdu = fits.open(events_list)
    framecount_per_sec = hdu[0].header["AVGFRMRT"]
    time = hdu[1].data["MJD_L2"]
    fx = hdu[1].data["Fx"]
    fy = hdu[1].data["Fy"]
    photons = hdu[1].data["EFFECTIVE_NUM_PHOTONS"]
    bad_flag = hdu[1].data["BAD FLAG"]
    mask = photons > 0
    mask = np.logical_and(mask, bad_flag)
    if "FrameCount" in hdu[1].data.names:
        first_frame_mask = hdu[1].data["FrameCount"] != 1
        mask = np.logical_and(mask, first_frame_mask)
    time = time[mask]
    fx = fx[mask]
    fy = fy[mask]
    return time, fx, fy, framecount_per_sec


def _get_peaks(light_curve, error_light_curve, time, num_consecutive, threshold):
    nan_mask = ~np.isnan(error_light_curve)
    source_time = time[nan_mask]
    source_light_curve = light_curve[nan_mask]
    source_light_curve_error = error_light_curve[nan_mask]

    non_zero_mask = source_light_curve_error > 0
    source_time = source_time[non_zero_mask]
    source_light_curve = source_light_curve[non_zero_mask]
    source_light_curve_error = source_light_curve_error[non_zero_mask]

    if source_light_curve.size == 0:
        return []

    light_curve_expected_value = np.median(source_light_curve)
    light_curve_threshold = threshold * light_curve_expected_value

    peak_mask = source_light_curve > light_curve_threshold
    peak_indices = np.where(peak_mask)[0]

    # Find where the difference is 1 (i.e., consecutive)
    diff = np.diff(peak_indices)
    consec = diff == 1

    # Add a 0 at the start and end to find group edges
    padded = np.concatenate(([0], consec.astype(int), [0]))
    diffs = np.diff(padded)

    # Start and end indices of groups of consecutive values
    starts = np.where(diffs == 1)[0]
    ends = np.where(diffs == -1)[0]

    # Collect indices for groups of length ≥ 3
    mask = np.zeros_like(peak_indices, dtype=bool)
    for start, end in zip(starts, ends):
        if (end - start + 1) >= num_consecutive:
            mask[start : end + 1] = True

    peak_indices = peak_indices[mask]
    return peak_indices


def _peak_method(
    time_bin_centers, histogram, error_histogram, num_consecutive, threshold
):
    candidates = []
    num_peaks_array = []
    light_curves = {}
    error_light_curves = {}
    for i in range(histogram.shape[0]):
        for j in range(histogram.shape[1]):
            light_curve = histogram[i, j, :]
            error_light_curve = error_histogram[i, j, :]
            light_curves[(i, j)] = light_curve
            error_light_curves[(i, j)] = error_light_curve
            peak_indices = _get_peaks(
                light_curve,
                error_light_curve,
                time_bin_centers,
                num_consecutive,
                threshold,
            )
            num_peaks = len(peak_indices)
            if num_peaks != 0:
                candidates.append([i, j])
                num_peaks_array.append(num_peaks)

    candidates = np.array(candidates)
    num_peaks_array = np.array(num_peaks_array)
    sort_order = np.argsort(num_peaks_array)[::-1]
    num_peaks_array = num_peaks_array[sort_order]
    candidates = candidates[sort_order]
    return candidates, num_peaks_array, light_curves, error_light_curves


def _normalized_excess_variance(light_curve, error_light_curve):
    nan_mask = ~np.isnan(error_light_curve)
    light_curve = light_curve[nan_mask]
    error_light_curve = error_light_curve[nan_mask]

    non_zero_mask = error_light_curve > 0
    light_curve = light_curve[non_zero_mask]
    error_light_curve = error_light_curve[non_zero_mask]

    if len(light_curve) == 0:
        return np.nan
    else:
        variance = np.var(light_curve)
        mean_squared = np.mean(light_curve) ** 2
        mean_squared_error = np.mean(error_light_curve**2)
        with np.errstate(all="ignore"):
            F = ((variance - mean_squared_error) / mean_squared) ** 0.5
        return np.round(F, 4)


def _excess_variance_method(histogram, error_histogram):
    candidates = []
    excess_variance_array = []
    light_curves = {}
    error_light_curves = {}
    for i in range(histogram.shape[0]):
        for j in range(histogram.shape[1]):
            light_curve = histogram[i, j, :]
            error_light_curve = error_histogram[i, j, :]
            light_curves[(i, j)] = light_curve
            error_light_curves[(i, j)] = error_light_curve
            excess_variance = _normalized_excess_variance(
                light_curve, error_light_curve
            )
            if excess_variance > 0:
                candidates.append([i, j])
                excess_variance_array.append(excess_variance)

    candidates = np.array(candidates)
    excess_variance_array = np.array(excess_variance_array)
    sort_order = np.argsort(excess_variance_array)[::-1]
    excess_variance_array = excess_variance_array[sort_order]
    candidates = candidates[sort_order]
    return candidates, excess_variance_array, light_curves, error_light_curves


def find_candidates(
    events_list=None,
    time_bin_size=20,
    spatial_bin_size=32,
    method="excess",
    num_consecutive=3,
    threshold=3,
):
    time, fx, fy, framecount_per_sec = _read_columns(events_list)
    unique_time = np.unique(time)
    event_data = np.column_stack((fx, fy, time))

    n_xbins = 4800 // spatial_bin_size
    n_ybins = n_xbins
    n_tbins = int((time.max() - time.min()) / time_bin_size)
    time_max = time.min() + (time_bin_size * n_tbins)

    unique_histogram, time_bin_edges = np.histogram(
        unique_time, bins=n_tbins, range=(time.min(), time_max)
    )
    unique_histogram = unique_histogram.astype("float")

    include_left = np.concatenate(([False], unique_histogram > 0))
    include_right = np.concatenate((unique_histogram > 0, [False]))
    time_bin_edges_mask = np.logical_or(include_left, include_right)
    time_bin_edges = time_bin_edges[time_bin_edges_mask]

    unique_histogram, time_bin_edges = np.histogram(unique_time, bins=time_bin_edges)
    unique_histogram = unique_histogram.astype("float")

    histogram, _ = np.histogramdd(
        event_data,
        bins=[n_xbins, n_ybins, time_bin_edges],
        range=[(0, 4800), (0, 4800), (time.min(), time_max)],
    )

    # To avoid bins with few frames.
    unique_histogram[unique_histogram < np.nanmedian(unique_histogram) / 2] = np.nan

    error_histogram = np.sqrt(histogram) / unique_histogram
    histogram = histogram / unique_histogram

    histogram = histogram * framecount_per_sec
    error_histogram = error_histogram * framecount_per_sec

    # To remove light curves with few data points.
    lightcurve_sums = np.nansum(histogram > 0, axis=-1)
    valid_data_median = np.median(lightcurve_sums[lightcurve_sums > 0])
    minimum_data_mask = lightcurve_sums < (valid_data_median / 2)
    minimum_data_mask_3d = np.broadcast_to(
        minimum_data_mask[:, :, np.newaxis], histogram.shape
    )
    histogram[minimum_data_mask_3d] = np.nan
    error_histogram[minimum_data_mask_3d] = np.nan

    time_bin_centers = 0.5 * (time_bin_edges[:-1] + time_bin_edges[1:])

    if method == "peaks":
        candidates, significance_array, light_curves, error_light_curves = _peak_method(
            time_bin_centers, histogram, error_histogram, num_consecutive, threshold
        )
    elif method == "excess":
        candidates, significance_array, light_curves, error_light_curves = (
            _excess_variance_method(histogram, error_histogram)
        )
    else:
        raise ValueError(f"Invalid value for method: '{method}'")

    return (
        candidates,
        significance_array,
        time_bin_centers,
        light_curves,
        error_light_curves,
    )


def print_candidates(
    candidates=None, significance_array=None, spatial_bin_size=None, how_many=5
):
    for candidate, significance in zip(
        candidates[:how_many], significance_array[:how_many]
    ):
        candidate_coo = (candidate + 0.5) * spatial_bin_size
        candidate_coo = candidate_coo.astype(int)
        print(
            f"Candidate at {candidate} bin ({candidate_coo} pixel), measure of significance = {significance}"
        )


def get_curves_locations(
    events_list=None,
    candidates=None,
    time_bin_centers=None,
    light_curves=None,
    error_light_curves=None,
    spatial_bin_size=None,
    how_many=5,
    output_prefix="revealit",
    figure_bin_size=2**1,
    figure_percentile=99.95,
    figure_dpi=150,
    light_curve_figure_size=(15, 5),
):

    candidates = candidates[:how_many]
    _, fx, fy, _ = _read_columns(events_list)
    n_xbins = 4800 // figure_bin_size
    n_ybins = n_xbins
    binned_image, _, _ = np.histogram2d(
        fy, fx, range=[(0, 4800), (0, 4800)], bins=[n_xbins, n_ybins]
    )

    Gaussian_kernel = Gaussian2DKernel(1.5, x_size=3, y_size=3)
    smoothed_binned_image = convolve(binned_image, Gaussian_kernel)

    fig, ax = plt.subplots()
    ax.imshow(
        smoothed_binned_image,
        vmin=np.median(smoothed_binned_image),
        vmax=np.percentile(smoothed_binned_image, figure_percentile),
        origin="lower",
        cmap="coolwarm",
    )

    for candidate_index in range(len(candidates)):
        source_coo = candidates[candidate_index]
        source_coo_scaled = source_coo * spatial_bin_size / figure_bin_size
        bin_coords_with_offset = (
            source_coo_scaled[0] - 0.5,
            source_coo_scaled[1] - 0.5,
        )
        rectangle = patches.Rectangle(
            bin_coords_with_offset,
            spatial_bin_size / figure_bin_size,
            spatial_bin_size / figure_bin_size,
            linewidth=2,
            fill=False,
        )
        ax.add_patch(rectangle)
        ax.annotate(f"{candidate_index}", bin_coords_with_offset)

    fig.savefig(f"{output_prefix}_candidate_locations.png", dpi=figure_dpi)
    plt.close("all")

    for candidate_index in range(len(candidates)):
        source_coo = candidates[candidate_index]
        bin_coords = (source_coo[0], source_coo[1])
        light_curve = light_curves[bin_coords]
        error_light_curve = error_light_curves[bin_coords]
        _plot_curve(
            candidate_index,
            source_coo,
            time_bin_centers,
            light_curve,
            error_light_curve,
            output_prefix,
            light_curve_figure_size,
            figure_dpi,
        )

    image_4800x4800, _, _ = np.histogram2d(
        fy, fx, range=[(0, 4800), (0, 4800)], bins=[4800, 4800]
    )
    for candidate_index in range(len(candidates)):
        source_coo = candidates[candidate_index]
        source_coo_scaled = source_coo * spatial_bin_size
        source_coo_scaled = source_coo_scaled.astype("int")
        sub_image_size = int(spatial_bin_size)
        x1 = source_coo_scaled[0]
        x2 = x1 + sub_image_size
        y1 = source_coo_scaled[1]
        y2 = y1 + sub_image_size
        cropped_image = image_4800x4800[y1:y2, x1:x2]
        fig, ax = plt.subplots()
        ax.imshow(
            cropped_image,
            vmin=np.mean(cropped_image) / 2,
            vmax=np.percentile(cropped_image, figure_percentile),
            origin="lower",
            cmap="coolwarm",
        )
        ax.set_title(f"Zoomed image for bin {source_coo}")
        fig.savefig(
            f"{output_prefix}_candidate_{candidate_index}_zoomed_image.png",
            dpi=figure_dpi,
        )
        plt.close("all")


def _plot_curve(
    candidate_index,
    source_coo,
    time_bin_centers,
    light_curve,
    error_light_curve,
    output_prefix,
    light_curve_figure_size,
    figure_dpi,
):
    nan_mask = ~np.isnan(error_light_curve)
    source_time = time_bin_centers[nan_mask]
    source_light_curve = light_curve[nan_mask]
    source_light_curve_error = error_light_curve[nan_mask]

    non_zero_mask = source_light_curve > 0
    source_time = source_time[non_zero_mask]
    source_light_curve = source_light_curve[non_zero_mask]
    source_light_curve_error = source_light_curve_error[non_zero_mask]

    fig, ax = plt.subplots(figsize=light_curve_figure_size)
    ax.errorbar(
        met_to_mjd(source_time),
        source_light_curve,
        yerr=source_light_curve_error,
        fmt=".",
        alpha=0.8,
    )
    ax.set_xlabel("Time (MJD)")
    ax.set_ylabel("CPS")
    ax.set_title(f"Light curve for bin {source_coo}")
    fig.savefig(f"{output_prefix}_candidate_{candidate_index}_MJD.png", dpi=figure_dpi)
    plt.close("all")

    fig, ax = plt.subplots(figsize=light_curve_figure_size)
    ax.errorbar(
        np.arange(len(source_time)),
        source_light_curve,
        yerr=source_light_curve_error,
        fmt=".",
        alpha=0.8,
    )
    ax.set_xlabel("Index")
    ax.set_ylabel("CPS")
    ax.set_title(f"Light curve for bin {source_coo}")
    fig.savefig(
        f"{output_prefix}_candidate_{candidate_index}_index.png", dpi=figure_dpi
    )
    plt.close("all")
