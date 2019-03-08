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

    def save_frame(self, canvas, ps=True, png=False, size=None):
        """Save a single frame as postscript or PNG or both."""

        psname = self.path/self._fname_fmt.format(self._current)
        # save ps image in any case
        # crop image to remove borders
        canvas.postscript(file=psname, colormode="color",
                          x=1, width=canvas.winfo_reqwidth()-2,
                          y=1, height=canvas.winfo_reqheight()-2)

        if png:
            # convert to png
            if size is None:
                raise ValueError("Need a size when saving PNGs")
            self.convert_frame(self._current, size)

        if not ps:
            # remove ps written before
            psname.unlink()

        self._current += 1

    def convert_frame(self, number, size):
        """Convert ps of a frame to PNG."""

        if number is None:
            number = self._current
        fname = self.path/self._fname_fmt.format(number)

        subprocess.run(["gs", "-dSAFER", "-dBATCH", "-dNOPAUSE", "-sDEVICE=png16m",
                        f"-g{size[0]}x{size[1]}", "-dEPSFitPage",
                        f"-sOutputFile={fname.with_suffix('.png')}", f"{fname}"],
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

    def convert_to_mp4(self, fname, fps=60):
        """
        Make an MP4 out of all saved frames.
        Requires frames to be saved as PNG.
        """
        subprocess.run(["ffmpeg",
                        "-y",
                        "-xerror",
                        "-framerate", f"{fps}",
                        "-i", f"{self.path}/%04d.png",
                        "-c:v", "libx264",
                        "-profile:v", "high",
                        "-crf", "20", "-pix_fmt",
                        "yuv420p",
                        fname],
                       check=True, capture_output=True)
