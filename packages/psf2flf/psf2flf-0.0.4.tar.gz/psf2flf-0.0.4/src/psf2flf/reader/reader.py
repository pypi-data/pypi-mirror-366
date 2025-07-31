from abc import ABC, abstractmethod
from pathlib import Path

from ..font import Font


class Reader(ABC):
    """Base class for font readers."""

    @staticmethod
    @abstractmethod
    def can_open(path: Path) -> bool:
        """Returns True if the reader can open the given file path."""
        pass

    @abstractmethod
    def read(self, path: Path) -> Font:
        """Reads the font from the given path and returns a Font object."""
        pass
