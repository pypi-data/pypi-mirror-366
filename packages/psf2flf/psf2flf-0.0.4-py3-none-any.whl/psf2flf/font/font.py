from dataclasses import dataclass, field


@dataclass
class Font:
    """A generic representation of a font."""

    meta: dict = field(default_factory=dict)
    glyphs: dict = field(default_factory=dict)

    @property
    def name(self) -> str:
        """Get the font name from metadata."""
        return self.meta.get("name", "")

    @property
    def style(self) -> frozenset[str]:
        """Get the font style from metadata."""
        return self.meta.get("styles", frozenset())

    @property
    def width(self) -> int:
        """Get the font width from metadata."""
        return self.meta.get("width", 0)

    @property
    def height(self) -> int:
        """Get the font height from metadata."""
        return self.meta.get("height", 0)

    def __eq__(self, other) -> bool:
        """Two fonts are equal if name, style, width, height match and overlapping ASCII glyphs are identical."""
        if not isinstance(other, Font):
            return False

        # Check basic properties
        if (
            self.name != other.name
            or self.style != other.style
            or self.width != other.width
            or self.height != other.height
        ):
            return False

        # Get ASCII printable characters that exist in both fonts
        ascii_chars = set(chr(i) for i in range(32, 128))
        self_chars = set(self.glyphs.keys())
        other_chars = set(other.glyphs.keys())
        common_ascii = ascii_chars & self_chars & other_chars

        # Check that common ASCII glyphs are identical
        for char in common_ascii:
            if self.glyphs[char] != other.glyphs[char]:
                return False

        return True

    def __iadd__(self, other):
        """Merge another font into this one if they are compatible."""
        if not isinstance(other, Font):
            raise TypeError(f"Cannot add {type(other).__name__} to Font")

        # Check compatibility using existing __eq__ logic
        if (
            self.name != other.name
            or self.style != other.style
            or self.width != other.width
            or self.height != other.height
        ):
            raise ValueError(
                f"Cannot merge incompatible fonts: "
                f"{self.name} {self.style} {self.width}x{self.height} != "
                f"{other.name} {other.style} {other.width}x{other.height}"
            )

        # Only add glyphs that don't exist in current font (fill gaps only)
        added_count = 0
        for char, glyph in other.glyphs.items():
            if char not in self.glyphs:
                self.glyphs[char] = glyph
                added_count += 1

        # Merge metadata (keep existing, but add missing charset info)
        if "charset" not in self.meta and "charset" in other.meta:
            self.meta["charset"] = other.meta["charset"]
        elif "charset" in self.meta and "charset" in other.meta:
            # If both have charset and they differ, combine them
            if self.meta["charset"] != other.meta["charset"]:
                charsets = {self.meta["charset"], other.meta["charset"]}
                self.meta["charset"] = "+".join(sorted(charsets))

        return self

    def force_merge(self, other):
        """Force merge another font, ignoring compatibility checks."""
        if not isinstance(other, Font):
            raise TypeError(f"Cannot add {type(other).__name__} to Font")

        # Only add glyphs that don't exist in current font (fill gaps only)
        added_count = 0
        for char, glyph in other.glyphs.items():
            if char not in self.glyphs:
                self.glyphs[char] = glyph
                added_count += 1

        # Merge metadata (keep existing, but add missing charset info)
        if "charset" not in self.meta and "charset" in other.meta:
            self.meta["charset"] = other.meta["charset"]
        elif "charset" in self.meta and "charset" in other.meta:
            # If both have charset and they differ, combine them
            if self.meta["charset"] != other.meta["charset"]:
                charsets = {self.meta["charset"], other.meta["charset"]}
                self.meta["charset"] = "+".join(sorted(charsets))

        return self
