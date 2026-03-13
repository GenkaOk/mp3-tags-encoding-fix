# MP3 Tags Encoding Fix

![Tests](https://github.com/GenkaOk/mp3-tags-encoding-fix/actions/workflows/python-tests.yml/badge.svg)

Read in other languages: [Russian](https://github.com/GenkaOk/mp3-tags-encoding-fix/blob/master/README.ru.md)

Small Python utility to read ID3 tags from MP3 files, fix common Cyrillic/encoding issues, and save corrected tags (optionally creating backup files). Includes a test suite with mocked ID3 objects to cover processing logic.

## Features
- Decode/repair tag strings encoded with common mismatches (Latin-1 → CP1251 → UTF-8).
- Process a single folder or walk directories recursively.
- Optionally create backup (`-fix.mp3`) files or overwrite originals.
- Dry-run mode to preview changes without writing files.

## Requirements
- Python 3.8+
- mutagen

Install dependencies:

```bash
python -m pip install mutagen
```

OR

```bash
python -m pip install -r requirements.txt
```

## Project layout
- mp3_processor.py — main script and library functions (including parse_and_fix_tags and decode_).
- tests/test_mp3_processor.py — unittest suite (uses unittest.mock to replace EasyID3 and file ops).

## Usage

Run the script from the command line:

```bash
python mp3_processor.py PATH_TO_FOLDER [--recursive] [--backup yes|no] [--dry-run]
```

Options:
- PATH_TO_FOLDER — folder containing MP3 files to process.
- --recursive — descend into subdirectories.
- --backup yes|no — create backup files by default (`yes`). If `no`, tags are saved in-place.
- --dry-run — do not write any files; only show what would be changed.

Examples:
- Process a single directory and create backups:
  `python mp3_processor.py ./music --backup yes`
- Process recursively and overwrite original files:
  `python mp3_processor.py ./music --recursive --backup no`
- Preview changes without writing:
  `python mp3_processor.py ./music --dry-run`

## License
MIT License — feel free to reuse and adapt.