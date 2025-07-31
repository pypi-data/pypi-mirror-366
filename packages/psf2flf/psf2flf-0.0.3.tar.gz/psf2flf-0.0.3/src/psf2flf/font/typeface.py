from dataclasses import dataclass, field

from .font import Font


@dataclass
class TypeFace:
    """Represents a collection of related fonts (e.g., by family, style, and size)."""

    name: str
    family: str = field(init=False)
    styles: dict[frozenset[str], dict[int, Font]] = field(default_factory=dict)

    def __post_init__(self):
        self.family = self.name
