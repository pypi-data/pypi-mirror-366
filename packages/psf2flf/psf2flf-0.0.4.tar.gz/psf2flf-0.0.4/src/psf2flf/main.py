import argparse
import sys
from pathlib import Path

from .font import FontDir
from .reader import read
from .writer import write
from .utils import print_dict


def show_info(source: Path):
    """Show information about a single font file."""
    font = read(source)
    print(f"Font: {source}")
    print_dict(font.meta)
    print(f"codepoints: {len(font.glyphs)}")


def is_directory_output(path: Path) -> bool:
    """Check if the output path indicates a directory."""
    path_str = str(path)

    # Explicit directory indicator (trailing slash) or tar file
    if path_str.endswith("/") or path.suffix == ".tar":
        return True

    # If no extension and not explicitly .flf, assume directory
    if not path.suffix:
        return True

    # If it's an existing directory
    if path.exists() and path.is_dir():
        return True

    return False


def convert_multiple(inputs: list[Path], output: Path, tall_mode: bool = False, force: bool = False):
    """Convert multiple input files to single output (font or directory)."""
    if is_directory_output(output):
        # Output is a directory or tar file - use FontDir
        container = FontDir()

        # Add all input fonts to the directory
        for input_path in inputs:
            try:
                if not input_path.exists():
                    print(f"ERROR: File not found: {input_path}", file=sys.stderr)
                    continue

                font = read(input_path)
                container += font
                print(f"Added: {input_path}")
            except Exception as e:
                print(f"ERROR reading {input_path}: {e}", file=sys.stderr)

        # Write the directory
        if output.suffix == ".tar":
            container.write_tar(output, tall_mode)
        else:
            # Ensure output path ends with / for directory
            if not str(output).endswith("/"):
                output = Path(str(output) + "/")
            container.write_directory(output, tall_mode)

    else:
        # Output is a single .flf file - merge into single Font
        if output.suffix != ".flf":
            output = output.with_suffix(".flf")

        merged_font = None

        for input_path in inputs:
            try:
                if not input_path.exists():
                    print(f"ERROR: File not found: {input_path}", file=sys.stderr)
                    return 1

                font = read(input_path)
                if merged_font is None:
                    merged_font = font
                    print(f"Base font: {input_path}")
                else:
                    if force:
                        merged_font.force_merge(font)
                        print(f"Force merged: {input_path}")
                    else:
                        merged_font += font
                        print(f"Merged: {input_path}")
            except Exception as e:
                print(f"ERROR processing {input_path}: {e}", file=sys.stderr)
                return 1

        if merged_font is not None:
            try:
                output.parent.mkdir(parents=True, exist_ok=True)
                write(merged_font, output, tall_mode)
                print(f"Output: {output}")
            except Exception as e:
                print(f"ERROR writing output {output}: {e}", file=sys.stderr)
                return 1
        else:
            print("ERROR: No fonts were successfully loaded", file=sys.stderr)
            return 1

    return 0


def convert_all_in_directory(source_dir: Path, dest_dir: Path, tall_mode: bool = False):
    """Convert all PSF fonts in a directory (legacy --all mode)."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    psf_files = list(source_dir.glob("*.psf")) + list(source_dir.glob("*.psf.gz"))

    for path in psf_files:
        try:
            font = read(path)
            name = path.stem.replace(".psf", "").replace(".gz", "")
            out_path = dest_dir / f"{name}.flf"
            write(font, out_path, tall_mode)
            print(f"{path}\t{out_path}")
        except Exception as e:
            print(f"{path}\tERROR: {e}")


def cli(argv):
    parser = argparse.ArgumentParser(
        description="Convert PSF fonts to FLF (FIGlet) format.",
        epilog="""
Examples:
  psf2flf font.psf output.flf                    # Convert single font
  psf2flf font1.psf font2.psf merged.flf         # Merge fonts into single output
  psf2flf font1.psf font2.psf output/            # Create directory of fonts
  psf2flf font1.psf font2.psf fonts.tar          # Create tar archive
  psf2flf --all input_dir/ output_dir/           # Convert all fonts in directory
  psf2flf --info font.psf                        # Show font information
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("files", nargs="*", help="Input PSF files and output destination. Last argument is output.")
    parser.add_argument(
        "--all", action="store_true", help="Convert all PSF fonts in input directory to output directory"
    )
    parser.add_argument("--info", action="store_true", help="Show font information instead of converting")
    parser.add_argument(
        "--tall", action="store_true", help="Use full-size 1:1 pixel mapping instead of default 2x1 compression"
    )
    parser.add_argument("--force", action="store_true", help="Force merge incompatible fonts by ignoring conflicts")

    args = parser.parse_args(argv)

    if args.info:
        if len(args.files) != 1:
            parser.error("--info requires exactly one input file.")
        show_info(Path(args.files[0]))
        return 0

    elif args.all:
        if len(args.files) != 2:
            parser.error("--all requires exactly two arguments: input_dir output_dir.")
        convert_all_in_directory(Path(args.files[0]), Path(args.files[1]), args.tall)
        return 0

    else:
        # New multi-input mode
        if len(args.files) < 2:
            parser.error("You must provide at least one input file and one output destination.")

        inputs = [Path(f) for f in args.files[:-1]]
        output = Path(args.files[-1])

        return convert_multiple(inputs, output, args.tall, args.force)


def main():
    return cli(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
