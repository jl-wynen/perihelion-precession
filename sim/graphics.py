import numpy as np
from colour import Color as Colour

## All custom colours, mapping names to Colour objects.
COLOURS = {
    "aiphiblue": Colour(red=0, green=84/255, blue=159/255),
    "aiphibordeaux": Colour(red=161/255, green=16/255, blue=53/255),
    "aiphidark": Colour(red=45/255, green=38/255, blue=50/255),
    "aiphidarkachrom": Colour(red=44/255, green=44/255, blue=44/255),
    "aiphigreen": Colour(red=87/255, green=171/255, blue=39/255),
    "aiphipetrol": Colour(red=0, green=97/255, blue=101/255),
    "aiphired": Colour(red=204/255, green=7/255, blue=30/255),
    "aiphiviolet": Colour(red=97/255, green=33/255, blue=88/255),
    "aiphiyellow": Colour(red=1, green=237/255, blue=0)
}

## Other names for custom colours defined in COLOURS.
COLOUR_ALIASES = {name[5:]: name for name in COLOURS.keys()}


def norm_colour(colour):
    """Resolve colour aliases."""
    if colour is None:
        return colour
    return "!".join((COLOUR_ALIASES[elem] if elem in COLOUR_ALIASES else elem
                     for elem in colour.split("!")))

def hex_colour(colour):
    """Return hex value of a colour if it is known (in COLOURS) or an instance of Colour."""
    if isinstance(colour, Colour):
        return colour.hex_l
    try:
        return COLOURS[norm_colour(colour)].hex_l
    except KeyError:
        return colour

class Transform:
    """
    Handle transformations from world to screen space.
    """

    def __init__(self, world_lower, world_upper, screen_lower, screen_upper, screen_z=0):
        """
        Arguments are bottom left and top right coordinates of world and screen space
        as well as z coordinate (depth) of the screen.
        """

        self.world_lower = np.array(world_lower)
        self.world_upper = np.array(world_upper)

        self.screen_lower = np.array(screen_lower)
        self.screen_upper = np.array(screen_upper)
        self.screen_z = screen_z

        # factor and summand for transformation world -> screen
        self._w2s_scale = self.screen_extends() / self.world_extends()
        self._w2s_shift = self.screen_lower - self.world_lower * self._w2s_scale

    def world_width(self):
        return self.world_upper[0] - self.world_lower[0]

    def world_height(self):
        return self.world_upper[1] - self.world_lower[1]

    def world_extends(self):
        return np.array((self.world_width(), self.world_height()))

    def screen_width(self):
        return self.screen_upper[0] - self.screen_lower[0]

    def screen_height(self):
        return self.screen_upper[1] - self.screen_lower[1]

    def screen_extends(self):
        return np.array((self.screen_width(), self.screen_height()))

    def world2screen(self, point):
        return point * self._w2s_scale + self._w2s_shift
