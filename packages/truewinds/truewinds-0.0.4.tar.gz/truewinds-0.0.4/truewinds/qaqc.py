import numpy as np
from numpy.typing import ArrayLike


class FillValue:
    COG: float = -1111.0  # Course over ground
    SOG: float = -9999.0  # Speed over ground
    WIND_DIR: float = 1111.0  # Wind direction
    WIND_SPEED: float = 9999.0  # Wind speed
    HEADING: float = 5555.0  # Heading


class FLAG:
    NOT_EVALUATED: int = 0
    OK: int = 1
    PROBABLY_OK: int = 2
    PROBABLY_BAD: int = 3
    BAD: int = 4
    MISSING_VALUE: int = 9


def flag_direction(direction: ArrayLike | int | float) -> np.array:
    """
    Flag a direction value, in degrees, if it exceeds the gross range of 0 to 360 degrees.
    :param direction: An array-like object containing direction values in degrees.
    :return: A numpy array of flags where 1 indicates OK and 4 indicates BAD.
    """
    flag = np.where((direction < 0) | (direction > 360), FLAG.BAD, FLAG.OK)
    return flag


def flag_speed(speed: ArrayLike | int | float,
               operator_min: float | None = None,
               operator_max: float | None = None) -> np.array:
    """
    Flag a speed value, in user defined units, if it is less than 0 or exceeds the operator-defined limits.

    :param speed: An array-like object containing speed values.
    :param operator_min: If supplied, values between 0 and the operator_min will be flagged as PROBABLY_OK.
    :param operator_max: If supplied, values exceeding the operator_max will be flagged as PROBABLY_OK.
    :return: A numpy array of flags where 1 indicates OK, 2 indicates PROBABLY_OK, and 4 indicates BAD.
    """
    flag = np.full_like(speed, FLAG.OK).astype(int)
    if operator_min is not None and operator_max is not None:
        flag = np.where((speed <= operator_min) | (speed >= operator_max), FLAG.PROBABLY_OK, FLAG.OK)
    flag = np.where(speed < 0, FLAG.BAD, flag)
    return flag


def check_zlr(zlr: float) -> None:
    """
    Verify that the zero line reference (zlr) is a valid value.
    If the input zlr is impossible (value less than 0 or greater than 360), then a ValueError is raised.

    :param zlr: A floating point value representing the zero line reference in degrees.
    :return: None
    """
    if zlr < 0 or zlr > 360:
        msg = 'Zero line reference must be a positive floating point value between 0 and 360 degrees.'
        raise ValueError(msg)
