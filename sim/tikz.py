"""
Wrapper around LaTeX Tikz image generation package.
"""

import subprocess
from tempfile import TemporaryDirectory
from pathlib import Path
import shutil

from .graphics import COLOURS, norm_colour

def define_colours(colours):
    """Return list of colour definition commands for all given colours (based on graphics.COLOURS)."""
    return [rf"\definecolor{{{colour}}}{{HTML}}{{{COLOURS[colour].hex[1:]}}}"
            for colour in colours]

def fmt_point(point):
    """Format a 2D point."""
    assert len(point) == 2
    return f"({point[0]},{point[1]})"

def fmt_option_val(option):
    """Format a single option (just a value , no key)."""
    if option is None:
        return ""
    return str(option)

def fmt_option_key(key, value):
    """Format a single keyword option."""
    if value is None:
        return ""
    return f"{key}={value}"

def fmt_options(options, kwoptions, *args, **kwargs):
    """
    Format comma separated list of options.

    Arguments:
        options: list of options. (Can be None.)
        kwoptions: dict of keyword options. (Can be None.)
        args: Is appended to options.
        kwargs: Is incorporated into kwoptions.
    """

    # make sure options is a list and incorporate args
    if options is None:
        options = []
    options.extend(args)
    # make sure kwoptions is a dict and incorporate kwargs
    if kwoptions is None:
        kwoptions = {}
    kwoptions.update(kwargs)

    not_empty = lambda x: x  # filter out empty options
    return ",".join(filter(not_empty,
                           (",".join(filter(not_empty,
                                            map(fmt_option_val,
                                                options))),
                            ",".join(filter(not_empty,
                                            map(lambda arg: fmt_option_key(*arg),
                                                kwoptions.items()))))))

def wrap(string, left="[", right="]"):
    """Wrap a string in two delimiters iff the string is non empty (or None)."""
    if string:
        return left+string+right
    return ""

