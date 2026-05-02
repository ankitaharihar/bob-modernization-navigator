from pathlib import Path


def detect_project_type(root: Path) -> tuple[str, str, str]:
    has_pom = (root / "pom.xml").exists()
    has_gradle = (root / "build.gradle").exists() or (root / "build.gradle.kts").exists()
    has_package_json = (root / "package.json").exists()

    if has_pom:
        return "spring-boot-or-java", "java", "maven"
    if has_gradle:
        return "spring-boot-or-java", "java", "gradle"
    if has_package_json:
        return "nodejs", "javascript/typescript", "npm"
    return "unknown", "unknown", "unknown"


def has_tests(root: Path) -> bool:
    return any(
        [
            (root / "src" / "test").exists(),
            (root / "test").exists(),
            (root / "__tests__").exists(),
        ]
    )


def has_ci(root: Path) -> bool:
    return any(
        [
            (root / ".github" / "workflows").exists(),
            (root / "Jenkinsfile").exists(),
            (root / ".gitlab-ci.yml").exists(),
        ]
    )
