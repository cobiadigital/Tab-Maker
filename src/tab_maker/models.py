"""Core data structures for Tab-Maker song parsing and conversion."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union


@dataclass(slots=True)
class ChordPlacement:
    """Represents a chord positioned at a specific character column."""
    chord: str
    column: int


@dataclass(slots=True)
class BlankLine:
    pass


@dataclass(slots=True)
class LyricLine:
    text: str


@dataclass(slots=True)
class ChordOnlyLine:
    chords: List[str]
    raw_text: str


@dataclass(slots=True)
class ChordLyricLine:
    lyrics: str
    placements: List[ChordPlacement]


SongLine = Union[BlankLine, LyricLine, ChordOnlyLine, ChordLyricLine]


@dataclass(slots=True)
class Section:
    name: Optional[str]
    lines: List[SongLine] = field(default_factory=list)


@dataclass(slots=True)
class Song:
    sections: List[Section]
    metadata: Dict[str, str] = field(default_factory=dict)


__all__ = [
    "BlankLine",
    "ChordLyricLine",
    "ChordOnlyLine",
    "ChordPlacement",
    "LyricLine",
    "Section",
    "Song",
    "SongLine",
]
