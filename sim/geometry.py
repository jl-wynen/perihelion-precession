import numpy as np
import numba

@numba.jit(nopython=True)
def cart2pol(cartesian):
    return np.array((np.linalg.norm(cartesian), np.arctan2(cartesian[1], cartesian[0])))

@numba.jit(nopython=True)
def pol2cart(polar):
    return polar[0] * np.array((np.cos(polar[1]), np.sin(polar[1])))

@numba.jit(nopython=True)
def radial_transform(point, centre, rs, pow0=1, pow1=1):
    relative = point - centre
    r, phi = cart2pol(relative)

    if r <= rs:
        return None # already below rs (avoid further calculations)

    rnew = r * (1 - (rs/r)**pow0)**pow1

    if rnew < 0:
        return None  # below event-horizon

    return pol2cart((rnew, phi)) + centre

def flamm_depth(r, rs):
    return 2*np.sqrt(rs*(r-rs))

def flamm_paraboloid(points, centre, rs, ref_point=np.array((0, 0))):
    # radius of reference point from centre
    ref_radius = np.linalg.norm(ref_point - centre)

    # radii of points from centre, mask all below rs
    radii = np.ma.masked_less_equal(np.linalg.norm(points-centre, axis=1), rs)

    # Flamm depth of all points shifted up such that ref_point is at depth 0
    depths = flamm_depth(radii, rs) - flamm_depth(ref_radius, rs)

    # mask points where depths is masked
    masked_points = np.ma.masked_array(points,
                                       np.repeat(depths.mask[:, np.newaxis], 2, axis=1))

    return masked_points, depths


def flamm_projection(points, centre, rs, ref_point=np.array((0, 0)), screen=0, camera=None):
    if camera is None:
        camera = np.array((*centre, 100))

    # move points onto the paraboloid
    points, depths = flamm_paraboloid(points, centre, rs, ref_point)

    # scaling factor for projection
    depth_scales = abs((screen-camera[2])/(depths-camera[2]))

    # project points onto the screen
    projected = camera[:2] + (points-camera[:2])*np.expand_dims(depth_scales, axis=1)

    return projected

def make_grid(p0, p1, nlines, resolution):
    return (np.array([[(x, y) for x in np.linspace(p0[0], p1[0], resolution[0])]
                     for y in np.linspace(p0[1], p1[1], nlines[0])]),
            np.array([[(x, y) for y in np.linspace(p0[1], p1[1], resolution[1])]
                      for x in np.linspace(p0[0], p1[0], nlines[1])]))
