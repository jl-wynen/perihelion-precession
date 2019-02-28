"""
Draw a simple image that can be used as a background.

Shows the Sun, Mercury, a short trajectory and gridlines for some large GR effects.
"""


from itertools import chain

import numpy as np

import sim

# image dimensions
SCREEN_WIDTH = 16
SCREEN_HEIGHT = 16
WORLD_WIDTH = 16
WORLD_HEIGHT = 16

# grid-lines
HLINES, VLINES = sim.make_grid((-WORLD_WIDTH/2, -WORLD_HEIGHT/2),
                               (WORLD_WIDTH/2, WORLD_HEIGHT/2),
                               nlines=(14, 14), resolution=(50, 50))

BACKGROUND_COLOUR = "aiphidarkachrom!50!black"
GRID_COLOUR = "white!50!aiphidarkachrom"
TRAJECTORY_COLOUR = "white!40!aiphidarkachrom"
MERCURY_COLOUR = "aiphired!60!aiphidarkachrom"
SUN_COLOUR = "aiphiyellow!50!aiphidarkachrom"

def draw_grid(img, lines, centre, rs):
    # maxiumum radius at which a line is shown
    max_radius = (SCREEN_WIDTH+SCREEN_HEIGHT)/2 / 3.3

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

def evolve(mercury, nsteps, dt, alpha, beta):
    trajectory = [mercury.x]

    for _ in range(nsteps):
        mercury = sim.advance(mercury, dt, alpha, beta)
        trajectory.append(mercury.x)

    return mercury, trajectory

def main():
    img = sim.tikz.Tikz(sim.Transform((-WORLD_WIDTH/2, -WORLD_HEIGHT/2),
                                      (WORLD_WIDTH/2, WORLD_HEIGHT/2),
                                      (0, 0),
                                      (0+SCREEN_WIDTH, 0+SCREEN_HEIGHT)),
                        clipping_region=[np.array((-WORLD_WIDTH/3, -WORLD_HEIGHT/3)),
                                         np.array((WORLD_WIDTH/3, WORLD_HEIGHT/3))])

    mercury = sim.CBody.mercury()
    sun = sim.CBody.sun()

    dt = 2.0 * np.linalg.norm(mercury.v) / mercury.acc / 2 # Time step
    alpha = 5e6 # Strength of 1/r**3 term
    beta = 0.0 # Strength of 1/r**4 term
    mercury, trajectory = evolve(mercury, 153*3, dt/3, alpha, beta)

    draw_grid(img, chain(HLINES, VLINES), np.array((0, 0)), 0.02)
    draw_trajectory(img, trajectory)
    img.circle(sun.x, 1, fill=SUN_COLOUR)
    img.circle(mercury.x, 0.4, fill=MERCURY_COLOUR)

    sim.tikz.render(img, "background.pdf", "background.tex")


if __name__ == "__main__":
    main()
