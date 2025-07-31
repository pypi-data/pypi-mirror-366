from dataclasses import dataclass, field
from pathlib import Path
import tarfile
from typing import Union

from .font import Font
from .typeface import TypeFace


@dataclass
class FontDir:
    """A collection of typefaces, typically representing a font directory or archive."""

    typefaces: dict[str, TypeFace] = field(default_factory=dict)

    def __iadd__(self, other: Union[Font, TypeFace]):
        """Add a font or typeface to this directory."""
        if isinstance(other, Font):
            return self._add_font(other)
        elif isinstance(other, TypeFace):
            return self._add_typeface(other)
        else:
            raise TypeError(f"Cannot add {type(other).__name__} to FontDir")

    def _add_font(self, font: Font):
        """Add a font to the appropriate typeface."""
        family_name = font.name

        if family_name not in self.typefaces:
            # Create new typeface for this family
            self.typefaces[family_name] = TypeFace(name=family_name)

        # Add font to the typeface
        self.typefaces[family_name] += font
        return self

    def _add_typeface(self, typeface: TypeFace):
        """Add an entire typeface to this directory."""
        family_name = typeface.name

        if family_name not in self.typefaces:
            # Simply add the new typeface
            self.typefaces[family_name] = typeface
        else:
            # Merge with existing typeface by adding all fonts
            existing_typeface = self.typefaces[family_name]
            for style_group in typeface.styles.values():
                for font in style_group.values():
                    existing_typeface += font

        return self

    def write_directory(self, output_dir: Path, tall_mode: bool = False):
        """Write all typefaces to a directory structure."""
        from ..writer import write  # Import here to avoid circular imports

        output_dir.mkdir(parents=True, exist_ok=True)

        for family_name, typeface in self.typefaces.items():
            for style_group in typeface.styles.values():
                for size, font in style_group.items():
                    # Generate filename: FamilyStyleHxW.flf with correct output dimensions
                    style_parts = list(font.style) if font.style else []
                    # Filter out size information from styles (already have dimensions)
                    style_parts = [s for s in style_parts if not any(char.isdigit() for char in s)]

                    # Calculate actual output dimensions
                    if tall_mode:
                        # Tall mode: 1:1 pixel mapping (narrow chars since pixels are square)
                        output_height = font.height
                        output_width = font.width
                        if "Narrow" not in style_parts:
                            style_parts.append("Narrow")
                    else:
                        # Default mode: 2:1 compression
                        output_height = (font.height + 1) // 2  # Round up for odd heights
                        output_width = font.width

                    style_suffix = "".join(style_parts) if style_parts else ""
                    dimensions = f"{output_height}x{output_width}"

                    filename = f"{family_name}{style_suffix}{dimensions}.flf"

                    output_path = output_dir / filename
                    write(font, output_path, tall_mode)
                    print(f"Written: {output_path}")

    def write_tar(self, output_path: Path, tall_mode: bool = False):
        """Write all typefaces to a tar archive."""
        from ..writer import write  # Import here to avoid circular imports
        import tempfile

        with tarfile.open(output_path, "w:gz") as tar:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                for family_name, typeface in self.typefaces.items():
                    for style_group in typeface.styles.values():
                        for size, font in style_group.items():
                            # Generate filename: FamilyStyleHxW.flf with correct output dimensions
                            style_parts = list(font.style) if font.style else []
                            # Filter out size information from styles (already have dimensions)
                            style_parts = [s for s in style_parts if not any(char.isdigit() for char in s)]

                            # Calculate actual output dimensions
                            if tall_mode:
                                # Tall mode: 1:1 pixel mapping (narrow chars since pixels are square)
                                output_height = font.height
                                output_width = font.width
                                if "Narrow" not in style_parts:
                                    style_parts.append("Narrow")
                            else:
                                # Default mode: 2:1 compression
                                output_height = (font.height + 1) // 2  # Round up for odd heights
                                output_width = font.width

                            style_suffix = "".join(style_parts) if style_parts else ""
                            dimensions = f"{output_height}x{output_width}"

                            filename = f"{family_name}{style_suffix}{dimensions}.flf"

                            temp_file = temp_path / filename
                            write(font, temp_file, tall_mode)

                            # Add to tar archive
                            tar.add(temp_file, arcname=filename)

        print(f"Created archive: {output_path}")
