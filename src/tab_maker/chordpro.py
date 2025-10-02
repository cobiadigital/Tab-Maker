"""Render helpers for emitting Tab-Maker songs as ChordPro text."""
from __future__ import annotations

from typing import List

from .models import (
    BlankLine,
    ChordLyricLine,
    ChordOnlyLine,
    LyricLine,
    Section,
    Song,
    SongLine,
)
from .render_utils import (
    PRIORITY_METADATA_KEYS,
    iter_ordered_metadata,
    merge_chords_with_lyrics,
)


def _render_metadata(song: Song) -> List[str]:
    if not song.metadata:
        return []

    output: List[str] = []
    for key, value in iter_ordered_metadata(song):
        if key in PRIORITY_METADATA_KEYS:
            output.append(f"{{{key}: {value}}}")
        else:
            output.append(f"{{meta:{key} {value}}}")

    return output


def _render_chord_only(line: ChordOnlyLine) -> str:
    return " ".join(f"[{chord}]" for chord in line.chords)


def _render_section(section: Section) -> List[str]:
    output: List[str] = []
    if section.name:
        output.append(f"{{comment: {section.name}}}")

    for entry in section.lines:
        if isinstance(entry, BlankLine):
            output.append("")
        elif isinstance(entry, ChordLyricLine):
            output.append(merge_chords_with_lyrics(entry))
        elif isinstance(entry, LyricLine):
            output.append(entry.text)
        elif isinstance(entry, ChordOnlyLine):
            output.append(_render_chord_only(entry))
        else:
            raise TypeError(f"Unhandled song line type: {type(entry)!r}")

    return output


def song_to_chordpro(song: Song) -> str:
    lines: List[str] = []
    lines.extend(_render_metadata(song))

    for idx, section in enumerate(song.sections):
        section_lines = _render_section(section)
        if idx > 0 and section_lines and (lines and lines[-1] != ""):
            lines.append("")
        lines.extend(section_lines)

    text = "\n".join(lines)
    if not text.endswith("\n"):
        text += "\n"
    return text


__all__ = ["song_to_chordpro"]
