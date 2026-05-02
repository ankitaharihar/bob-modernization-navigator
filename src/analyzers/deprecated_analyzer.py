"""
Deprecated API Analyzer: detects outdated APIs in Java and JavaScript/TypeScript.
"""

from typing import List

from src.analyzers.base import BaseAnalyzer
from src.models import Category, Finding, Severity

JAVA_EXTENSIONS = {".java"}
JS_EXTENSIONS = {".js", ".ts", ".jsx", ".tsx"}

PATTERNS = {
    "javax.persistence": (
        Severity.HIGH,
        "javax.persistence usage detected",
        "Migrate to jakarta.persistence for Spring Boot 3+ compatibility.",
    ),
    "javax.validation": (
        Severity.HIGH,
        "javax.validation usage detected",
        "Migrate to jakarta.validation for Spring Boot 3+ compatibility.",
    ),
    "javax.servlet": (
        Severity.HIGH,
        "javax.servlet usage detected",
        "Migrate to jakarta.servlet for Spring Boot 3+ compatibility.",
    ),
    "WebSecurityConfigurerAdapter": (
        Severity.HIGH,
        "Deprecated Spring Security: WebSecurityConfigurerAdapter",
        "Replace with a SecurityFilterChain bean and Spring Security 6+ DSL.",
    ),
    "csrf().disable()": (
        Severity.HIGH,
        "CSRF protection disabled",
        "Re-enable CSRF for browser flows or implement token-based strategy intentionally.",
    ),
    "org.junit.Test": (
        Severity.MEDIUM,
        "JUnit 4 usage detected",
        "Migrate tests to JUnit 5 (org.junit.jupiter.api.Test).",
    ),
    "new Date(": (
        Severity.LOW,
        "Legacy Date API usage",
        "Prefer java.time APIs such as LocalDateTime or Instant.",
    ),
    "Calendar.getInstance": (
        Severity.LOW,
        "Legacy Calendar API usage",
        "Prefer java.time APIs over java.util.Calendar.",
    ),
    "var ": (
        Severity.LOW,
        "JavaScript var keyword detected",
        "Replace var with let/const for predictable scoping.",
    ),
    "function(": (
        Severity.LOW,
        "Old-style function expression detected",
        "Consider arrow functions and async/await where it improves clarity.",
    ),
}


class DeprecatedAnalyzer(BaseAnalyzer):
    display_name = "Deprecated APIs"

    def analyze(self) -> List[Finding]:
        findings: List[Finding] = []
        for path in self.iter_files(JAVA_EXTENSIONS | JS_EXTENSIONS):
            content = path.read_text(errors="ignore")
            for pattern, (severity, title, recommendation) in PATTERNS.items():
                if pattern in content:
                    findings.append(
                        Finding(
                            category=Category.DEPRECATED_API,
                            severity=severity,
                            title=title,
                            description=f"Pattern `{pattern}` found in source file.",
                            file_path=self.relative(path),
                            recommendation=recommendation,
                            effort="medium",
                        )
                    )
        return findings
