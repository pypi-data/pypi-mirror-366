import calendar
from datetime import datetime
from pygeomag import GeoMag


def dt2dy(dt: datetime) -> float:
    """
    Convert a Pyton datetime object to a float value that represents the decimal year.
    :param dt: A datetime.datetime object.
    :return: A float value representing the decimal year.
    """

    year = dt.year
    total_year_days = calendar.isleap(year) + 365
    day_of_year = dt.timetuple().tm_yday
    ydf = day_of_year / total_year_days
    decimal_year = year + ydf
    return decimal_year


def estimate_magnetic_declination(time: datetime,
                                  latitude: float,
                                  longitude: float,
                                  altitude: float = 0.0,
                                  high_resolution: bool = False):
    """
    Estimate the magnetic declination at a given time and position using the PyGeomag package.

    For data older than 2010, the default coefficients are used.

    :param time: The input time as a datetime object.
    :param latitude: The latitude of the measurement location in degrees.
    :param longitude: The longitude of the measurement location in degrees.
    :param altitude: The altitude of the measurement location in meters. Default is 0.0 m.
    :param high_resolution: If True, use the high-resolution model. Currently, this is only available for time inputs
        from 2025 onward.
    :return: The estimated magnetic declination in degrees for the given inputs.
    """

    dy = dt2dy(time)  # Convert datetime to decimal year.
    gm = GeoMag(base_year=time, high_resolution=high_resolution)
    result = gm.calculate(glat=latitude, glon=longitude, alt=altitude, time=dy)
    mag_dec = result.d
    return gm, mag_dec
