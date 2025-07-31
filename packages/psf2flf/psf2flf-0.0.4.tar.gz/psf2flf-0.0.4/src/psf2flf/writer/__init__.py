from pathlib import Path

from ..font import Font
from .flf import FLFWriter
from .writer import Writer


_writers: list[Writer] = [
    FLFWriter(),
]


def write(font: Font, path: Path, tall_mode: bool = False):
    """Writes a font to the given path using the appropriate writer."""
    for writer in _writers:
        if writer.can_write(path):
            writer.write(font, path, tall_mode)
            return
    raise ValueError(f"No writer found for file: {path}")
