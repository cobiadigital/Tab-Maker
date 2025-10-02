"""CLI for converting ChordPro (.cho) files into two-line RTF output."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, Optional

from .chord_layout import song_to_two_line_segments
from .chordpro_parser import parse_chordpro
from .rtf import segments_to_rtf


def _read_input(path: Optional[str]) -> str:
    if path:
        return Path(path).read_text(encoding="utf-8")
    return sys.stdin.read()


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert a ChordPro (.cho) file into RTF with chords above the lyrics.",
    )
    parser.add_argument(
        "source",
        nargs="?",
        help="Path to the input .cho file. Reads from stdin if omitted.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Path to write the generated RTF. Defaults to stdout.",
    )
    return parser


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        raw_text = _read_input(args.source)
        song = parse_chordpro(raw_text)
        segments = song_to_two_line_segments(song)
        rtf_text = segments_to_rtf(segments)
    except Exception as exc:  # pragma: no cover - CLI guard
        parser.error(str(exc))
        return 2

    if args.output:
        Path(args.output).write_text(rtf_text, encoding="utf-8")
    else:
        sys.stdout.write(rtf_text)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
