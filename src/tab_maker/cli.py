"""Command line interface for converting chord sheets to ChordPro."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, Optional

from .chordpro import song_to_chordpro
from .parser import parse_song


def _read_input(path: Optional[str]) -> str:
    if path:
        return Path(path).read_text(encoding="utf-8")
    return sys.stdin.read()


def _apply_metadata(args: argparse.Namespace, song_metadata: dict[str, str]) -> None:
    if args.title:
        song_metadata["title"] = args.title
    if args.artist:
        song_metadata["artist"] = args.artist
    if args.album:
        song_metadata["album"] = args.album
    if args.key:
        song_metadata["key"] = args.key
    if args.meta:
        for item in args.meta:
            if "=" not in item:
                raise ValueError(f"Metadata values must use key=value format: {item!r}")
            key, value = item.split("=", 1)
            key = key.strip()
            value = value.strip()
            if not key:
                raise ValueError("Metadata key may not be empty")
            song_metadata[key] = value


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert an Ultimate Guitar style chord sheet into ChordPro format.",
    )
    parser.add_argument(
        "source",
        nargs="?",
        help="Path to the input chord sheet. Reads from stdin when omitted.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Path to write the ChordPro output. Defaults to stdout.",
    )
    parser.add_argument("--title", help="Song title metadata", default=None)
    parser.add_argument("--artist", help="Song artist metadata", default=None)
    parser.add_argument("--album", help="Song album metadata", default=None)
    parser.add_argument("--key", help="Song key metadata", default=None)
    parser.add_argument(
        "--meta",
        action="append",
        help="Additional metadata entries in key=value format (may repeat)",
    )
    return parser


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        raw_input = _read_input(args.source)
        song = parse_song(raw_input)
        _apply_metadata(args, song.metadata)
        output_text = song_to_chordpro(song)
    except Exception as exc:  # pragma: no cover - best effort CLI guard
        parser.error(str(exc))
        return 2

    if args.output:
        Path(args.output).write_text(output_text, encoding="utf-8")
    else:
        sys.stdout.write(output_text)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
