"""Security analyzer for secrets and risky patterns."""

import re
from typing import List

from src.analyzers.base import BaseAnalyzer
from src.models import Category, Finding, RepoProfile, Severity

SCAN_EXTENSIONS = {".java", ".js", ".ts", ".properties", ".yml", ".yaml", ".env", ".json"}

SECRET_PATTERNS = [
    r"password\s*=\s*['\"]?.+['\"]?",
    r"api[_-]?key\s*=\s*['\"]?.+['\"]?",
    r"secret\s*=\s*['\"]?.+['\"]?",
    r"token\s*=\s*['\"]?.+['\"]?",
    r"aws_access_key_id\s*=\s*.+",
    r"private_key\s*=\s*.+",
]

RISKY_PATTERNS = {
    r"SELECT\s+.*\+": (
        Severity.HIGH,
        "Possible SQL injection risk",
        "Use parameterized queries or Spring Data abstractions.",
    ),
    r'@CrossOrigin\("?\*"?\)': (
        Severity.MEDIUM,
        "Permissive CORS: @CrossOrigin(\"*\")",
        "Restrict allowed origins to trusted domains.",
    ),
    r'MessageDigest\.getInstance\("MD5"\)': (
        Severity.HIGH,
        "Weak hash: MD5",
        "Replace with SHA-256 or bcrypt/Argon2 for credentials.",
    ),
    r'MessageDigest\.getInstance\("SHA1"\)': (
        Severity.HIGH,
        "Weak hash: SHA-1",
        "Replace with SHA-256 or stronger password hashing algorithms.",
    ),
    r"Runtime\.getRuntime\(\)\.exec\(": (
        Severity.HIGH,
        "Unsafe Runtime.exec() call",
        "Use ProcessBuilder with explicit argument lists.",
    ),
    r"eval\(": (
        Severity.HIGH,
        "JavaScript eval() usage",
        "Avoid eval and use safe parsing/execution alternatives.",
    ),
}


class SecurityAnalyzer(BaseAnalyzer):
    display_name = "Security"

    def supports(self, profile: RepoProfile) -> bool:
        return profile.language in {"java", "javascript/typescript", "unknown"}

    def analyze(self) -> List[Finding]:
        findings: List[Finding] = []
        for path in self.iter_files(SCAN_EXTENSIONS):
            content = path.read_text(errors="ignore")
            rel = self.relative(path)
            findings.extend(self._check_secrets(content, rel))
            findings.extend(self._check_risky_patterns(content, rel))
        return findings

    def _check_secrets(self, content: str, rel_path: str) -> List[Finding]:
        findings: List[Finding] = []
        for pattern in SECRET_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                findings.append(
                    Finding(
                        category=Category.SECURITY,
                        severity=Severity.CRITICAL,
                        title="Possible hardcoded secret",
                        description=f"Matched pattern: `{pattern}`",
                        file_path=rel_path,
                        recommendation="Move secrets to env vars or secret managers.",
                        effort="low",
                    )
                )
        return findings

    def _check_risky_patterns(self, content: str, rel_path: str) -> List[Finding]:
        findings: List[Finding] = []
        for pattern, (severity, title, recommendation) in RISKY_PATTERNS.items():
            if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                findings.append(
                    Finding(
                        category=Category.SECURITY,
                        severity=severity,
                        title=title,
                        description=f"Risky pattern detected: `{pattern}`",
                        file_path=rel_path,
                        recommendation=recommendation,
                        effort="medium",
                    )
                )
        return findings
