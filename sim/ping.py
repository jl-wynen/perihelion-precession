"""
Class Ping to mark a location.
"""

from .util import interpolate

class Ping:
    """
    Mark a location.

    Displays a ring around some position and changes the radius of the
    ring for every frame until a final radius is reached.
    Then, switches to a filled circle with the target radius.

    Call Ping.draw() to initially draw and update the ping.
    """

    def __init__(self, position, colour, radius_final, radius_initial, nframes):
        """
        Arguments:
            position: (numpy array) 2D position of the ping (centre).
            colour: Colour string.
            radius_final: Radius of the circle after the animation.
            radius_initial: Radius of the ring at the beginning of the animation.
            nframes: Number of frames it takes to got from radius_initial to radius_final.
        """

        self.position = position
        self.colour = colour

        # animation finished?
        self._finished = False
        # iteratator (animating) or float (finished)
        self._radius = interpolate(radius_initial, radius_final, nframes)
        # ID of the circle or ring
        self._gid = None

    def draw(self, anim, keep_finished=True):
        """
        Draw the ping into backend anim.
        Every time this function is called, the previous ring/circle is
        removed and replaced by one with modified radius.
        Call this function exactly once per frame!
        """

        if self._finished and keep_finished and self._gid is not None:
            # finished circle is already drawn
            return

        anim.clear(self._gid)

        # get the radius first to set self._finished properly
        radius = self._get_radius()
        if self._finished:
            fill = self.colour
            draw = None
        else:
            fill = None
            draw = self.colour

        self._gid = anim.circle(self.position, radius, fill, draw)

    def clear(self, anim):
        """Remove the ring/circle from display."""
        anim.clear(self._gid)

    def gid(self):
        """Return the ID of the ring/circle, can be None if nothing has been drawn yet."""
        return self._gid

    def _get_radius(self):
        """Return the next radius of the ring/circle, advances the radius iterator."""

        if self._finished:
            # self._radius is a float now
            return self._radius

        try:
            # get next radius
            return next(self._radius)
        except StopIteration as stop:
            # set internal state to 'finished'
            self._radius = stop.value
            self._finished = True
            return self._radius
