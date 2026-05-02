from typing import Iterable, List

from src.models import Finding, Severity, XAIInsight
from src.xai.fix_suggester import suggest_before_after


class ExplanationEngine:
    """Build explainable insights for each finding."""

    def enrich(self, findings: Iterable[Finding]) -> List[Finding]:
        enriched: List[Finding] = []
        for finding in findings:
            before, after = suggest_before_after(finding)
            finding.xai = XAIInsight(
                why_it_matters=self._why_it_matters(finding),
                suggested_fix=finding.recommendation or "Apply a standards-compliant modernization change.",
                before_snippet=before,
                after_snippet=after,
                impact=self._impact(finding),
            )
            enriched.append(finding)
        return enriched

    def _why_it_matters(self, finding: Finding) -> str:
        title = finding.title.lower()
        if "sql injection" in title:
            return "Unsanitized query construction allows attackers to alter queries and exfiltrate or modify data."
        if "hardcoded secret" in title:
            return "Committed secrets can be leaked through source control, logs, artifacts, or accidental sharing."
        if "deprecated spring security" in title or "websecurityconfigureradapter" in title:
            return "Deprecated framework APIs block runtime and dependency upgrades and increase maintenance risk."
        if "cors" in title:
            return "Permissive CORS can allow untrusted origins to call sensitive endpoints from user browsers."
        if finding.severity == Severity.CRITICAL:
            return "Critical issues can lead to immediate security or production risk if left unresolved."
        if finding.severity == Severity.HIGH:
            return "High severity findings increase failure probability and technical debt in modernization programs."
        return "Addressing this finding improves reliability, maintainability, and long-term upgrade readiness."

    def _impact(self, finding: Finding) -> str:
        if finding.severity == Severity.CRITICAL:
            return "Removes high-risk exploit paths and materially improves security posture."
        if finding.severity == Severity.HIGH:
            return "Unblocks modernization steps and reduces upgrade friction in subsequent releases."
        return "Improves code quality and lowers future maintenance cost."
