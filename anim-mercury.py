from itertools import cycle, chain
import time
from pathlib import Path

import numpy as np

import sim

# image dimensions
WIDTH = 600
HEIGHT = 600

# resolution of output bitmaps
OUTPUT_RESOLUTION = 150

# grid-lines
HLINES, VLINES = sim.make_grid((-10, -10), (10, 10),
                               nlines=(20, 20), resolution=(50, 50))


def draw_grid(anim, lines, centre, rs, colour):
    for line in lines:
        anim.line(sim.flamm_projection(line, centre, rs, np.array((-10, -10))), colour, tags="grid")
        # anim.line(line, colour, tags="grid")

        # for p0, p1 in sim.neighbours(line):
        #     q0 = sim.radial_transform(p0, centre, rs, 1, 4)
        #     q1 = sim.radial_transform(p1, centre, rs, 1, 4)
        #     draw_line(canvas, (q0, q1), colour, "grid")

def anim_orbit(anim, mercury, nframes, dt, alpha, beta, frames=None):
    mercury_oval = None
    trajectory = [mercury.x]

    for _ in range(nframes):
        start = time.time()

        mercury = sim.advance(mercury, dt, alpha, beta)
        trajectory.append(mercury.x)

        anim.clear(mercury_oval)
        anim.line(trajectory[-2:], "#606060", lw=2, tags="trajectory")
        mercury_oval = anim.circle(mercury.x, 0.1, fill="red", tags="mercury")
        anim.update()

        if frames:
            frames.save_frame(anim.canvas, ps=True, png=True, resolution=OUTPUT_RESOLUTION)

        end = time.time()
        time_diff = end-start
        time.sleep(max(1/60 - time_diff, 0))

    return mercury

def main():
    anim = sim.tk.Tk(sim.Transform((-5, -5), (5, 5), (0, 0), (0+WIDTH, 0+HEIGHT)),
                     background="#161616")

    # frames = sim.FrameManager(Path(__file__).resolve().parent/"frames", True)

    mercury = sim.CBody.mercury()
    sun = sim.CBody.sun()

    dt = 2.0 * np.linalg.norm(mercury.v) / mercury.acc / 2 # Time step
    alpha = 5e6 # Strength of 1/r**3 term
    beta = 0.0 # Strength of 1/r**4 term

    anim.draw_background()
    draw_grid(anim, chain(HLINES, VLINES), np.array((0, 0)), 0.01, "#404040")
    anim.circle(sun.x, 0.5, fill="yellow")

    mercury = anim_orbit(anim, mercury, 100000, dt, alpha, beta)

    # print("Creating GIF")
    # frames.convert_to_gif("mercury.gif")
    # print("Created animation mercury.gif")

    sim.tk.mainloop()


if __name__ == "__main__":
    main()
