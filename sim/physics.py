import dataclasses

import numpy as np

from .geometry import pol2cart


# Schwarzschild radius of Sun, in units of R0
RS = 2.95e-7
# Specific angular momentum, in units of R0**2
RL2 = 8.19e-7


@dataclasses.dataclass
class CBody:
    x: np.ndarray
    v: np.ndarray

    acc: float

    @classmethod
    def mercury(cls, phi=0):
        # Values computed using https://nssdc.gsfc.nasa.gov/planetary/factsheet
        RM0 = 4.60    # Initial radius of Mercury orbit, in units of R0
        VM0 = 5.10e-1 # Initial orbital speed of Mercury, in units of R0/T0
        AM = 9.90e-1  # Base acceleration of Mercury, in units of R0**3/T0**2

        return cls(pol2cart((RM0, phi)),
                   pol2cart((VM0, phi+np.pi/2)),
                   AM)

    @classmethod
    def sun(cls):
        return cls(np.array((0, 0)),
                   np.array((0, 0)),
                   0)


def acceleration(body, alpha, beta):
    r = np.linalg.norm(body.x)
    # compute the factor coming from General Relativity
    grfact = 1 + alpha * RS / r + beta * RL2 / r**2
    # compute the acceleration
    return -body.acc * grfact / r**2 * body.x / r

def advance(body, dt, alpha, beta):
    v = body.v + acceleration(body, alpha, beta)*dt
    x = body.x + v*dt
    return dataclasses.replace(body, x=x, v=v)
