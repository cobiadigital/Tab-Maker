# Tab-Maker

Convert Ultimate Guitar chord sheets into ChordPro and transform existing `.cho` files into printer-friendly RTF with chords above the lyrics.

## Getting Started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Ultimate Guitar → ChordPro

```bash
python -m tab_maker.cli input.txt -o output.cho --title "Song Title" --artist "Artist Name"
```

Stream from the clipboard:

```bash
pbpaste | python -m tab_maker.cli --title "Song Title" > song.cho
```

## ChordPro (.cho) → RTF

```bash
python -m tab_maker.cho_to_rtf_cli song.cho -o song.rtf
```

The RTF output places each chord line (bolded) directly above its lyric line so the chart reads naturally in most word processors. Omit `-o` to write the RTF to stdout.
