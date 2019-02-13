import subprocess
from pathlib import Path
import shutil

def init_directory(path, overwrite):
    """Create directory, remove it if it exists and overwrite==True."""
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
        # TODO use x=0, y=0, width=600, height=600 to print only visible area (removes artefacts at the borders)
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

        # TODO
# subprocess.run(['gs', '-sDEVICE=png16m', '-sOutputFile=%04d.png',
#                 '-g50x50', '-dBATCH', '-dNOPAUSE', *psfiles],
#                cwd='frames')

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
