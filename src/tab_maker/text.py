"""Plain text rendering utilities for Tab-Maker."""
from __future__ import annotations

from typing import List

from .models import BlankLine, ChordLyricLine, ChordOnlyLine, LyricLine, Song, SongLine
from .render_utils import iter_ordered_metadata, merge_chords_with_lyrics


def _format_metadata_line(key: str, value: str) -> str:
    readable_key = key.replace("_", " ").title()
    return f"{readable_key}: {value}"


def _render_line(entry: SongLine) -> str:
    if isinstance(entry, BlankLine):
        return ""
    if isinstance(entry, ChordLyricLine):
        return merge_chords_with_lyrics(entry)
    if isinstance(entry, LyricLine):
        return entry.text
    if isinstance(entry, ChordOnlyLine):
        return entry.raw_text if entry.raw_text else " ".join(entry.chords)
    raise TypeError(f"Unhandled song line type: {type(entry)!r}")


def song_to_plain_lines(song: Song) -> List[str]:
    """Return a list of plain-text lines representing the song."""
    lines: List[str] = []

    metadata_lines = [
        _format_metadata_line(key, value) for key, value in iter_ordered_metadata(song)
    ]
    if metadata_lines:
        lines.extend(metadata_lines)
        lines.append("")

    for index, section in enumerate(song.sections):
        if section.name:
            lines.append(section.name)
        for entry in section.lines:
            rendered = _render_line(entry)
            lines.append(rendered)
        if index != len(song.sections) - 1:
            lines.append("")

    return lines


__all__ = ["song_to_plain_lines"]
