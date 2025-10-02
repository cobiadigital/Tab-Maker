"""Parsing utilities for converting Ultimate Guitar style chord sheets."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Optional

from .models import (
    BlankLine,
    ChordLyricLine,
    ChordOnlyLine,
    ChordPlacement,
    LyricLine,
    Section,
    Song,
    SongLine,
)

_SECTION_HEADER = re.compile(r"^\[(?P<name>[^\]]+)\]\s*$")
_NOISE_TOKENS = {"|", "||", "|:", ":|", "||:", "::"}


@dataclass(slots=True)
class _PendingChordLine:
    placements: List[ChordPlacement]
    raw_text: str


def _is_chord_token(token: str) -> bool:
    token = token.strip()
    if not token:
        return False
    if token.upper() == "N.C.":
        return True
    if token in _NOISE_TOKENS:
        return True
    if token[0] not in "ABCDEFG":
        return False

    idx = 1
    length = len(token)

    if idx < length and token[idx] in "#b":
        idx += 1

    keywords = ("mMaj", "sus", "maj", "min", "dim", "aug", "add", "maj", "m")

    while idx < length:
        ch = token[idx]
        if ch.isdigit():
            while idx < length and token[idx].isdigit():
                idx += 1
            continue
        if ch in "+-#b":
            idx += 1
            continue
        if ch == "/":
            idx += 1
            if idx >= length or token[idx] not in "ABCDEFG":
                return False
            idx += 1
            if idx < length and token[idx] in "#b":
                idx += 1
            continue
        if ch == "(":
            idx += 1
            while idx < length and token[idx] != ")":
                idx += 1
            if idx >= length:
                return False
            idx += 1
            continue

        matched_keyword = False
        for keyword in keywords:
            if token.startswith(keyword, idx):
                idx += len(keyword)
                matched_keyword = True
                break
        if matched_keyword:
            continue
        return False

    return True


def _extract_chords(line: str) -> Optional[List[ChordPlacement]]:
    placements: List[ChordPlacement] = []
    for match in re.finditer(r"\S+", line):
        token = match.group()
        if token in _NOISE_TOKENS:
            continue
        if not _is_chord_token(token):
            return None
        placements.append(ChordPlacement(chord=token, column=match.start()))
    return placements if placements else None


def _flush_pending(
    pending: Optional[_PendingChordLine],
    output: List[SongLine],
) -> None:
    if pending is None:
        return
    output.append(
        ChordOnlyLine(
            chords=[placement.chord for placement in pending.placements],
            raw_text=pending.raw_text,
        )
    )
    pending.placements.clear()


def parse_song(text: str) -> Song:
    sections: List[Section] = []
    current_section = Section(name=None)
    pending: Optional[_PendingChordLine] = None

    def start_new_section(section_name: str) -> None:
        nonlocal current_section, pending
        if pending is not None:
            _flush_pending(pending, current_section.lines)
            pending = None
        if current_section.lines or current_section.name is not None:
            sections.append(current_section)
        current_section = Section(name=section_name)

    for raw_line in text.splitlines():
        line = raw_line.rstrip("\r")
        header_match = _SECTION_HEADER.match(line.strip())
        if header_match:
            start_new_section(header_match.group("name"))
            continue

        if not line.strip():
            if pending is not None:
                _flush_pending(pending, current_section.lines)
                pending = None
            current_section.lines.append(BlankLine())
            continue

        chord_positions = _extract_chords(line)
        if chord_positions is not None:
            if pending is not None:
                _flush_pending(pending, current_section.lines)
            pending = _PendingChordLine(placements=chord_positions, raw_text=line)
            continue

        if pending is not None:
            current_section.lines.append(
                ChordLyricLine(lyrics=line, placements=pending.placements)
            )
            pending = None
        else:
            current_section.lines.append(LyricLine(text=line))

    if pending is not None:
        _flush_pending(pending, current_section.lines)

    if current_section.lines or current_section.name is not None:
        sections.append(current_section)

    return Song(sections=sections)


__all__ = ["parse_song"]
