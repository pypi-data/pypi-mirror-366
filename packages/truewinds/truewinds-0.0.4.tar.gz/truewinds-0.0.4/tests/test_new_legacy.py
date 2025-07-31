from datetime import datetime, timezone
import numpy as np

from truewinds import compute_true_winds
from truewinds.legacy import truew

TEST_TIME = datetime.now(timezone.utc)

DUMMY_COG = 123.456  # Dummy course over ground.
DUMMY_SOG = 7.89  # Dummy speed over ground.
DUMMY_HDG = 45.67  # Dummy heading.
DUMMY_RWD = 12.34567  # Dummy relative wind direction.
DUMMY_RWS = 5.78  # Dummy relative wind speed.
DUMMY_ZLR = 180
RETURN_FLAGS = False

def test():

    ntw = compute_true_winds(cog = DUMMY_COG,
                            sog = DUMMY_SOG,
                            hdg = DUMMY_HDG,
                            rwd = DUMMY_RWD,
                            rws = DUMMY_RWS,
                            zlr = DUMMY_ZLR,
                            return_flags= RETURN_FLAGS)

    ltw = truew(crse = DUMMY_COG,
                cspd = DUMMY_SOG,
                wdir = DUMMY_RWD,
                zlr = DUMMY_ZLR,
                hd = DUMMY_HDG,
                wspd = DUMMY_RWS)

    # Round to nearest 5 decimal places for comparison.
    # Sometimes there are differences in floating point precision between the numpy and math modules.
    ntwd = np.round(ntw['true_wind_direction'], 5)
    ntws = np.round(ntw['true_wind_speed'], 5)

    ltwd = np.round(ltw[0], 5)
    ltws = np.round(ltw[1], 5)

    assert ntwd == ltwd
    assert ntws == ltws

