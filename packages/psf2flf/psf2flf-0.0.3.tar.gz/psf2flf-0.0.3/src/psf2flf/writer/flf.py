from pathlib import Path

from ..font import Font
from .writer import Writer


class FLFWriter(Writer):
    @staticmethod
    def can_write(path: Path) -> bool:
        return path.suffix == ".flf"

    def write(self, font: Font, output_path: Path, tall_mode: bool = False):
        height = font.meta["height"]
        width = font.meta["width"]
        fig_height, max_length, _ = self._calculate_flf_dimensions(width, height, tall_mode)

        hardblank = "$"
        layout = 0

        # Get the default glyph for fallback
        default_glyph_data = font.glyphs.get("?")

        # Prepare ASCII glyphs (32-126)
        ascii_glyphs = []
        for i in range(32, 127):
            char = chr(i)
            glyph = font.glyphs.get(char, default_glyph_data)
            if glyph is None:
                # Create a blank glyph if no default and no specific glyph
                glyph = [[False for _ in range(width)] for _ in range(height)]
            ascii_glyphs.append(glyph)

        # Collect extended glyphs (outside 32-126)
        extended_glyphs = {}
        for char, glyph_data in font.glyphs.items():
            cp = ord(char)
            if not (32 <= cp <= 126):
                extended_glyphs[cp] = glyph_data

        # Sort extended glyphs by codepoint
        sorted_extended_codepoints = sorted(extended_glyphs.keys())

        # Total number of characters to write
        total_chars_to_write = len(ascii_glyphs) + len(sorted_extended_codepoints)

        with output_path.open("w", encoding="utf-8") as f:
            # Write FLF header with the correct number of characters
            f.write(
                f"flf2a{hardblank} {fig_height} {fig_height - 1} {max_length} 0 {layout} 0 0 {total_chars_to_write}\n"
            )

            # Write ASCII glyphs (32-126) - no 0x prefix
            for glyph_data in ascii_glyphs:
                rendered = self._render_block_glyph(glyph_data, width, height, tall_mode)
                for i, line in enumerate(rendered):
                    padded_line = line.replace(" ", hardblank).ljust(max_length, hardblank)
                    terminator = "@" if i < len(rendered) - 1 else "@@"
                    f.write(padded_line + terminator + "\n")

            # Write extended glyphs - with 0x prefix
            for cp in sorted_extended_codepoints:
                glyph_data = extended_glyphs[cp]
                rendered = self._render_block_glyph(glyph_data, width, height, tall_mode)

                f.write(f"0x{cp:X}\n")  # Write character code line

                for i, line in enumerate(rendered):
                    padded_line = line.replace(" ", hardblank).ljust(max_length, hardblank)
                    terminator = "@" if i < len(rendered) - 1 else "@@"
                    f.write(padded_line + terminator + "\n")

    def _calculate_flf_dimensions(self, font_width: int, font_height: int, tall_mode: bool):
        if tall_mode:
            fig_height = font_height
            max_length = font_width
            display_width = font_width
        else:
            fig_height = (font_height + 1) // 2
            max_length = font_width
            display_width = font_width

        return fig_height, max_length, display_width

    def _render_block_glyph(self, pixel_array: list[list[bool]], width: int, height: int, tall_mode: bool) -> list[str]:
        if tall_mode:
            return self._render_full_pixels(pixel_array, width, height)
        else:
            return self._render_short_blocks(pixel_array, width, height)

    def _render_short_blocks(self, pixel_array: list[list[bool]], width: int, height: int) -> list[str]:
        lines = []
        for y in range(0, height, 2):
            line = ""
            for x in range(width):
                top_pixel = pixel_array[y][x] if y < height and x < width else False
                bottom_pixel = pixel_array[y + 1][x] if y + 1 < height and x < width else False

                if top_pixel and bottom_pixel:
                    line += "█"
                elif top_pixel:
                    line += "▀"
                elif bottom_pixel:
                    line += "▄"
                else:
                    line += " "
            lines.append(line)
        return lines

    def _render_full_pixels(self, pixel_array: list[list[bool]], width: int, height: int) -> list[str]:
        lines = []
        for y in range(height):
            line = ""
            for x in range(width):
                if pixel_array[y][x]:
                    line += "█"
                else:
                    line += " "
            lines.append(line)
        return lines
