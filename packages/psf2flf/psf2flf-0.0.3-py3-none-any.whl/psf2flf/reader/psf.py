import gzip
import struct
import re
import sys
from pathlib import Path

from ..font import Font
from .reader import Reader


class PSFParseError(Exception):
    pass


_SIZE_PATTERN = re.compile(r"(\d+(?:x\d+)?)$")
_BOLD_PATTERN = re.compile(r"Bold$")


def _parse_psf_filename(filename: str) -> tuple[str, frozenset[str], int | None]:
    """
    Parses a PSF filename to extract font name, style modifiers, and size.

    Returns:
        tuple[str, frozenset[str], int | None]:
            - name: The core font name (e.g., "Terminus", "Fixed").
            - styles: A frozenset of style modifiers (e.g., {"Arabic", "Bold", "14"}).
            - size: The primary height of the font (e.g., 14, 28), or None if not found.
    """
    stem = Path(filename).stem
    if stem.endswith(".psf"):
        stem = Path(stem).stem

    name_parts = stem.split("-")

    name = stem  # Default
    styles = set()
    primary_size: int | None = None

    if len(name_parts) > 1:
        # Assume first part is language/script
        styles.add(name_parts[0])
        remaining_name = "-".join(name_parts[1:])

        # Try to extract size from the end
        size_match = _SIZE_PATTERN.search(remaining_name)
        if size_match:
            size_str = size_match.group(1)
            styles.add(size_str)
            try:
                primary_size = int(size_str.split("x")[0])
            except ValueError:
                pass
            remaining_name = remaining_name[: size_match.start()]

        # Try to extract Bold style
        bold_match = _BOLD_PATTERN.search(remaining_name)
        if bold_match:
            styles.add("Bold")
            remaining_name = remaining_name[: bold_match.start()]

        # The rest is the family name
        name = remaining_name.strip("-")  # Remove any trailing hyphens

    else:
        # No hyphens, use full stem as name, no styles/size
        name = stem

    return name, frozenset(styles), primary_size


