from dataclasses import dataclass, field
from typing import Dict, List

from src.models.findings import Finding, Severity


@dataclass
class RepoProfile:
    repo_path: str
    project_type: str
    language: str
    build_tool: str
    has_tests: bool
    has_dockerfile: bool
    has_ci: bool


@dataclass
class ModernizationResult:
    profile: RepoProfile
    findings: List[Finding] = field(default_factory=list)

    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.CRITICAL)

    @property
    def high_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.HIGH)

    @property
    def findings_sorted(self) -> List[Finding]:
        return sorted(self.findings, key=lambda f: f.severity_rank)

    @property
    def counts_by_severity(self) -> Dict[str, int]:
        counts = {sev.value: 0 for sev in Severity}
        for finding in self.findings:
            counts[finding.severity.value] += 1
        return counts
