from datetime import datetime, timezone

from truewinds import compute_true_winds


TEST_TIME = datetime.now(timezone.utc)

DUMMY_COG = 123.456  # Dummy course over ground.
DUMMY_SOG = 7.89  # Dummy speed over ground.
DUMMY_HDG = 45.67  # Dummy heading.
DUMMY_RWD = 12.34567  # Dummy relative wind direction.
DUMMY_RWS = 5.78  # Dummy relative wind speed.
DUMMY_ZLR = 180
RETURN_FLAGS = True

def test():

    tw = compute_true_winds(cog = DUMMY_COG,
                            sog = DUMMY_SOG,
                            hdg = DUMMY_HDG,
                            rwd = DUMMY_RWD,
                            rws = DUMMY_RWS,
                            zlr = DUMMY_ZLR,
                            return_flags= RETURN_FLAGS)

    assert isinstance(tw['true_wind_direction'], float)
    assert isinstance(tw['true_wind_speed'], float)
    assert 'flag_sog' in list(tw.keys())
