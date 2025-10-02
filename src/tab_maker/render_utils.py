"""Shared rendering helpers for Tab-Maker outputs."""
from __future__ import annotations

from typing import Dict, Iterator, List, Tuple

from .models import ChordLyricLine, Song

PRIORITY_METADATA_KEYS: Tuple[str, ...] = (
    "title",
    "subtitle",
    "artist",
    "album",
    "composer",
    "year",
    "key",
    "tempo",
    "capo",
)


def iter_ordered_metadata(song: Song) -> Iterator[Tuple[str, str]]:
    """Yield metadata entries with preferred keys first."""
    seen: Dict[str, str] = {}
    for key in PRIORITY_METADATA_KEYS:
        if key in song.metadata:
            yield key, song.metadata[key]
            seen[key] = song.metadata[key]
    for key, value in song.metadata.items():
        if key in seen:
            continue
        yield key, value


def merge_chords_with_lyrics(line: ChordLyricLine) -> str:
    """Inline chord placements within a lyric string."""
    lyrics = line.lyrics
    result: List[str] = []
    last_index = 0

    for placement in sorted(line.placements, key=lambda item: item.column):
        index = max(placement.column, 0)
        slice_end = min(index, len(lyrics))
        if slice_end > last_index:
            result.append(lyrics[last_index:slice_end])
            last_index = slice_end
        if index > len(lyrics):
            padding = index - len(lyrics)
            if padding:
                result.append(" " * padding)
        result.append(f"[{placement.chord}]")

    result.append(lyrics[last_index:])
    return "".join(result)


__all__ = [
    "PRIORITY_METADATA_KEYS",
    "iter_ordered_metadata",
    "merge_chords_with_lyrics",
]
