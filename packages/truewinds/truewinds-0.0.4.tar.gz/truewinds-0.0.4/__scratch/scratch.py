def _calc_twd(x,y):
    calm_flag = 1
    if np.abs(x) > 1e-05:
        mdir = np.arctan2(y, x) * (180/np.pi)
    else:
        if np.abs(y) > 1e-05:
            mdir = 180 - (90 * y) / np.abs(y)
        else:
            mdir = 270
            calm_flag = 0
    return mdir, calm_flag
vfunc = np.vectorize(_calc_twd)
result = vfunc(x,y)


## Rework
#mtdir = np.full_like(x, 270)

#mtdir = np.where((np.abs(x) <= 1e-05) & (np.abs(y) > 1e-05), 180-(90*y)/np.abs(y), mtdir)
#calm = np.where((np.abs(x) <= 1e-05) & (np.abs(y) <= 1e-05), 0, calm)




### NEEDS TESTS
# def mean_direction(degrees: ArrayLike) -> float:
#     radians = deg2rad(degrees)
#     mean_rad = np.arctan2(np.sum(np.sin(radians)), np.sum(np.cos(radians)))
#     mean_deg = rad2deg(mean_rad) % 360
#     return mean_deg
#
