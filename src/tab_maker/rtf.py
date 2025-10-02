"""RTF export for Tab-Maker songs."""
from __future__ import annotations

from typing import Iterable, List, Sequence

from .chord_layout import RenderSegment
from .models import Song
from .text import song_to_plain_lines

_RTF_HEADER = r"{\rtf1\ansi\deff0{\fonttbl{\f0 Courier New;}}\viewkind4\uc1\pard\f0\fs22 "
_RTF_FOOTER = "}"


def _escape_rtf(text: str) -> str:
    return text.replace("\\", "\\\\").replace("{", r"\{").replace("}", r"\}")


def lines_to_rtf(lines: Iterable[str]) -> str:
    rtf_parts: List[str] = [_RTF_HEADER]
    empty = True
    for line in lines:
        empty = False
        if line:
            rtf_parts.append(f"{_escape_rtf(line)}\\par")
        else:
            rtf_parts.append("\\par")
    if empty:
        rtf_parts.append("\\par")
    rtf_parts.append(_RTF_FOOTER)
    return "\n".join(rtf_parts)


def segments_to_rtf(segments: Sequence[RenderSegment]) -> str:
    """Render annotated two-line segments to RTF with chord formatting."""
    parts: List[str] = [_RTF_HEADER]
    title_text: str | None = None
    artist_text: str | None = None
    skip_indices: set[int] = set()

    idx = 0
    while idx < len(segments) and segments[idx].kind == "metadata":
        raw_text = segments[idx].text
        lowered = raw_text.lower()
        if lowered.startswith("title:"):
            value = raw_text.split(":", 1)[1].strip()
            if value:
                title_text = value
                skip_indices.add(idx)
        elif lowered.startswith("artist:"):
            value = raw_text.split(":", 1)[1].strip()
            if value:
                artist_text = value
                skip_indices.add(idx)
        idx += 1

    if title_text or artist_text:
        header_style = r"\pard\plain\qc\b\f0\fs32 "
        if title_text:
            parts.append(f"{header_style}{_escape_rtf(title_text)}\\par")
        if artist_text:
            parts.append(f"{header_style}{_escape_rtf(artist_text)}\\par")
        parts.append("\\pard\\f0\\fs22 ")

    idx = 0
    started = False

    while idx < len(segments):
        if idx in skip_indices:
            idx += 1
            continue

        segment = segments[idx]
        kind = segment.kind

        if kind == "blank":
            parts.append("\\par")
            started = False
            idx += 1
            continue

        if kind in {"metadata", "section", "other"}:
            if started:
                parts.append("\\par")
            parts.append(f"{_escape_rtf(segment.text)}\\par")
            started = False
            idx += 1
            continue

        if kind == "chord":
            chord_text = f"\\b {_escape_rtf(segment.text)}\\b0"
            if idx + 1 < len(segments) and segments[idx + 1].kind == "lyric":
                lyric_text = _escape_rtf(segments[idx + 1].text)
                if started:
                    parts.append("\\par")
                parts.append(f"{chord_text}\\line {lyric_text}")
                parts.append("\\par")
                started = False
                idx += 2
                continue
            else:
                if started:
                    parts.append("\\par")
                parts.append(f"{chord_text}\\par")
                started = False
                idx += 1
                continue

        if kind == "lyric":
            if started:
                parts.append("\\par")
            parts.append(f"{_escape_rtf(segment.text)}\\par")
            started = False
            idx += 1
            continue

        # Fallback
        if started:
            parts.append("\\par")
        parts.append(f"{_escape_rtf(segment.text)}\\par")
        started = False
        idx += 1

    parts.append(_RTF_FOOTER)
    return "\n".join(parts)

def song_to_rtf(song: Song) -> str:
    return lines_to_rtf(song_to_plain_lines(song))


__all__ = ["song_to_rtf", "lines_to_rtf", "segments_to_rtf"]

