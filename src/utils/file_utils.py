from pathlib import Path
from typing import Iterator, Optional, Set

IGNORED_DIRS = {
    ".git",
    "target",
    "build",
    "node_modules",
    ".idea",
    ".vscode",
    "dist",
    "coverage",
    "__pycache__",
    ".venv",
}


def iter_files(root: Path, extensions: Optional[Set[str]] = None) -> Iterator[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if extensions and path.suffix not in extensions:
            continue
        yield path


def read_text_safe(path: Path) -> str:
    return path.read_text(errors="ignore")
