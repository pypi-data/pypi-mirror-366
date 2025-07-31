import argparse
import sys
from pathlib import Path

from .reader import read
from .writer import write
from .utils import print_dict


def show_info(source: Path):
    font = read(source)
    print(f"Font: {source}")
    print_dict(font.meta)
    print(f"codepoints: {len(font.glyphs)}")


def convert_single(source: Path, dest: Path, tall_mode: bool = False):
    font = read(source)

    if dest.suffix != ".flf":
        dest = dest.with_suffix(".flf")

    dest.parent.mkdir(parents=True, exist_ok=True)

    write(font, dest, tall_mode)
    print(f"{source}\t{dest}")


def convert_all(source_dir: Path, dest_dir: Path, tall_mode: bool = False):
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
    parser = argparse.ArgumentParser(description="Convert PSF fonts to FLF (FIGlet) format.")
    parser.add_argument("source", nargs="?", help="PSF font file or input directory")
    parser.add_argument("dest", nargs="?", help="Output file (single) or directory (--all)")
    parser.add_argument("--all", action="store_true", help="Convert all PSF fonts in a directory")
    parser.add_argument("--info", action="store_true", help="Show font information instead of converting")
    parser.add_argument(
        "--tall", action="store_true", help="Use full-size 1:1 pixel mapping instead of default 2x1 compression"
    )
    args = parser.parse_args(argv)

    if args.info:
        if not args.source:
            parser.error("You must provide a source PSF file when using --info.")
        show_info(Path(args.source))
    elif args.all:
        if not args.source or not args.dest:
            parser.error("You must provide source and dest directories when using --all.")
        convert_all(Path(args.source), Path(args.dest), tall_mode=args.tall)
    else:
        if not args.source or not args.dest:
            parser.error("You must provide a source PSF file and dest file.")
        convert_single(Path(args.source), Path(args.dest), tall_mode=args.tall)

    return 0


def main():
    return cli(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
