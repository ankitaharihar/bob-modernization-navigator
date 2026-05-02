from src.analyzers.dependency_analyzer import DependencyAnalyzer
from src.analyzers.deprecated_analyzer import DeprecatedAnalyzer
from src.analyzers.security_analyzer import SecurityAnalyzer
from src.analyzers.test_gap_analyzer import TestGapAnalyzer


def get_default_analyzers(repo_path: str):
    """Default analyzer pipeline. Add new analyzers here to make them plug-and-play."""
    return [
        DependencyAnalyzer(repo_path),
        DeprecatedAnalyzer(repo_path),
        SecurityAnalyzer(repo_path),
        TestGapAnalyzer(repo_path),
    ]


__all__ = [
    "DependencyAnalyzer",
    "DeprecatedAnalyzer",
    "SecurityAnalyzer",
    "TestGapAnalyzer",
    "get_default_analyzers",
]
