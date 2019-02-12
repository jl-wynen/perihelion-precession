from tkinter import Tk, Canvas, mainloop
from itertools import cycle, chain
import subprocess
from pathlib import Path
import shutil

import numpy as np

from geometry import make_grid, flamm_projection
from util import neighbours

# image dimensions
WIDTH = 600
HEIGHT = 600

CENTRE = np.array((WIDTH/2, HEIGHT/2))

BACKGROUND = "#2c2c2c"

# grid-lines
HLINES, VLINES = make_grid((-200, -200), (WIDTH+200, HEIGHT+200),
                           nlines=(10, 10), resolution=(50, 50))

def init_directory(path, overwrite):
    if path.exists():
        if not overwrite:
            raise RuntimeError(f"Path {path} already exists, not allowed to overwrite.")
        shutil.rmtree(path)
    path.mkdir()


class FrameManager:
    """
    Write and convert animation frames.
    """

    def __init__(self, path, overwrite):
        self.path = Path(path)
        self._fname_fmt = "{:04d}.eps"
        self._current = 0

        init_directory(path, overwrite)

    def save_frame(self, canvas, ps=True, png=False, resolution=None):
        """Save a single frame as postscript or PNG or both."""

        psname = self.path/self._fname_fmt.format(self._current)
        # save ps image in any case
        canvas.postscript(file=psname, colormode="color")

        if png:
            # convert to png
            if resolution is None:
                raise ValueError("Need a resoltuion when saving PNGs")
            self.convert_frame(self._current, resolution)

        if not ps:
            # remove ps written before
            psname.unlink()

        self._current += 1

    def convert_frame(self, number, resolution):
        """Convert ps of a frame to PNG."""

        if number is None:
            number = self._current
        fname = self.path/self._fname_fmt.format(number)

        subprocess.run(["gs", "-dSAFER", "-dBATCH", "-dNOPAUSE", "-sDEVICE=png16m",
                        f"-r{resolution}", f"-sOutputFile={fname.with_suffix('.png')}", f"{fname}"],
                       check=True, capture_output=True)

    def convert_to_gif(self, fname):
        """
        Make a GIF out of all saved frames.
        Requires frames to be saved as PNG.
        """
        subprocess.run(["convert", *sorted(filter(lambda x: x.suffix == ".png",
                                                  self.path.iterdir()),
                                           key=lambda x: int(x.stem)),
                        fname],
                       check=True, capture_output=True)


def setup_window(width, height, background):
    """Open a new window contianing a canvas."""
    window = Tk()
    canvas = Canvas(window, width=width, height=height, background=background)
    canvas.pack()
    return window, canvas

def draw_line(canvas, line, centre, rs, colour):
    for p0, p1 in neighbours(flamm_projection(line, centre, rs, np.array((0, 0)))):
        if not np.ma.is_masked(p0) and not np.ma.is_masked(p1):
            canvas.create_line(*p0[:2], *p1[:2], fill=colour)

def draw_grid(canvas, centre, rs, colour):
    for line in chain(HLINES, VLINES):
        draw_line(canvas, line, centre, rs, colour)

def main():
    # frames = FrameManager(Path(__file__).resolve().parent/"frames", True)

    window, canvas = setup_window(WIDTH, HEIGHT, BACKGROUND)

    rss = np.linspace(0, 100, 100)
    for i, rs in enumerate(cycle(chain(rss, reversed(rss)))):

        canvas.delete("all")
        canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill=BACKGROUND)

        canvas.create_oval(CENTRE[0]-rs, CENTRE[1]-rs, CENTRE[0]+rs, CENTRE[1]+rs, fill="black")
        draw_grid(canvas, CENTRE, rs, "gray")
        window.update()

        # frames.save_frame(canvas, png=True, resolution=150)
        # if i == 50:
            # break

    # print("Creating GIF")
    # frames.convert_to_gif("mercury.gif")
    # print("Created animation mercury.gif")

    mainloop()


if __name__ == "__main__":
    main()
