from typing import Iterable, List

from src.models import Finding, XAIInsight
from src.xai.fix_suggester import get_fix_suggestion, suggest_before_after


def enrich_findings(findings):
    enriched = []

    for finding in findings:
        extra = get_fix_suggestion(finding.title)
        before, after = suggest_before_after(finding)

        finding.xai = XAIInsight(
            why_it_matters=extra["why"],
            suggested_fix=extra["fix"],
            before_snippet=before,
            after_snippet=after,
            impact=extra["impact"],
        )
        enriched.append(finding)

    return enriched


class ExplanationEngine:
    """Build explainable insights for each finding."""

    def enrich(self, findings: Iterable[Finding]) -> List[Finding]:
        return enrich_findings(findings)
