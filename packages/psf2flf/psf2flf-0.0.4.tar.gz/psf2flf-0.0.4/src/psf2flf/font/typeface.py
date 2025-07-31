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

    def __iadd__(self, font: Font):
        """Add a font to this typeface."""
        if not isinstance(font, Font):
            raise TypeError(f"Cannot add {type(font).__name__} to TypeFace")

        # Check if this font belongs to this typeface family
        if font.name != self.name:
            raise ValueError(f"Cannot add font '{font.name}' to typeface '{self.name}': " f"family name mismatch")

        # Get or create style group
        style_key = font.style
        if style_key not in self.styles:
            self.styles[style_key] = {}

        size_group = self.styles[style_key]
        font_size = font.height  # Use height as the size key

        if font_size in size_group:
            # Merge with existing font of same size
            size_group[font_size] += font
        else:
            # Add as new size variant
            size_group[font_size] = font

        return self