# TODO use transform and make all methods take coordinates in world space
class Tikz:
    """
    Represents a single Tikz picture.
    Provides methods for constructing and writing the picture.
    """


    def __init__(self, transform, background=None, defines=None, options=None,
                 kwoptions=None, global_colours=None):
        """
        Construct a new Tikz picture.

        Arguments:
            transform: graphics.Transform that encodes world and screen coordinates.
            background: Colour (string) of the background, None for transparent background.
                        This colour must be defined in the TeX document outside of the figure.
            defines: list of custom commands to place before any other commands in the picture.
            options: list of options to pass to the pikzpicture environment.
            kwoptions: dict of keyword options to pass to the tikzpicture environment.
            global_colours: set of globally defined colours.
                            Those colours are not redefined in the picture.
        """

        self.transform = transform
        self.background = background
        self.defines = defines if defines else []
        self.options = options if options else []
        self.kwoptions = kwoptions if kwoptions else {}
        self.global_colours = global_colours if global_colours else set()

        self._commands = []
        self._used_colours = set()

    def __str__(self):
        """Write a tikzpicture environment with all stored commands."""

        # can't use backslash in f-string
        newline = "\n"

        options = self.options
        kwoptions = self.kwoptions

        # add background to options
        if self.background:
            options.append("show background rectangle")
            kwoptions.update({"background rectangle/.style": f"{{fill={self.background}}}"})

        return rf"""\begin{{tikzpicture}}{wrap(fmt_options(self.options, self.kwoptions))}
{newline.join(define_colours(self._used_colours))}
{newline.join(self.defines)}
{newline.join(self._commands)}
\end{{tikzpicture}}"""

    def use_colour(self, colour):
        """
        Declare that a colour is used in the figure.

        Arguments:
            colour: Name string of a single colour or LaTeX shading expression,
                    i.e. col1!50!col2.
        """

        if colour is None:
            return

        def _not_convertible_to_float(item):
            try:
                float(item)
            except ValueError:
                return True
            return False

        # look at all components and ignore numbers
        for col in filter(_not_convertible_to_float, colour.split("!")):
            if col in COLOURS.keys() and not col in self.global_colours:
                self._used_colours.add(col)
            # else: assume it is known in LaTeX (hex value)

    def cmd(self, command):
        """Add an arbitrary command."""
        self._commands.append(command)

    def line(self, points, ls="--", draw="black", lw=None, options=None, kwoptions=None):
        r"""
        Add a line between two points.

        Arguments:
            points: Iterable of points to draw through.
            ls: Line style (string).
            draw: Colour of the line (string).
            lw: Line width.
            options: list of extra options to pass to \draw.
            kwoptions: dict of extra keyword options to pass to \draw.
        """

        draw = norm_colour(draw)
        self.use_colour(draw)

        if kwoptions is None:
            kwoptions = {}
        kwopts = {'draw': draw, **kwoptions}
        if lw:
            kwopts['line width'] = lw

        self._commands.append(rf"\draw{wrap(fmt_options(options,kwopts))} " +
                              f" {ls} ".join(map(fmt_point, points))+";")

    def node(self, pos, shape=None, draw=None, fill="black", text="", lw=0.2,
             sep=0, minsize=3, options=None, kwoptions=None):
        r"""
        Draw a node at a given point.

        Arguments:
            pos: Position of the node (two element collection)
            shape: Shape of the node, passed as first option to \node.
            draw: Colour of outline (string).
            fill: Colour of node interior (string).
            text: String to show on the node.
            lw: Width of the node's border.
            sep: Separation of node border and text.
            minsize: Minimum size of the node.
            options: list of extra options to pass to \draw.
            kwoptions: dict of extra keyword options to pass to \draw.
        """

        draw = norm_colour(draw)
        self.use_colour(draw)
        fill = norm_colour(fill)
        self.use_colour(fill)

        self._commands.append(rf"\node[{shape+',' if shape else ''}"
                              rf"line width={lw},inner sep={sep},minimum size={minsize},"
                              rf"{fmt_options(options,kwoptions,draw=draw,fill=fill)}] "
                              rf"at {fmt_point(pos)} {{{text}}};")

    def circle(self, pos, radius, draw=None, fill="black", lw=0, options=None, kwoptions=None):
        """
        Draw a circle at given position.
        """

        fill = norm_colour(fill)
        self.use_colour(fill)

        draw = norm_colour(draw)
        if draw is None:
            draw = fill
        self.use_colour(draw)

        self._commands.append(rf"\filldraw[line width={lw},"
                              rf"{fmt_options(options, kwoptions, draw=draw, fill=fill)}] "
                              rf" {fmt_point(pos)} circle ({radius});")

    def rectangle(self, pos, *args, **kwargs):
        """
        Draw a rectangle at given position.
        Calls Tikz.node with shape='rectangle', args, and kwargs.
        """
        self.node(pos, "rectangle", *args, **kwargs)

def write(image, fname):
    """Write a standalone TeX file containing only the given Tikz image."""
    with open(fname, "w") as texf:
        # can't use backslash in f-string
        newline = "\n"

        texf.write(rf"""\documentclass{{standalone}}
\usepackage{{tikz}}
\usetikzlibrary{{backgrounds}}
{newline.join(define_colours(COLOURS.keys()))}
\begin{{document}}
{image}
\end{{document}}
""")

def render(image, out_fname="img.pdf", source_fname=None):
    """
    Render a Tikz image to PDF by using pdflatex.
    Write and compile TeX in a temporary directory and store only the output file
    and potentially the source file.

    Arguments:
        image: Tikz object containing the drawing commands.
        out_fname: Name/path of the output file.
        source_fname: If not None, save the source under this name/path.
    """
    with TemporaryDirectory() as workdir:
        workdir = Path(workdir)
        write(image, workdir/"img.tex")

        try:
            subprocess.run(["pdflatex", "-halt-on-error", "-interaction=nonstopmode", "img.tex"],
                           capture_output=True, check=True, cwd=workdir)
        except subprocess.CalledProcessError as exc:
            print(exc.output.decode("utf-8"))
            raise

        if source_fname:
            shutil.copy(workdir/"img.tex", source_fname)
        shutil.copy(workdir/"img.pdf", out_fname)
