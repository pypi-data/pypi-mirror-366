import numpy as np
from numpy.typing import ArrayLike


def deg2rad(degrees: float | ArrayLike) -> float | ArrayLike:
    """
    Convert degrees to radians.

    :param degrees: The angle in degrees.
    :return: Radians.
    """

    radians = degrees * np.pi / 180
    return radians


def rad2deg(radians: float | ArrayLike) -> float | ArrayLike:
    """
    Convert radians to degrees.

    :param radians: The angle in radians.
    :return: Degrees.
    """

    degrees = radians * 180 / np.pi
    return degrees


def knots2mps(knots: float | ArrayLike) -> float | ArrayLike:
    """
    Convert knots to meters per second.

    :param knots: Speed in knots.
    :return: Speed in meters per second.
    """

    mps = knots * 0.514444
    return mps


def kmph2mps(kmph: float | ArrayLike) -> float | ArrayLike:
    """
    Convert kilometers per hour to meters per second.

    :param kmph: Speed in kilometers per hour.
    :return: Speed in meters per second.
    """

    mps = kmph * 1000 / 3600
    return mps
