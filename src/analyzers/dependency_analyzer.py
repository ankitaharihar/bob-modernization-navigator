"""Dependency analyzer for Java/Node runtime and legacy packages."""

import json
import re
from typing import List

from src.analyzers.base import BaseAnalyzer
from src.models import Category, Finding, RepoProfile, Severity


class DependencyAnalyzer(BaseAnalyzer):
    display_name = "Dependencies"

    OLD_JAVA_VERSIONS = {"1.8", "8", "11", "17", "21"}
    OLD_NODE_VERSIONS = ["10", "12", "14", "16", "18", "20"]
    OLD_SPRING_PREFIXES = ("1.", "2.", "3.")
    LEGACY_JAVA_DEPS = [
        ("junit", "junit"),
        ("log4j", "log4j"),
        ("commons-collections", "commons-collections"),
    ]
    DEPRECATED_NODE_PACKAGES = {
        "request": "Replace with fetch, axios, or undici.",
        "node-sass": "Replace with sass (Dart Sass).",
        "gulp-util": "Replace with individual maintained packages.",
        "babel-eslint": "Replace with @babel/eslint-parser.",
    }

    def supports(self, profile: RepoProfile) -> bool:
        return profile.language in {"java", "javascript/typescript", "unknown"}

    def analyze(self) -> List[Finding]:
        findings: List[Finding] = []
        findings.extend(self._check_pom())
        findings.extend(self._check_package_json())
        return findings

    def _check_pom(self) -> List[Finding]:
        pom = self.root / "pom.xml"
        if not pom.exists():
            return []

        content = pom.read_text(errors="ignore")
        findings: List[Finding] = []

        java_match = re.search(r"<java\.version>(.*?)</java\.version>", content)
        if java_match and java_match.group(1).strip() in self.OLD_JAVA_VERSIONS:
            findings.append(
                Finding(
                    category=Category.DEPENDENCY,
                    severity=Severity.HIGH,
                    title=f"Old Java version: {java_match.group(1).strip()}",
                    description="Project targets a Java version below latest LTS.",
                    file_path="pom.xml",
                    recommendation="Upgrade to Java 25 LTS after compatibility validation.",
                    effort="medium",
                )
            )

        spring_match = re.search(
            r"<artifactId>spring-boot-starter-parent</artifactId>\s*<version>(.*?)</version>",
            content,
            re.DOTALL,
        )
        if spring_match and spring_match.group(1).strip().startswith(self.OLD_SPRING_PREFIXES):
            findings.append(
                Finding(
                    category=Category.DEPENDENCY,
                    severity=Severity.HIGH,
                    title=f"Old Spring Boot: {spring_match.group(1).strip()}",
                    description="Spring Boot 1.x/2.x/3.x may block latest-runtime upgrades.",
                    file_path="pom.xml",
                    recommendation="Plan migration to a latest supported Spring Boot line.",
                    effort="high",
                )
            )

        for group, artifact in self.LEGACY_JAVA_DEPS:
            if f"<groupId>{group}</groupId>" in content and f"<artifactId>{artifact}</artifactId>" in content:
                findings.append(
                    Finding(
                        category=Category.DEPENDENCY,
                        severity=Severity.MEDIUM,
                        title=f"Legacy dependency: {group}:{artifact}",
                        description=f"{group}:{artifact} is legacy or has safer modern alternatives.",
                        file_path="pom.xml",
                        recommendation="Review and replace with a supported dependency.",
                        effort="medium",
                    )
                )

        return findings

    def _check_package_json(self) -> List[Finding]:
        pkg = self.root / "package.json"
        if not pkg.exists():
            return []

        try:
            data = json.loads(pkg.read_text(errors="ignore"))
        except json.JSONDecodeError:
            return [
                Finding(
                    category=Category.DEPENDENCY,
                    severity=Severity.MEDIUM,
                    title="Invalid package.json",
                    description="package.json could not be parsed.",
                    file_path="package.json",
                    recommendation="Fix JSON syntax before dependency analysis.",
                    effort="low",
                )
            ]

        findings: List[Finding] = []
        node_ver = data.get("engines", {}).get("node", "")
        if any(v in node_ver for v in self.OLD_NODE_VERSIONS):
            findings.append(
                Finding(
                    category=Category.DEPENDENCY,
                    severity=Severity.HIGH,
                    title=f"Old Node.js engine: {node_ver}",
                    description="Project targets an outdated Node.js version.",
                    file_path="package.json",
                    recommendation="Upgrade to latest Node.js LTS and validate dependencies.",
                    effort="medium",
                )
            )

        all_deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
        for pkg_name, rec in self.DEPRECATED_NODE_PACKAGES.items():
            if pkg_name in all_deps:
                findings.append(
                    Finding(
                        category=Category.DEPENDENCY,
                        severity=Severity.MEDIUM,
                        title=f"Deprecated Node package: {pkg_name}",
                        description=f"{pkg_name} is deprecated or not maintained.",
                        file_path="package.json",
                        recommendation=rec,
                        effort="medium",
                    )
                )

        return findings
