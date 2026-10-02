import argparse
import csv
import json
from dataclasses import asdict
from pathlib import Path

from .finder import find_duplicates


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Find duplicate files without deleting anything.")
    parser.add_argument("directory", type=Path)
    parser.add_argument("--min-size", type=int, default=1, help="ignore smaller files (bytes)")
    parser.add_argument("--json", type=Path, dest="json_path")
    parser.add_argument("--csv", type=Path, dest="csv_path")
    args = parser.parse_args(argv)
    if args.min_size < 0:
        parser.error("--min-size must be non-negative")
    try:
        groups, candidates, unreadable = find_duplicates(args.directory, args.min_size)
    except OSError as error:
        parser.error(str(error))
    total = sum(group.reclaimable_bytes for group in groups)
    for index, group in enumerate(groups, 1):
        print(f"Group {index}: {group.size_bytes} bytes each; {group.reclaimable_bytes} reclaimable")
        for path in group.paths:
            print(f"  {path}")
    print(f"{len(groups)} duplicate group(s), {candidates} candidate file(s), {unreadable} unreadable; estimated reclaimable: {total} bytes")
    if args.json_path:
        args.json_path.write_text(json.dumps([asdict(g) | {"reclaimable_bytes": g.reclaimable_bytes} for g in groups], indent=2), encoding="utf-8")
    if args.csv_path:
        with args.csv_path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(["sha256", "size_bytes", "reclaimable_bytes", "path"])
            for group in groups:
                for path in group.paths:
                    writer.writerow([group.sha256, group.size_bytes, group.reclaimable_bytes, path])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
