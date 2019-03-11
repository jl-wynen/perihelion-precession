from itertools import chain
import time
from pathlib import Path

import numpy as np

import sim

# image dimensions
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
WORLD_WIDTH = 16
WORLD_HEIGHT = 16

# size of output pixel images
OUTPUT_WIDTH = 1024
OUTPUT_HEIGHT = 1024
OUTPUT_SIZE = (OUTPUT_WIDTH, OUTPUT_HEIGHT)

# grid-lines
HLINES, VLINES = sim.make_grid((-WORLD_WIDTH/2-4, -WORLD_HEIGHT/2-4),
                               (WORLD_WIDTH/2+4, WORLD_HEIGHT/2+4),
                               nlines=(20, 20), resolution=(50, 50))

GRID_COLOUR = "#404040"
BACKGROUND_COLOUR = "#161616"
TRAJECTORY_COLOUR = "#606060"
PERIHELION_COLOUR = "#a0a0a0"
MERCURY_COLOUR = "red"
SUN_COLOUR = "yellow"


def draw_grid(anim, lines, centre, rs, colour):
    for line in lines:
        anim.line(sim.flamm_projection(line, centre, rs, np.array((WORLD_WIDTH, WORLD_HEIGHT))),
                  colour, tags="grid")

        # for p0, p1 in sim.neighbours(line):
        #     q0 = sim.radial_transform(p0, centre, rs, 1, 4)
        #     q1 = sim.radial_transform(p1, centre, rs, 1, 4)
        #     anim.line((q0, q1), colour, tags="grid")

def anim_grid(anim, rsiter, frames=None):
    for rs in rsiter:
        start = time.time()

        anim.clear("grid")
        draw_grid(anim, chain(HLINES, VLINES), np.array((0, 0)), rs, GRID_COLOUR)
        anim.canvas.tag_lower("grid", "sun")
        anim.update()

        if frames:
            frames.save_frame(anim.canvas, ps=True, png=True, size=OUTPUT_SIZE)

        end = time.time()
        time_diff = end-start
        time.sleep(max(1/60 - time_diff, 0))


def anim_orbit(anim, mercury, iterator, integrator_params, tracker=None, frames=None):
    mercury_oval = None
    trajectory = [mercury.x]

    for _ in iterator:
        start = time.time()

        mercury = sim.advance(mercury, tracker=tracker, **integrator_params)
        trajectory.append(mercury.x)

        anim.clear(mercury_oval)
        anim.line(trajectory[-2:], TRAJECTORY_COLOUR, lw=2, tags="trajectory")
        mercury_oval = anim.circle(mercury.x, 0.2, fill=MERCURY_COLOUR, tags="mercury")
        anim.update()

        if frames:
            frames.save_frame(anim.canvas, ps=True, png=True, size=OUTPUT_SIZE)

        end = time.time()
        time_diff = end-start
        time.sleep(max(1/60 - time_diff, 0))

    return mercury

def sleep_animation(anim, duration, frames=None):
    nframes = int(duration*60)
    for _ in range(nframes):
        start = time.time()
        anim.update()

        if frames:
            frames.save_frame(anim.canvas, ps=True, png=True, size=OUTPUT_SIZE)

        end = time.time()
        time_diff = end-start
        time.sleep(max(1/60 - time_diff, 0))

def until_perihelion(niterations, anim, reference_point, colour):
    """
    Construct a tracker and an animation iterator to animate until
    niterations perihelions have been found.
    The tracker marks all except for the first perihelion btu cheats and places all
    pings at the same position. This is to hide numerical inaccuracies in
    finding the perihelions.
    """

    nvisited = 0
    pinger = sim.ExtremaTracker.tk_ping(anim, colour)
    skip_perihelion = True  # skip the next perihelion that is found?
    perihelion = None  # previously found perihelion, use this as THE true location

    def _on_perihelion(point):
        nonlocal nvisited, skip_perihelion, perihelion
        nvisited += 1
        if skip_perihelion:
            skip_perihelion = False
        elif perihelion is None:
            perihelion = point
            pinger(perihelion)
        else:
            pinger(perihelion)

    def _iterator():
        count = 0
        while nvisited < niterations:
            yield count

    tracker = sim.ExtremaTracker(reference_point, _on_perihelion)
    return tracker, _iterator()

def write_animation(frames, gif=False, mp4=True):
    if gif:
        print("Creating GIF")
        frames.convert_to_gif("mercury.gif")
        print("Created animation mercury.gif")

    if mp4:
        print("Creating MP4")
        frames.convert_to_mp4("mercury.mp4")
        print("Created animation mercury.mp4")


def main():
    anim = sim.tk.Tk(sim.Transform((-WORLD_WIDTH/2, -WORLD_HEIGHT/2),
                                   (WORLD_WIDTH/2, WORLD_HEIGHT/2),
                                   (0, 0),
                                   (0+SCREEN_WIDTH, 0+SCREEN_HEIGHT)),
                     background=BACKGROUND_COLOUR)

    frames = sim.FrameManager(Path(__file__).resolve().parent/"frames", True)

    mercury = sim.CBody.mercury()
    sun = sim.CBody.sun()

    integrator_params = {"length": 2.0 * np.linalg.norm(mercury.v) / mercury.acc / 2 *2,
                         "nsteps": 20*2,
                         "alpha": 0.0,
                         "beta": 0.0}

    anim.draw_background()
    draw_grid(anim, chain(HLINES, VLINES), np.array((0, 0)), 0, GRID_COLOUR)
    anim.circle(sun.x, 0.8, fill=SUN_COLOUR, tags="sun")

    # newtonian
    tracker, iterator = until_perihelion(4, anim, sun.x, PERIHELION_COLOUR)
    mercury = anim_orbit(anim, mercury, iterator, integrator_params,
                         tracker=tracker, frames=frames)

    # transform grid
    anim.clear("mercury")
    sleep_animation(anim, 0.5, frames)
    anim_grid(anim, np.linspace(0, 0.017, 60), frames=frames)
    sleep_animation(anim, 0.5, frames)

    # switch on GR
    integrator_params["beta"] = 2e6
    tracker = sim.ExtremaTracker(sun.x, sim.ExtremaTracker.tk_ping(anim, PERIHELION_COLOUR))
    mercury = anim_orbit(anim, mercury, range(600), integrator_params,
                         tracker=tracker, frames=frames)

    write_animation(frames)

    sim.tk.mainloop()


if __name__ == "__main__":
    main()
