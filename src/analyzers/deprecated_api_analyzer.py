"""Backward-compatible wrapper for deprecated analyzer naming."""

from src.analyzers.deprecated_analyzer import DeprecatedAnalyzer


class DeprecatedApiAnalyzer(DeprecatedAnalyzer):
    pass
