"""Utilities to render chords on a separate line above lyrics."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from .models import BlankLine, ChordLyricLine, ChordOnlyLine, LyricLine, Song


@dataclass(slots=True)
class RenderSegment:
    """Represents a line of text annotated with its semantic type."""
    kind: str  # one of: metadata, section, chord, lyric, blank, other
    text: str


def _build_chord_line(placements: Iterable, lyric_length: int) -> str:
    max_width = lyric_length
    for placement in placements:
        max_width = max(max_width, placement.column + len(placement.chord))
    if max_width == 0:
        return ""

    chars = [" "] * max_width
    for placement in placements:
        start = placement.column
        chord = placement.chord
        end = start + len(chord)
        if end > len(chars):
            chars.extend(" " for _ in range(end - len(chars)))
        for idx, character in enumerate(chord):
            chars[start + idx] = character
    return "".join(chars).rstrip()


def chord_line_with_lyrics(line: ChordLyricLine) -> List[RenderSegment]:
    chord_line = _build_chord_line(line.placements, len(line.lyrics))
    segments: List[RenderSegment] = []
    if chord_line:
        segments.append(RenderSegment(kind="chord", text=chord_line))
    segments.append(RenderSegment(kind="lyric", text=line.lyrics.rstrip()))
    return segments


def song_to_two_line_segments(song: Song) -> List[RenderSegment]:
    """Return annotated segments placing chords above lyrics."""
    segments: List[RenderSegment] = []

    if "title" in song.metadata:
        segments.append(RenderSegment(kind="metadata", text=f"Title: {song.metadata['title']}"))
    if "artist" in song.metadata:
        segments.append(RenderSegment(kind="metadata", text=f"Artist: {song.metadata['artist']}"))
    for key, value in song.metadata.items():
        if key in {"title", "artist"}:
            continue
        segments.append(RenderSegment(kind="metadata", text=f"{key.title()}: {value}"))

    if segments:
        segments.append(RenderSegment(kind="blank", text=""))

    for idx, section in enumerate(song.sections):
        if section.name:
            segments.append(RenderSegment(kind="section", text=section.name))
        for entry in section.lines:
            if isinstance(entry, BlankLine):
                segments.append(RenderSegment(kind="blank", text=""))
            elif isinstance(entry, ChordLyricLine):
                segments.extend(chord_line_with_lyrics(entry))
            elif isinstance(entry, LyricLine):
                segments.append(RenderSegment(kind="lyric", text=entry.text.rstrip()))
            elif isinstance(entry, ChordOnlyLine):
                segments.append(RenderSegment(kind="chord", text=entry.raw_text.rstrip()))
            else:
                segments.append(RenderSegment(kind="other", text=str(entry)))
        if idx != len(song.sections) - 1:
            segments.append(RenderSegment(kind="blank", text=""))

    return segments


def song_to_two_line_plain_text(song: Song) -> List[str]:
    """Return a simple list of strings using the two-line chord layout."""
    return [segment.text for segment in song_to_two_line_segments(song)]


__all__ = [
    "RenderSegment",
    "song_to_two_line_segments",
    "song_to_two_line_plain_text",
    "chord_line_with_lyrics",
]
