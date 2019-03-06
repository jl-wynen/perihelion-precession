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
                               nlines=(16, 16), resolution=(50, 50))

BACKGROUND_COLOUR = "aiphidarkachrom!50!black"
GRID_COLOUR = "white!50!aiphidarkachrom"
TRAJECTORY_COLOUR = "white!40!aiphidarkachrom"
PERIHELION_COLOUR = "white!80!aiphidarkachrom"
MERCURY_COLOUR = "aiphired!60!aiphidarkachrom"
SUN_COLOUR = "aiphiyellow!80!aiphidarkachrom"

# Define shading to make the sun glow.
# This must be included in the preamble of any TeX document
# using images created with this script!
EXTRA_PREAMBLE = r"""\pgfdeclareradialshading{glow}{\pgfpoint{0cm}{0cm}}{
  color(0mm)=(white);
  color(1.7mm)=(white);
  color(2mm)=(white!50!black);
  color(2.4mm)=(white!20!transparent);
  color(2.7mm)=(transparent)
}

\begin{tikzfadingfrompicture}[name=glow fading]
  \shade[shading=glow] (0,0) circle (1.3);
\end{tikzfadingfrompicture}
"""

def draw_grid(img, lines, centre, rs):
    # maximum radius at which a line is shown
    max_radius = (SCREEN_WIDTH+SCREEN_HEIGHT)/2 / 3

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
        img.line([start, end], draw=f"{TRAJECTORY_COLOUR}!{t/T*100}!darkachrom", lw=2)

def scale_to(x, from_max, to_min, to_max):
    """Scale a value from range [0, from_max] to range [to_min, to_max]."""
    return x / from_max * (to_max - to_min) + to_min

def draw_perihelions(img, perihelions):
    nper = len(perihelions)
    for i, perihelion in enumerate(perihelions):
        if nper == 1:
            col = 100
        else:
            col = scale_to(i, nper-1, 50, 100)
        colour = f"{PERIHELION_COLOUR}!{col}!aiphidarkachrom"
        img.circle(perihelion, 0.2, fill=colour)

def evolve(mercury, nsteps, params, tracker):
    trajectory = [mercury.x]

    for _ in range(nsteps):
        mercury = sim.advance(mercury, **params, tracker=tracker)
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

    perihelions = []
    tracker = sim.ExtremaTracker(sun.x, on_periapsis=perihelions.append)

    integrator_params = {"length": 2.0 * np.linalg.norm(mercury.v) / mercury.acc / 2,
                         "nsteps": 10,
                         "alpha": 0,
                         "beta": 2e6}

    mercury, trajectory = evolve(mercury, 1000, integrator_params, tracker)

    draw_grid(img, chain(HLINES, VLINES), np.array((0, 0)), 0.017)
    draw_trajectory(img, trajectory)
    draw_perihelions(img, perihelions)
    img.cmd(rf"\fill[{SUN_COLOUR},path fading=glow fading] {sim.tikz.fmt_point(sun.x)} circle (3);")
    img.circle(mercury.x, 0.4, fill=MERCURY_COLOUR)

    sim.tikz.render(img, "snapshot.pdf", "snapshot.tex", extra_preamble=EXTRA_PREAMBLE)
    with open("image.tex", "w") as f:
        f.write(str(img))

if __name__ == "__main__":
    main()
