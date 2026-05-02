from dataclasses import dataclass
from typing import List, Sequence, Tuple

from src.analyzers import get_default_analyzers
from src.models import Finding, RepoProfile


@dataclass
class AnalyzerRun:
    name: str
    findings_count: int


class AnalyzerEngine:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self._analyzers = get_default_analyzers(repo_path)

    def run(self, profile: RepoProfile) -> Tuple[List[Finding], Sequence[AnalyzerRun]]:
        findings: List[Finding] = []
        runs: List[AnalyzerRun] = []

        for analyzer in self._analyzers:
            if not analyzer.supports(profile):
                continue
            batch = analyzer.analyze()
            findings.extend(batch)
            runs.append(AnalyzerRun(name=analyzer.display_name, findings_count=len(batch)))

        return findings, runs
