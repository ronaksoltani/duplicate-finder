from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path

CHUNK_SIZE = 1024 * 1024
IGNORED_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__"}


@dataclass(frozen=True)
class DuplicateGroup:
    sha256: str
    size_bytes: int
    paths: tuple[str, ...]

    @property
    def reclaimable_bytes(self) -> int:
        return self.size_bytes * (len(self.paths) - 1)


def fingerprint(path: Path, chunk_size: int = CHUNK_SIZE) -> str:
    """Hash a file incrementally, keeping memory use bounded."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _walk_files(root: Path):
    for current, dirs, filenames in os.walk(root, followlinks=False):
        dirs[:] = [name for name in dirs if name not in IGNORED_DIRS]
        for name in filenames:
            path = Path(current, name)
            try:
                if not path.is_symlink() and path.is_file():
                    yield path
            except OSError:
                continue


def find_duplicates(root: Path, min_size: int = 1) -> tuple[list[DuplicateGroup], int, int]:
    """Return duplicate groups, number of candidates, and unreadable count."""
    root = root.expanduser().resolve()
    if not root.is_dir():
        raise NotADirectoryError(root)
    by_size: dict[int, list[Path]] = {}
    unreadable = 0
    for path in _walk_files(root):
        try:
            size = path.stat().st_size
        except OSError:
            unreadable += 1
            continue
        if size >= min_size:
            by_size.setdefault(size, []).append(path)
    candidates = [path for paths in by_size.values() if len(paths) > 1 for path in paths]
    by_digest: dict[tuple[int, str], list[Path]] = {}
    for size, paths in by_size.items():
        if len(paths) < 2:
            continue
        for path in paths:
            try:
                by_digest.setdefault((size, fingerprint(path)), []).append(path)
            except OSError:
                unreadable += 1
    groups = [DuplicateGroup(digest, size, tuple(sorted(str(p) for p in paths)))
              for (size, digest), paths in by_digest.items() if len(paths) > 1]
    groups.sort(key=lambda group: (-group.reclaimable_bytes, group.paths[0]))
    return groups, len(candidates), unreadable
