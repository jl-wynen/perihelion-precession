from tkinter import Tk, Canvas, mainloop
from itertools import cycle, chain
import time

import numpy as np

import sim

# image dimensions
WIDTH = 600
HEIGHT = 600

CENTRE = np.array((WIDTH/2, HEIGHT/2))

BACKGROUND = "#2c2c2c"

# grid-lines
HLINES, VLINES = sim.make_grid((-200, -200), (WIDTH+200, HEIGHT+200),
                               nlines=(20, 20), resolution=(50, 50))


def setup_window(width, height, background):
    """Open a new window contianing a canvas."""
    window = Tk()
    canvas = Canvas(window, width=width, height=height, background=background)
    canvas.pack()
    return window, canvas

def draw_line(canvas, line, colour):
    for p0, p1 in sim.neighbours(line):
        if not np.ma.is_masked(p0) and not np.ma.is_masked(p1):
            canvas.create_line(*p0[:2], *p1[:2], fill=colour)

def draw_grid(canvas, centre, rs, colour):
    for line in chain(HLINES, VLINES):
        draw_line(canvas, sim.flamm_projection(line, centre, rs, np.array((0, 0))), colour)

def sim2screen(point, sim_bounds, screen_size):
    return point*screen_size/2/sim_bounds + screen_size/2

def main():
    # frames = FrameManager(Path(__file__).resolve().parent/"frames", True)

    window, canvas = setup_window(WIDTH, HEIGHT, BACKGROUND)

    mercury = sim.CBody.mercury()
    sun = sim.CBody.sun()

    dt = 2.0 * np.linalg.norm(mercury.v) / mercury.acc / 2 # Time step
    alpha = 5e6 # Strength of 1/r**3 term
    beta = 0.0 # Strength of 1/r**4 term

    sim_bounds = np.array((5, 5))
    screen_size = np.array((WIDTH, HEIGHT))

    mercury_oval = None

    sx = sim2screen(sun.x, sim_bounds, screen_size)

    canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill=BACKGROUND)
    draw_grid(canvas, CENTRE, 20, "#404040")
    canvas.create_oval(sx[0]-20, sx[1]-20,
                       sx[0]+20, sx[1]+20,
                       fill="yellow")
    
    trajectory = [sim2screen(mercury.x, sim_bounds, screen_size)]
    while True:
        mercury = sim.advance(mercury, dt, alpha, beta)
        trajectory.append(sim2screen(mercury.x, sim_bounds, screen_size))

        # canvas.delete("all")
        if mercury_oval is not None:
            canvas.delete(mercury_oval)


        mx = sim2screen(mercury.x, sim_bounds, screen_size)

        draw_line(canvas, trajectory[-2:], "gray")

        mercury_oval = canvas.create_oval(mx[0]-10, mx[1]-10,
                                          mx[0]+10, mx[1]+10,
                                          fill="red")

        window.update()

        time.sleep(1/60)
        
        # frames.save_frame(canvas, png=True, resolution=150)
        # if i == 50:
            # break

    # print("Creating GIF")
    # frames.convert_to_gif("mercury.gif")
    # print("Created animation mercury.gif")

    mainloop()

# animate grid    
# def main():
#     # frames = FrameManager(Path(__file__).resolve().parent/"frames", True)

#     window, canvas = setup_window(WIDTH, HEIGHT, BACKGROUND)

#     rss = np.linspace(0, 100, 100)
#     for i, rs in enumerate(cycle(chain(rss, reversed(rss)))):

#         canvas.delete("all")
#         canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill=BACKGROUND)

#         canvas.create_oval(CENTRE[0]-rs, CENTRE[1]-rs, CENTRE[0]+rs, CENTRE[1]+rs, fill="black")
#         draw_grid(canvas, CENTRE, rs, "gray")
#         window.update()

#         # frames.save_frame(canvas, png=True, resolution=150)
#         # if i == 50:
#             # break

#     # print("Creating GIF")
#     # frames.convert_to_gif("mercury.gif")
#     # print("Created animation mercury.gif")

#     mainloop()


if __name__ == "__main__":
    main()
