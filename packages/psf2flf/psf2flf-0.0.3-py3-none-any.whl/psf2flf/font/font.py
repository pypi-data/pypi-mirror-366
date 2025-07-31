from dataclasses import dataclass, field


@dataclass
class Font:
    """A generic representation of a font."""

    meta: dict = field(default_factory=dict)
    glyphs: dict = field(default_factory=dict)
