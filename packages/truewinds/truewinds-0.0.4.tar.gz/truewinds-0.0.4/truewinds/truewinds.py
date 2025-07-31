import numpy as np
from numpy.typing import ArrayLike

from truewinds.core import deg2rad, rad2deg
from truewinds.qaqc import (FLAG,
                            flag_direction,
                            flag_speed,
                            check_zlr)

def compute_apparent_wind_direction(hdg: float | ArrayLike,
                                    rwd: float | ArrayLike,
                                    zlr: float = 0.0) -> float | ArrayLike:
    """
    Compute the apparent wind direction from the true heading, relative wind direction, and zero line reference.

    :param hdg: The true heading of the vessel or platform in degrees.
    :param rwd: The relative wind direction in degrees.
    :param zlr: The clockwise angle between the bow of the platform and the anemometer reference line in degrees.
    :return: The apparent wind direction in degrees.
    """

    # Compute apparent wind direction and reduce it to the range [0, 360].
    awd = hdg + rwd + zlr
    awd = awd % 360
    return awd


def compute_uv(true_wind_direction: float | ArrayLike,
               true_wind_speed: float | ArrayLike) -> tuple[float | ArrayLike, float | ArrayLike]:
    """
    Compute the u and v components of the true wind vector.

    :param true_wind_direction: True wind direction in degrees.
    :param true_wind_speed: True wind speed in the same units as the speed.
    :return: A tuple containing the u and v components of the true wind vector.
    """

    if np.all([isinstance(v, float | int) for v in [true_wind_direction, true_wind_speed]]):
        return_singleton = True
    else:
        return_singleton = False

    # Convert to Numpy arrays if the inputs are not already arrays.
    true_wind_direction = np.asarray(true_wind_direction)
    true_wind_speed = np.asarray(true_wind_speed)

    # Compute u and v components of the true wind vector.
    u = -1 * true_wind_speed * np.sin(deg2rad(true_wind_direction))
    v = -1 * true_wind_speed * np.cos(deg2rad(true_wind_direction))

    components = {'u_true_wind': u, 'v_true_wind': v}

    if return_singleton is True:
        components = {k: float(v) for k, v in components.items()}

    return components



def compute_true_winds(cog: float | ArrayLike,
                       sog: float | ArrayLike,
                       hdg: float | ArrayLike,
                       rwd: float | ArrayLike,
                       rws: float | ArrayLike,
                       zlr: float = 0.0,
                       return_flags: bool = True,
                       return_components: bool = True) -> dict[str, float | int | ArrayLike]:
    """
    Compute true wind direction and true wind speed from a moving reference frame, such as a vessel or mobile platform.

    This function is a vectorized adaptation of the original True Winds Python code written by Mylene Remigio
    and is based on the work of Smith et al. 1999. To use the original code, please use the legacy module.

    :param cog: Course over ground in degrees.
        Most often derived from a NMEA0183 VTG message.
    :param sog: Speed over ground.
        Most often derived from a NMEA0183 VTG message.
        Units for speed over ground much match relative wind speed (rws) units.
    :param hdg: The true heading of the vessel or platform in degrees.
        Most often derived from a NMEA0183 HDG message.
    :param rwd: Relative wind direction in degrees from which the wind is blowing. Derived from an anemometer on the platform.
    :param rws: Relative wind speed in the same units as speed over ground (sog).
        Derived from an anemometer on the platform.
    :param zlr: The clockwise angle between the bow of the platform and the anemometer reference line in degrees.
        Default is 0.0 degrees.
    :param return_flags: If True, flags are returned with the true wind dictionary.
    :return: A dictionary containing true wind direction and true wind speed
    """

    # Checks
    check_zlr(zlr)

    # Check input types.
    if np.all([isinstance(v, float | int) for v in [cog, sog, hdg, rwd, rws]]):
        return_singleton = True
    else:
        return_singleton = False

    # Convert to Numpy arrays if the inputs are not already arrays.
    cog = np.asarray(cog)
    sog = np.asarray(sog)
    hdg = np.asarray(hdg)
    rwd = np.asarray(rwd)
    rws = np.asarray(rws)

    # Flag data
    flag_cog = flag_direction(cog)
    flag_sog = flag_speed(sog)
    flag_hdg = flag_direction(hdg)
    flag_rwd = flag_direction(rwd)
    flag_rws = flag_speed(rws)

    # NaN bad data
    cog = np.where(flag_cog == FLAG.BAD, np.nan, cog)
    sog = np.where(flag_sog == FLAG.BAD, np.nan, sog)
    hdg = np.where(flag_hdg == FLAG.BAD, np.nan, hdg)
    rwd = np.where(flag_rwd == FLAG.BAD, np.nan, rwd)
    rws = np.where(flag_rws == FLAG.BAD, np.nan, rws)

    # Convert course over ground to math coordinates and ensure it is in the range [0, 360].
    mcog = 90 - cog
    mcog = np.where(mcog <= 0, mcog + 360, mcog)

    # Compute apparent wind direction.
    awd = compute_apparent_wind_direction(hdg=hdg, rwd=rwd, zlr=zlr)

    # Convert apparent wind direction to math coordinates and ensure it is in the range [0, 360].
    mawd = 270 - awd
    mawd = np.where(mawd <= 0, mawd + 360, mawd)
    mawd = np.where(mawd > 360, mawd - 360, mawd)

    # Compute true wind speed.
    x = rws * np.cos(deg2rad(mawd)) + sog * np.cos(deg2rad(mcog))
    y = rws * np.sin(deg2rad(mawd)) + sog * np.sin(deg2rad(mcog))
    tws = np.sqrt(x * x + y * y)

    # Compute true wind direction.
    mtwd = np.where((np.abs(x) > 1e-05), rad2deg(np.arctan2(y, x)), 180 - (90 * y) / np.abs(y))
    mtwd = np.where((np.abs(x) <= 1e-05) & (np.abs(y) <= 1e-05), 270,
                    mtwd)  # If both x, y are near 0, set math direction to 270.
    calm = np.where((np.abs(x) > 1e-05) & (np.abs(y) > 1e-05), 1,
                    0)  # Calm flag of 1 (True) indicates conditions are calm.
    twd = 270 - mtwd
    twd = np.where(twd < 0, np.abs(twd % -360) * calm, twd)
    twd = np.where(twd > 360, (twd % 360) * calm, twd)
    twd = np.where((calm == 1) & (twd < 1e-05), 360, twd)

    # Convert computed data to dictionaries.
    tw = {'true_wind_direction': twd,
          'true_wind_speed': tws}

    flags = {'flag_sog': flag_sog,
             'flag_cog': flag_cog,
             'flag_hdg': flag_hdg,
             'flag_rwd': flag_rwd,
             'flag_rws': flag_rws}

    if return_components is True:
        components = compute_uv(true_wind_direction=twd, true_wind_speed=tws)
        tw = tw | components

    if return_singleton is True:
        tw = {k: float(v) for k, v in tw.items()}
        flags = {k: int(v) for k, v in flags.items()}

    if return_flags is True:
        tw = tw | flags

    return tw

