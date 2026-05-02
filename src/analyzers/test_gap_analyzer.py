"""Test gap analyzer for Java and Node source sets."""

from pathlib import Path
from typing import List

from src.analyzers.base import BaseAnalyzer
from src.models import Category, Finding, RepoProfile, Severity

JAVA_SKIP_SUFFIXES = ("Application", "Config", "Configuration", "Constants", "Exception")
NODE_TEST_DIRS = ["test", "__tests__", "tests", "spec"]


class TestGapAnalyzer(BaseAnalyzer):
    display_name = "Test Gaps"

    def supports(self, profile: RepoProfile) -> bool:
        return profile.language in {"java", "javascript/typescript", "unknown"}

    def analyze(self) -> List[Finding]:
        findings: List[Finding] = []
        java_src = self.root / "src" / "main" / "java"
        java_test = self.root / "src" / "test" / "java"

        if java_src.exists():
            findings.extend(self._check_java(java_src, java_test))

        if (self.root / "package.json").exists():
            findings.extend(self._check_node())

        return findings

    def _check_java(self, src_dir: Path, test_dir: Path) -> List[Finding]:
        findings: List[Finding] = []
        test_files = {p.name for p in test_dir.rglob("*.java")} if test_dir.exists() else set()

        for src_file in src_dir.rglob("*.java"):
            cls = src_file.stem
            if cls.endswith(JAVA_SKIP_SUFFIXES):
                continue
            if f"{cls}Test.java" not in test_files:
                findings.append(
                    Finding(
                        category=Category.TEST_GAP,
                        severity=Severity.MEDIUM,
                        title=f"Missing test: {cls}",
                        description=f"No {cls}Test.java found under src/test/java.",
                        file_path=self.relative(src_file),
                        recommendation=(
                            f"Create {cls}Test.java for happy path, invalid input, edge cases, and exceptions."
                        ),
                        effort="medium",
                    )
                )
        return findings

    def _check_node(self) -> List[Finding]:
        findings: List[Finding] = []
        test_files: set[str] = set()
        for dir_name in NODE_TEST_DIRS:
            test_dir = self.root / dir_name
            if test_dir.exists():
                for path in test_dir.rglob("*"):
                    test_files.add(path.stem)

        src_dir = self.root / "src"
        if not src_dir.exists():
            return findings

        for src_file in src_dir.rglob("*"):
            if src_file.suffix not in {".js", ".ts"}:
                continue
            if ".test." in src_file.name or ".spec." in src_file.name:
                continue
            mod = src_file.stem
            if f"{mod}.test" not in test_files and f"{mod}.spec" not in test_files:
                findings.append(
                    Finding(
                        category=Category.TEST_GAP,
                        severity=Severity.MEDIUM,
                        title=f"Missing test: {mod}",
                        description=f"No test/spec found for {src_file.name}.",
                        file_path=self.relative(src_file),
                        recommendation="Add success, error, and boundary-path tests.",
                        effort="medium",
                    )
                )
        return findings
