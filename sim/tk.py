import tkinter

import numpy as np

from .graphics import hex_colour
from .util import neighbours

def setup_window(width, height, background):
    """Open a new window contianing a canvas."""
    window = tkinter.Tk()
    if background:
        canvas = tkinter.Canvas(window, width=width, height=height, background=background)
    else:
        canvas = tkinter.Canvas(window, width=width, height=height)
    canvas.pack()
    return window, canvas

def mainloop():
    """Run the Tcl/Tk main loop."""
    tkinter.mainloop()


class Tk:
    def __init__(self, transform, background=None):
        self.transform = transform
        self.background = background

        self.window, self.canvas = setup_window(*self.transform.screen_extends(), background)

    def clear(self, objects="all"):
        """Delete given objects from canvas."""
        self.canvas.delete(objects)

    def update(self):
        """Update the display."""
        self.window.update()

    def draw_background(self):
        """Draw fullscreen rectangle with background colour."""
        return self.canvas.create_rectangle(*self.transform.screen_lower,
                                            *self.transform.screen_upper,
                                            fill=hex_colour(self.background),
                                            tags="background")

    def circle(self, pos, radius, fill, draw=None, tags=None):
        """Draw acircle at given position with given radius."""
        if draw is None:
            draw = fill

        return self.canvas.create_oval(*self.transform.world2screen(pos-radius),
                                       *self.transform.world2screen(pos+radius),
                                       fill=hex_colour(fill),
                                       outline=hex_colour(draw),
                                       tags=tags)

    def line(self, points, draw, lw=1, tags=None):
        """Draw a line through all given points."""
        return [self.canvas.create_line(*p0[:2], *p1[:2], fill=hex_colour(draw),
                                        width=lw, tags=tags)
                for p0, p1 in neighbours(map(self.transform.world2screen, points))
                if not np.ma.is_masked(p0) and not np.ma.is_masked(p1)]
