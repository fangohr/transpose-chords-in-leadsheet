from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .transposer import ChordParseError, transpose_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="transpose-chords",
        description="Transpose whitespace-delimited chord symbols in a text file.",
    )
    parser.add_argument("inputfile", type=Path)
    parser.add_argument("semitones", type=int, help="Semitone shift, e.g. +3 or -2")
    parser.add_argument("outputfile", type=Path, nargs="?")
    parser.add_argument(
        "--prefer-flats",
        action="store_true",
        help="Render output notes using flat names instead of sharp names.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        text = args.inputfile.read_text(encoding="utf-8")
        transposed = transpose_text(
            text,
            semitones=args.semitones,
            prefer_flats=args.prefer_flats,
        )
        if args.outputfile is None:
            print(transposed, end="")
        else:
            args.outputfile.write_text(transposed, encoding="utf-8")
    except ChordParseError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
