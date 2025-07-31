from pathlib import Path

from .psf import PSFReader
from .reader import Reader


_readers: list[Reader] = [
    PSFReader(),
]


def read(path: Path):
    """Reads a font from the given path using the appropriate reader."""
    for reader in _readers:
        if reader.can_open(path):
            return reader.read(path)
    raise ValueError(f"No reader found for file: {path}")
