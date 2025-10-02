"""Parse ChordPro (.cho) files into Tab-Maker song structures."""
from __future__ import annotations

import re
from typing import List, Optional

from .models import (
    BlankLine,
    ChordLyricLine,
    ChordPlacement,
    LyricLine,
    Section,
    Song,
)

_DIRECTIVE_RE = re.compile(r"^\{([^:]+):\s*(.*?)\s*\}$")
_SECTION_DIRECTIVES = {"comment", "comment_italic", "comment_box"}
_METADATA_DIRECTIVES = {
    "title",
    "subtitle",
    "artist",
    "album",
    "composer",
    "year",
    "key",
    "tempo",
    "capo",
}


def _parse_chordpro_text_line(line: str) -> ChordLyricLine | LyricLine:
    placements: List[ChordPlacement] = []
    lyric_chars: List[str] = []
    idx = 0
    column = 0
    length = len(line)

    while idx < length:
        char = line[idx]
        if char == "[":
            closing = line.find("]", idx + 1)
            if closing == -1:  # treat unmatched '[' as literal
                lyric_chars.append(char)
                column += 1
                idx += 1
                continue
            chord = line[idx + 1 : closing].strip()
            if chord:
                placements.append(ChordPlacement(chord=chord, column=column))
            idx = closing + 1
            continue
        lyric_chars.append(char)
        column += 1
        idx += 1

    lyrics = "".join(lyric_chars)
    if placements:
        return ChordLyricLine(lyrics=lyrics, placements=placements)
    return LyricLine(text=lyrics)


def parse_chordpro(text: str) -> Song:
    sections: List[Section] = []
    current_section = Section(name=None)
    metadata: dict[str, str] = {}

    def start_new_section(name: str) -> None:
        nonlocal current_section
        if current_section.lines or current_section.name is not None:
            sections.append(current_section)
        current_section = Section(name=name)

    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        directive_match = _DIRECTIVE_RE.match(stripped)
        if directive_match:
            key = directive_match.group(1).strip().lower()
            value = directive_match.group(2)
            if key in _SECTION_DIRECTIVES:
                start_new_section(value)
                continue
            if key in _METADATA_DIRECTIVES:
                metadata[key] = value
                continue
            # Unknown directive treated as plain lyric text without braces
            stripped = value
        if not stripped and raw_line == "":
            current_section.lines.append(BlankLine())
            continue
        if not raw_line.strip():  # whitespace-only line
            current_section.lines.append(BlankLine())
            continue

        parsed_line = _parse_chordpro_text_line(raw_line)
        current_section.lines.append(parsed_line)

    if current_section.lines or current_section.name is not None:
        sections.append(current_section)

    return Song(sections=sections, metadata=metadata)


__all__ = ["parse_chordpro"]