class PSFReader(Reader):
    @staticmethod
    def can_open(path: Path) -> bool:
        try:
            with gzip.open(path, "rb") if str(path).endswith(".gz") else open(path, "rb") as f:
                magic = f.read(4)
            return magic[0:2] == b"\x36\x04" or magic[0:4] == b"\x72\xb5\x4a\x86"
        except Exception:
            return False

    def read(self, path: Path) -> Font:
        with gzip.open(path, "rb") if str(path).endswith(".gz") else open(path, "rb") as f:
            self.data = f.read()

        font = Font()
        font.meta["file_name"] = str(path)

        name, styles, primary_size = _parse_psf_filename(path.name)
        font.meta["name"] = name
        font.meta["styles"] = styles
        if primary_size is not None:
            font.meta["primary_size"] = primary_size

        if self.data[0:2] == b"\x36\x04":
            self._parse_psf1(font)
        elif self.data[0:4] == b"\x72\xb5\x4a\x86":
            self._parse_psf2(font)
        else:
            raise PSFParseError("Not a PSF file")

        return font

    def _parse_psf1(self, font: Font):
        font.meta["format"] = "psf1"
        mode = self.data[2]
        height = self.data[3]

        if mode > 0x111:
            raise PSFParseError("Unknown mode")

        glyphs = 512 if mode & 0b001 else 256
        has_unicode_table = bool(mode & 0b010)
        width = 8
        char_size = height
        bytes_per_row = 1

        font.meta["psf1"] = {
            "mode": mode,
            "has_unicode_table": has_unicode_table,
        }
        font.meta["width"] = width
        font.meta["height"] = height
        font.meta["glyphs"] = glyphs
        font.meta["char_size"] = char_size

        raw_glyphs = self._read_glyphs(4, glyphs, height, width, char_size, bytes_per_row)

        unicode_map = {}
        if has_unicode_table:
            unicode_map = self._parse_unicode_table(4 + glyphs * char_size, glyphs, is_psf1=True)
            total_mappings = sum(len(mappings) for mappings in unicode_map.values())
            font.meta["unicode_glyphs"] = len(unicode_map)
            font.meta["unicode_mappings"] = total_mappings

        # Map glyphs to characters
        for i, glyph_data in enumerate(raw_glyphs):
            if i in unicode_map:
                for unicode_val in unicode_map[i]:
                    font.glyphs[chr(unicode_val)] = glyph_data
            else:
                # Fallback for glyphs not in the unicode map
                if i < 256:
                    print(
                        f"Warning: Glyph {i} (0x{i:02X}) has no Unicode mapping in {font.meta['file_name']}, using fallback chr({i})",
                        file=sys.stderr,
                    )
                    font.glyphs[chr(i)] = glyph_data

    def _parse_psf2(self, font: Font):
        font.meta["format"] = "psf2"
        header = struct.unpack("<7I", self.data[4:32])  # Skip magic, read 7 values
        (
            version,
            header_size,
            flags,
            glyphs,
            char_size,
            height,
            width,
        ) = header

        if version != 0:
            raise PSFParseError("Unknown sub-version")
        if header_size != 32:
            raise PSFParseError("Unknown header size")

        bytes_per_row = (width + 7) // 8
        if char_size != height * bytes_per_row:
            raise PSFParseError("Mismatch in char byte size")

        font.meta["psf2"] = {
            "version": version,
            "header_size": header_size,
            "flags": flags,
        }
        font.meta["width"] = width
        font.meta["height"] = height
        font.meta["glyphs"] = glyphs
        font.meta["char_size"] = char_size

        raw_glyphs = self._read_glyphs(header_size, glyphs, height, width, char_size, bytes_per_row)

        unicode_map = {}
        if flags & 1:
            unicode_map = self._parse_unicode_table(header_size + glyphs * char_size, len(raw_glyphs), is_psf1=False)
            total_mappings = sum(len(mappings) for mappings in unicode_map.values())
            font.meta["unicode_glyphs"] = len(unicode_map)
            font.meta["unicode_mappings"] = total_mappings

        # Map glyphs to characters
        for i, glyph_data in enumerate(raw_glyphs):
            if i in unicode_map:
                for unicode_val in unicode_map[i]:
                    font.glyphs[chr(unicode_val)] = glyph_data
            else:
                # Fallback for glyphs not in the unicode map
                if i < 256:
                    print(
                        f"Warning: Glyph {i} (0x{i:02X}) has no Unicode mapping in {font.meta['file_name']}, using fallback chr({i})",
                        file=sys.stderr,
                    )
                    font.glyphs[chr(i)] = glyph_data

    def _read_glyphs(
        self, offset: int, glyph_count: int, height: int, width: int, char_size: int, bytes_per_row: int
    ) -> list[list[list[bool]]]:
        """Read glyphs and return as a list of pixel arrays."""
        data_pos = offset
        all_glyphs = []

        for glyph_idx in range(glyph_count):
            glyph_pixels = []

            for y in range(height):
                row_pixels = []
                x = 0

                for byte_idx in range(bytes_per_row):
                    if data_pos < len(self.data):
                        byte_value = self.data[data_pos]
                        data_pos += 1
                    else:
                        byte_value = 0

                    for bit in range(8):
                        if x < width:
                            pixel_on = bool(byte_value & (1 << (7 - bit)))
                            row_pixels.append(pixel_on)
                            x += 1

                glyph_pixels.append(row_pixels)

            all_glyphs.append(glyph_pixels)
        return all_glyphs

    def _parse_unicode_table(self, offset: int, glyph_count: int, is_psf1: bool = False) -> dict[int, list[int]]:
        """Parse PSF1/PSF2 unicode mapping table and return a dictionary."""

        pos = offset
        unicode_map = {}

        if is_psf1:
            # PSF1: Each glyph's mapping ends with 0xFFFF (16-bit)
            for glyph_idx in range(glyph_count):
                unicode_list = []

                while pos + 1 < len(self.data):
                    # Read 16-bit little-endian value
                    val = self.data[pos] | (self.data[pos + 1] << 8)
                    pos += 2

                    if val == 0xFFFF:  # End of this glyph's mappings
                        break
                    elif val == 0xFFFE:  # Sequence separator
                        # In PSF1, sequences are separated by 0xFFFE
                        continue
                    else:
                        unicode_list.append(val)

                if unicode_list:
                    unicode_map[glyph_idx] = unicode_list

        else:
            # PSF2: UTF-8 encoded, each glyph's mapping ends with 0xFF
            for glyph_idx in range(glyph_count):
                unicode_list = []
                sequence_bytes = []

                while pos < len(self.data):
                    byte = self.data[pos]
                    pos += 1

                    if byte == 0xFF:  # End of this glyph's mappings
                        # Process any remaining bytes
                        if sequence_bytes:
                            try:
                                utf8_str = bytes(sequence_bytes).decode("utf-8")
                                for char in utf8_str:
                                    unicode_list.append(ord(char))
                            except UnicodeDecodeError:
                                pass
                        break
                    elif byte == 0xFE:  # Sequence separator
                        # Process accumulated bytes before separator
                        if sequence_bytes:
                            try:
                                utf8_str = bytes(sequence_bytes).decode("utf-8")
                                for char in utf8_str:
                                    unicode_list.append(ord(char))
                            except UnicodeDecodeError:
                                pass
                            sequence_bytes = []
                    else:
                        sequence_bytes.append(byte)

                if unicode_list:
                    unicode_map[glyph_idx] = unicode_list

        return unicode_map
