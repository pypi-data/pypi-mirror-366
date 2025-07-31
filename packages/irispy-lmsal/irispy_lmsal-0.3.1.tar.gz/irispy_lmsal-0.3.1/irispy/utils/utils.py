"""
This module provides general utility functions.
"""

import numbers

import numpy as np
from scipy import interpolate, ndimage

import astropy.units as u
from astropy.modeling.models import custom_model

from irispy.utils.response import get_iris_response

__all__ = [
    "calculate_dust_mask",
    "calculate_uncertainty",
    "gaussian1d_on_linear_bg",
    "get_detector_type",
    "get_interpolated_effective_area",
    "image_clipping",
]


def image_clipping(image, cutoff=1.5e-3, gamma=1.0):
    """
    Computes and returns the min and max values of the input (image), clipping
    brightest and darkest pixels.

    Parameters
    ----------
    image : `numpy.ndarray`
        The input image.
    cutoff : float, optional
        The cutoff value for the histogram.
        Defaults to 1.5e-3
    gamma : float, optional
        The gamma value for the histogram.
        Defaults to 1.0

    References
    ----------
    Based on original IDL routine by P.Suetterlin (06 Jul 1993)
    Ported by V.Hansteen (15 Apr 2020)
    """
    hmin = np.min(image)
    hmax = np.max(image)
    if issubclass(image.dtype.type, numbers.Integral):
        nbins = np.abs(np.max(image) - np.min(image))
        hist = np.histogram(image, bins=nbins)
        fak = 1
    else:
        nbins = 10000
        fak = nbins / (hmax - hmin)
        hist = np.histogram((image - hmin) * fak, range=(0.0, float(nbins)), bins=nbins)
    h = hist[0]
    bins = hist[1]
    nh = np.size(h)
    # Integrate the histogram so that h(i) holds the number of points
    # with equal or lower intensity.
    for i in range(1, nh - 1):
        h[i] = h[i] + h[i - 1]
    h = h / float(h[nh - 2])
    h[nh - 1] = 1
    # As cutoff is in percent and h is normalized to unity,
    # vmin/vmax are the indices of the point where the number of pixels
    # with lower/higher intensity reach the given limit. This has to be
    # converted to a real image value by dividing by the scalefactor
    # fak and adding the min value of the image
    # Note that the bottom value is taken off (addition of h[0] to cutoff),
    # there are often very many points in IRIS images that are set to zero, this
    # removes them from calculation... and seems to work.
    vmin = (np.max(np.where(h <= (cutoff + h[0]), bins[1:] - bins[0], 0)) / fak + hmin) ** gamma
    vmax = (np.min(np.where(h >= (1.0 - cutoff), bins[1:] - bins[0], nh - 2)) / fak + hmin) ** gamma
    return vmin, vmax


@custom_model
def gaussian1d_on_linear_bg(
    x,
    amplitude=None,
    mean=None,
    standard_deviation=None,
    constant_term=None,
    linear_term=None,
):
    return amplitude * np.exp(-(((x - mean) / standard_deviation) ** 2)) + constant_term + linear_term * x


def get_detector_type(meta):
    """
    Gets the IRIS detector type from a meta dictionary.

    In this function, FUV1 and FUV2 are just assigned as FUV.

    Parameters
    ----------
    meta: dict-like
        Dictionary-like object containing entry for "detector type"

    Returns
    -------
    `str`
        Detector type.
    """
    return "FUV" if "FUV" in meta["detector type"] else meta["detector type"]


def get_interpolated_effective_area(time_obs, response_version, detector_type, obs_wavelength):
    """
    To compute the interpolated time-dependent effective area.

    It will generalize to the time of the observation.

    Parameters
    ----------
    time_obs : an `astropy.time.Time` object, as a kwarg, valid for version > 2
        Observation times of the datapoints.
        This argument is ignored for versions 1 and 2.
    response_version : `int`
        Version number of effective area file to be used. Cannot be set
        simultaneously with response_file or pre_launch kwarg. Default=4.
    detector_type : `str`
        Detector type: 'FUV' or 'NUV'.
    obs_wavelength : `astropy.units.Quantity`
        The wavelength at which the observation has been taken in Angstroms.

    Returns
    -------
    `numpy.array`
        The effective area(s) determined by interpolation with a spline fit.
    """
    iris_response = get_iris_response(time_obs, response_version=response_version)
    if detector_type == "FUV":
        detector_type_index = 0
    elif detector_type == "NUV":
        detector_type_index = 1
    else:
        msg = "Detector type not recognized."
        raise ValueError(msg)
    eff_area = iris_response["AREA_SG"][detector_type_index, :]
    response_wavelength = iris_response["LAMBDA"]
    # Interpolate the effective areas to cover the wavelengths
    # at which the data is recorded:
    eff_area_interp_base_unit = u.Angstrom
    tck = interpolate.splrep(
        response_wavelength.to(eff_area_interp_base_unit).value,
        eff_area.to(eff_area_interp_base_unit**2).value,
        s=0,
    )
    return interpolate.splev(obs_wavelength.to(eff_area_interp_base_unit).value, tck) * eff_area_interp_base_unit**2


def calculate_dust_mask(data_array):
    """
    Calculate a mask with the dust positions in a given array.

    Parameters
    ----------
    data_array : `numpy.ndarray`
        This array contains some dust position that will be calculated. The array
        must have scaled values.

    Returns
    -------
    `numpy.ndarray` of `bool`
        This array has the same shape than data_array and contains the dust positions
        when the value is True.
    """
    # Creating a mask with the same shape than the inputted data array.
    mask = np.zeros_like(data_array, dtype=bool)
    # Set the pixel value to True is the pixel is recognized as a dust pixel.
    mask[(data_array < 0.5) & (data_array > -200)] = True
    # Extending the mask to avoid the neighbours pixel influenced by the dust pixels.
    struct = np.array([np.zeros((3, 3)), np.ones((3, 3)), np.zeros((3, 3))], dtype=bool)
    return ndimage.binary_dilation(mask, structure=struct).astype(mask.dtype)


def calculate_uncertainty(data: np.array, readout_noise: u.Quantity, unit: u.Quantity) -> float:
    """
    Calculates the uncertainty of a given data array.

    Parameters
    ----------
    data : np.array
        The data array.
    readout_noise : u.Quantity
        The readout noise, needs to be a unit that is convertible to photon.
    unit : u.Quantity
        The final unit that the value should be converted to.

    Returns
    -------
    float
        The readout noise with no unit.
    """
    return (
        u.Quantity(
            np.sqrt((data * unit).to(u.photon).value + readout_noise.to(u.photon).value ** 2),
            unit=u.photon,
        )
        .to(unit)
        .value
    )
