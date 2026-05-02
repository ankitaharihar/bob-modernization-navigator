from pathlib import Path
from typing import Iterator, Optional, Set

from src.models import RepoProfile
from src.utils.file_utils import iter_files
from src.utils.repo_utils import detect_project_type, has_ci, has_tests


class RepoScanner:
    def __init__(self, repo_path: str):
        self.root = Path(repo_path).resolve()

    def profile(self) -> RepoProfile:
        project_type, language, build_tool = detect_project_type(self.root)
        return RepoProfile(
            repo_path=str(self.root),
            project_type=project_type,
            language=language,
            build_tool=build_tool,
            has_tests=has_tests(self.root),
            has_dockerfile=(self.root / "Dockerfile").exists(),
            has_ci=has_ci(self.root),
        )

    def iter_files(self, extensions: Optional[Set[str]] = None) -> Iterator[Path]:
        yield from iter_files(self.root, extensions)
