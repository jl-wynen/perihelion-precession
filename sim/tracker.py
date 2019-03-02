"""
Track extreme points of an orbit.
"""

import numpy as np

from .physics import CBody

class ExtremaTracker:
    """
    Track the radius of a body relative to another and perform user defined
    action when the periapsis or apapsis are found.
    """

    def __init__(self, reference_point, on_periapsis=None, on_apapsis=None):
        """
        Arguments:
            reference_point: CBody or coordinates relative to which radii are measured.
            on_periapsis: Function to call with the coordinates of each periapsis when found.
            on_apapsis: Function to call with the coordinates of each apapsis when found.
        """

        self.reference_point = reference_point.x if isinstance(reference_point, CBody) \
            else reference_point
        self.on_periapsis = on_periapsis
        self.on_apapsis = on_apapsis

        # radius currently increasing? (moving towards apapsis)
        self._increasing = None
        # raidus from last call to add_point()
        self._before = None

    def _process_radius(self, old, current, point):
        """Process a new radius."""

        if self._increasing is None:
            # first measured radius
            self._increasing = old < current

        elif self._increasing and old > current:
            # passed apapsis
            if self.on_apapsis:
                self.on_apapsis(point)
            self._increasing = False

        elif not self._increasing and old < current:
            # passed periapsis
            if self.on_periapsis:
                self.on_periapsis(point)
            self._increasing = True

    def add_point(self, point):
        """Add a new point to track, passedd in as coordinates or CBody."""

        if isinstance(point, CBody):
            point = point.x

        radius = np.linalg.norm(self.reference_point - point)

        if self._before is not None:
            self._process_radius(self._before, radius, point)

        self._before = radius

    @staticmethod
    def tk_ping(anim, colour, *args, **kwargs):
        """Returns a function that marks a point with an animated ping using the Tcl/Tk backend."""
        return lambda point: anim.ping(point, colour, *args, **kwargs)

    @staticmethod
    def tikz_ping(img, radius, colour, *args, **kwargs):
        """Returns a function that marks a point with a circle using the Tikz backend."""
        return lambda point: img.circle(point, radius, colour, *args, **kwargs)
