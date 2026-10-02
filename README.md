# Duplicate File Finder

Find byte-for-byte duplicate files by size and streaming SHA-256 fingerprints. The tool reports duplicate groups and the recoverable byte count; it never removes or changes a file.

## Quick start

```bash
python -m venv .venv
python -m pip install -e .
dupe-finder ~/Downloads --json duplicates.json
dupe-finder ./photos --csv duplicates.csv --min-size 4096
```

Review a report before taking any cleanup action. The estimate assumes one copy in each duplicate group would be retained. Symbolic links are ignored, and unreadable paths are counted instead of crashing the scan.

## Learning notes

Files are grouped by size first because identical files must have identical byte counts. Only those candidates are read, in fixed-size chunks, into SHA-256. This avoids loading large videos into memory and avoids hashing every unique-sized file.

## Development

```bash
python -m pip install -e ".[dev]"
pytest
```

## License

MIT. See [LICENSE](LICENSE).
