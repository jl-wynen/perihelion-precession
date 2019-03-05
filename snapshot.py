from itertools import cycle, chain
import time
from pathlib import Path

import numpy as np

import sim


# image dimensions
SCREEN_WIDTH = 16
SCREEN_HEIGHT = 16
WORLD_WIDTH = 14
WORLD_HEIGHT = 14

# grid-lines
HLINES, VLINES = sim.make_grid((-WORLD_WIDTH/2, -WORLD_HEIGHT/2),
                               (WORLD_WIDTH/2, WORLD_HEIGHT/2),
                               nlines=(14, 14), resolution=(50, 50))

BACKGROUND_COLOUR = "aiphidarkachrom!50!black"
GRID_COLOUR = "white!50!aiphidarkachrom"
TRAJECTORY_COLOUR = "white!40!aiphidarkachrom"
PERIHELION_COLOUR = "white!60!aiphidarkachrom"
MERCURY_COLOUR = "aiphired!60!aiphidarkachrom"
SUN_COLOUR = "aiphiyellow!50!aiphidarkachrom"


def draw_grid(img, lines, centre, rs):
    # maximum radius at which a line is shown
    max_radius = (SCREEN_WIDTH+SCREEN_HEIGHT)/2 / 2.3

    for line in lines:
        line = sim.flamm_projection(line, centre, rs, np.array((WORLD_WIDTH, WORLD_HEIGHT)))
        for start, end in sim.neighbours(line):
            radius = np.linalg.norm((start+end)/2 - centre)
            # fraction of GRID_COLOUR to use for this segment
            frac = 100 - min(radius / max_radius, 1) * 100
            img.line([start, end], draw=f'{GRID_COLOUR}!{frac}!{BACKGROUND_COLOUR}', lw=1)

def draw_trajectory(img, trajectory):
    T = len(trajectory)
    for t, (start, end) in enumerate(sim.neighbours(trajectory)):
        img.line([start, end], draw=f"{TRAJECTORY_COLOUR}!{t/T*100}!darkachrom", lw=4)

def evolve(mercury, nsteps, params):
    trajectory = [mercury.x]

    for _ in range(nsteps):
        mercury = sim.advance(mercury, **params)
        trajectory.append(mercury.x)

    return mercury, np.array(trajectory)

def main():
    img = sim.tikz.Tikz(sim.Transform((-WORLD_WIDTH/2, -WORLD_HEIGHT/2),
                                      (WORLD_WIDTH/2, WORLD_HEIGHT/2),
                                      (0, 0),
                                      (0+SCREEN_WIDTH, 0+SCREEN_HEIGHT)))
                        # background=BACKGROUND_COLOUR)

    mercury = sim.CBody.mercury()
    sun = sim.CBody.sun()

    integrator_params = {"length": 2.0 * np.linalg.norm(mercury.v) / mercury.acc / 2,
                         "nsteps": 10,
                         "alpha": 0.0,
                         "beta": 0.0}

    mercury, trajectory = evolve(mercury, 200, integrator_params)

    draw_grid(img, chain(HLINES, VLINES), np.array((0, 0)), 0)
    draw_trajectory(img, trajectory)
    img.circle(sun.x, 1, fill=SUN_COLOUR)
    img.circle(mercury.x, 0.4, fill=MERCURY_COLOUR)

    radii = np.linalg.norm(trajectory - sun.x, axis=1)
    perihelion_idx = np.argmin(radii)
    img.circle(trajectory[perihelion_idx], 0.2, fill=PERIHELION_COLOUR)
    # img.node(trajectory[perihelion_idx], "circle", fill=PERIHELION_COLOUR, minsize=10,
             # kwoptions={"label": fr"0:\huge\textcolor{{{PERIHELION_COLOUR}}}{{perihelion}}"})

    sim.tikz.render(img, "snapshot.pdf", "snapshot.tex")
    with open("image.tex", "w") as f:
        f.write(str(img))

if __name__ == "__main__":
    main()
