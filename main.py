"""
Bob Modernization Navigator — CLI entry point.

Usage:
  bmn analyze --repo <path> [--output <dir>]
  bmn analyze --repo ./sample-apps/legacy-spring-app --output modernization-output-before
"""

import sys
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from src.scanner import RepoScanner
from src.models import ModernizationResult, Severity
from src.analyzers.dependency_analyzer import DependencyAnalyzer
from src.analyzers.deprecated_api_analyzer import DeprecatedApiAnalyzer
from src.analyzers.security_analyzer import SecurityAnalyzer
from src.analyzers.test_gap_analyzer import TestGapAnalyzer
from src.report.report_generator import ReportGenerator

console = Console()

SEVERITY_STYLE = {
    Severity.CRITICAL: "bold red",
    Severity.HIGH: "bold yellow",
    Severity.MEDIUM: "yellow",
    Severity.LOW: "cyan",
}


@click.group()
def cli():
    """Bob Modernization Navigator — legacy code modernization agent."""
    pass


@cli.command()
@click.option("--repo", required=True, help="Path to the legacy repository to analyze.")
@click.option("--output", default="modernization-output", show_default=True,
              help="Directory where reports will be written.")
def analyze(repo: str, output: str):
    """Scan a repository and generate modernization reports."""

    console.print(Panel.fit(
        "[bold blue]Bob Modernization Navigator[/bold blue]\n"
        "[dim]Powered by IBM Bob IDE[/dim]",
        border_style="blue",
    ))
    console.print(f"\n📁 Repository: [green]{repo}[/green]")
    console.print(f"📄 Output dir: [cyan]{output}[/cyan]\n")

    # ── 1. Profile the repository ─────────────────────────────────────────
    with console.status("Profiling repository…"):
        scanner = RepoScanner(repo)
        profile = scanner.profile()

    console.print(f"[bold]Project type:[/bold] {profile.project_type}  "
                  f"[bold]Language:[/bold] {profile.language}  "
                  f"[bold]Build:[/bold] {profile.build_tool}")
    console.print(f"Tests: {'✅' if profile.has_tests else '❌'}  "
                  f"Dockerfile: {'✅' if profile.has_dockerfile else '❌'}  "
                  f"CI/CD: {'✅' if profile.has_ci else '❌'}\n")

    # ── 2. Run all analyzers ──────────────────────────────────────────────
    findings = []
    analyzers = [
        ("Dependencies", DependencyAnalyzer(repo)),
        ("Deprecated APIs", DeprecatedApiAnalyzer(repo)),
        ("Security", SecurityAnalyzer(repo)),
        ("Test Gaps", TestGapAnalyzer(repo)),
    ]

    for name, analyzer in analyzers:
        with console.status(f"Running {name} analyzer…"):
            batch = analyzer.analyze()
        findings.extend(batch)
        console.print(f"  {name}: [bold]{len(batch)}[/bold] findings")

    result = ModernizationResult(profile=profile, findings=findings)

    # ── 3. Print findings table ───────────────────────────────────────────
    table = Table(title="\nModernization Findings", box=box.ROUNDED, show_lines=True)
    table.add_column("Severity", style="bold", min_width=10)
    table.add_column("Category", min_width=14)
    table.add_column("Title", min_width=40)
    table.add_column("File", style="dim", min_width=30)

    for f in result.findings_sorted:
        style = SEVERITY_STYLE.get(f.severity, "")
        table.add_row(
            f.severity.value.upper(),
            f.category.value,
            f.title,
            f.file_path or "N/A",
            style=style,
        )

    console.print(table)

    # ── 4. Summary counts ─────────────────────────────────────────────────
    console.print(
        f"\n[bold red]Critical:[/bold red] {result.critical_count}  "
        f"[bold yellow]High:[/bold yellow] {result.high_count}  "
        f"Total: {len(findings)}"
    )

    # ── 5. Generate reports ───────────────────────────────────────────────
    with console.status("Generating reports…"):
        ReportGenerator(output).generate(result)

    console.print(f"\n[bold green]✅ Done![/bold green] Reports written to: [cyan]{output}/[/cyan]")
    console.print("\n[bold]Next steps:[/bold]")
    console.print("  1. Open [cyan]bob-prompts.md[/cyan] in Bob IDE")
    console.print("  2. Run Prompt 1 to understand findings")
    console.print("  3. Run Prompt 2 to implement the first fix")
    console.print("  4. Re-run: [dim]bmn analyze --repo <path> --output modernization-output-after[/dim]")
    console.print("  5. Compare: [dim]python scripts/compare_runs.py modernization-output-before modernization-output-after[/dim]\n")

    # Exit with non-zero if critical findings found (useful for CI)
    if result.critical_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    cli()
