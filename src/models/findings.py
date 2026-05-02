from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Category(str, Enum):
    DEPENDENCY = "dependency"
    DEPRECATED_API = "deprecated-api"
    SECURITY = "security"
    TEST_GAP = "test-gap"


SEVERITY_ORDER = {
    Severity.CRITICAL: 0,
    Severity.HIGH: 1,
    Severity.MEDIUM: 2,
    Severity.LOW: 3,
}


@dataclass
class XAIInsight:
    why_it_matters: str
    suggested_fix: str
    before_snippet: str
    after_snippet: str
    impact: str


@dataclass
class Finding:
    category: Category
    severity: Severity
    title: str
    description: str
    file_path: Optional[str] = None
    recommendation: Optional[str] = None
    effort: str = "medium"
    xai: Optional[XAIInsight] = None

    @property
    def severity_rank(self) -> int:
        return SEVERITY_ORDER.get(self.severity, 99)
