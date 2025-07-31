from abc import ABC, abstractmethod
from pathlib import Path

from ..font import Font


class Writer(ABC):
    """Base class for font writers."""

    @staticmethod
    @abstractmethod
    def can_write(path: Path) -> bool:
        """Returns True if the writer can write to the given file path."""
        pass

    @abstractmethod
    def write(self, font: Font, path: Path):
        """Writes the font to the given path."""
        pass
