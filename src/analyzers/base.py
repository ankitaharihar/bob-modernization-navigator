"""Base class for modular analyzers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, List, Set

from src.models import Finding, RepoProfile
from src.utils import IGNORED_DIRS


class BaseAnalyzer(ABC):
    display_name = "Analyzer"

    def __init__(self, repo_path: str):
        self.root = Path(repo_path).resolve()

    def supports(self, profile: RepoProfile) -> bool:
        """Override to filter analyzer execution by project profile."""
        return True

    @abstractmethod
    def analyze(self) -> List[Finding]:
        ...

    def iter_files(self, extensions: Set[str]) -> Iterable[Path]:
        for path in self.root.rglob("*"):
            if path.is_file() and path.suffix in extensions:
                if not any(part in IGNORED_DIRS for part in path.parts):
                    yield path

    def relative(self, path: Path) -> str:
        return str(path.relative_to(self.root))
