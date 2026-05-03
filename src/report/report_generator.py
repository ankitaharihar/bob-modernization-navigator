"""
Report Generator: produces all output files from a ModernizationResult.

Output files:
  modernization-report.md   — full technical findings + roadmap
  bob-prompts.md            — copy-paste prompts for IBM Bob IDE
  judge-summary.md          — concise summary for hackathon judges
  dashboard.html            — simple visual summary (opens in browser)
"""

import json
from collections import defaultdict
from pathlib import Path
from src.models import ModernizationResult, Severity
from src.xai.explanation_engine import enrich_findings


SEVERITY_EMOJI = {
    Severity.CRITICAL: "🔴",
    Severity.HIGH: "🟠",
    Severity.MEDIUM: "🟡",
    Severity.LOW: "🔵",
}


class ReportGenerator:
    def __init__(self, output_dir: str):
        self.out = Path(output_dir)
        self.out.mkdir(parents=True, exist_ok=True)

    def generate(self, result: ModernizationResult) -> None:
        self._write_main_report(result)
        self._write_bob_prompts(result)
        self._write_judge_summary(result)
        self._write_dashboard(result)

    # ── Main Markdown Report ───────────────────────────────────────────────

    def _write_main_report(self, result: ModernizationResult) -> None:
        p = result.profile
        enriched_findings = enrich_findings(result.findings_sorted)
        by_cat = defaultdict(list)
        for f in enriched_findings:
            by_cat[f.category].append(f)

        lines = [
            "# Modernization Report\n",
            "## Executive Summary\n",
            "Analysis of modernization opportunities across dependency versions, "
            "deprecated APIs, security risks, and test coverage gaps.\n",
            "## Repository Profile\n",
            f"| Field | Value |",
            f"|---|---|",
            f"| Repository | `{p.repo_path}` |",
            f"| Project type | `{p.project_type}` |",
            f"| Language | `{p.language}` |",
            f"| Build tool | `{p.build_tool}` |",
            f"| Tests present | `{p.has_tests}` |",
            f"| Dockerfile | `{p.has_dockerfile}` |",
            f"| CI/CD | `{p.has_ci}` |\n",
            "## Findings Summary\n",
            "| Severity | Count |",
            "|---|---:|",
        ]

        for sev in Severity:
            count = sum(1 for f in result.findings if f.severity == sev)
            if count:
                lines.append(f"| {SEVERITY_EMOJI[sev]} {sev.value.capitalize()} | {count} |")

        lines.append(f"\n**Total findings:** {len(result.findings)}\n")

        lines.extend(self._write_xai_section(enriched_findings))

        for cat, findings in by_cat.items():
            lines += [
                f"## {cat.value.replace('-', ' ').title()} Findings\n",
                "| Severity | Title | File | Recommendation | Effort |",
                "|---|---|---|---|---|",
            ]
            for f in findings:
                emoji = SEVERITY_EMOJI.get(f.severity, "")
                lines.append(
                    f"| {emoji} {f.severity.value} | {f.title} "
                    f"| `{f.file_path or 'N/A'}` | {f.recommendation or 'N/A'} | {f.effort} |"
                )
            lines.append("")

        lines += [
            "## Prioritized Migration Roadmap\n",
            "### Phase 1 — Stabilize & Secure",
            "- Remove hardcoded secrets; move to environment variables.",
            "- Fix critical and high security findings.",
            "- Add tests for risky business logic.\n",
            "### Phase 2 — Upgrade Runtime & Dependencies",
            "- Upgrade Java / Node.js / Spring Boot versions.",
            "- Upgrade build plugins and dependency baseline.",
            "- Run full regression suite after each upgrade.\n",
            "### Phase 3 — Migrate Deprecated APIs",
            "- Replace `javax.*` imports with `jakarta.*`.",
            "- Replace `WebSecurityConfigurerAdapter` with `SecurityFilterChain`.",
            "- Migrate JUnit 4 tests to JUnit 5.\n",
            "### Phase 4 — Improve Quality & Documentation",
            "- Generate missing unit and integration tests.",
            "- Update README and migration guide.",
            "- Generate PR summaries and release notes.\n",
            "## Checklist\n",
            "- [ ] Review dependency upgrade plan",
            "- [ ] Fix all critical and high security risks",
            "- [ ] Replace deprecated APIs",
            "- [ ] Add missing tests",
            "- [ ] Update documentation",
            "- [ ] Implement fixes using IBM Bob IDE",
            "- [ ] Export Bob task session reports to `bob_sessions/`\n",
        ]

        (self.out / "modernization-report.md").write_text("\n".join(lines), encoding="utf-8")

    def _write_xai_section(self, findings):
        lines = ["## Explainable AI (XAI) Insights\n"]
        if not findings:
            lines.append("No findings available.\n")
            return lines

        for item in findings:
            lines.append(f"Issue: {item.title}")
            lines.append(f"Why: {item.xai.why_it_matters if item.xai else item.description}")
            lines.append(f"Fix: {item.xai.suggested_fix if item.xai else item.recommendation or 'Code update required.'}")
            lines.append(f"Impact: {item.xai.impact if item.xai else 'Improves maintainability.'}\n")

        return lines

    # ── Bob Prompts ────────────────────────────────────────────────────────

    def _write_bob_prompts(self, result: ModernizationResult) -> None:
        content = """\
# IBM Bob IDE — Copy-Paste Prompts

## Prompt 1: Understand the Repository
```
You are my enterprise modernization architect.

Analyze this workspace and explain:
1. What this project does and its purpose.
2. The main modules, packages, and key files.
3. The highest modernization risks based on modernization-output-before/modernization-report.md.
4. Which findings are the safest AND most impactful to fix first.
5. A recommended implementation order for a hackathon demo.

Keep suggestions scoped to changes safe for a demo.
```

## Prompt 2: Implement the First Fix (SQL Injection)
```
Using modernization-output-before/modernization-report.md, implement the safest high-impact fix.

Focus on: fixing unsafe SQL string concatenation in the legacy Spring Boot app.

Requirements:
1. Keep the change small and reviewable (one class or method).
2. Preserve existing behavior exactly.
3. Use PreparedStatement or Spring Data JPA repository pattern.
4. Add or update a focused unit test if practical.
5. Explain every file you change and why.
6. Give me the exact command to validate the fix.

Do NOT migrate the full Spring Boot version yet.
```

## Prompt 3: Add Focused Tests
```
Add focused tests for the component you just changed.

Requirements:
1. Cover the normal successful case.
2. Cover an invalid or malicious input case (SQL injection attempt).
3. Keep tests minimal and runnable with the existing test framework.
4. Explain clearly how each test proves the modernization improvement.
```

## Prompt 4: Improve the Analyzer
```
Review this modernization-navigator project itself.

Add improvements to the analyzer:
1. Add one new Spring Boot modernization detection rule.
2. Add one new security detection rule.
3. Add or update tests for both new rules.
4. Keep changes small and explain implementation + validation steps.

Good rule ideas:
- Detect csrf().disable() in security config
- Detect @CrossOrigin("*")
- Detect javax.servlet imports
- Detect JUnit 4 imports (org.junit.Test)
- Detect old maven-compiler-plugin source/target values
- Detect missing GitHub Actions CI
```

## Prompt 5: Generate Final Docs
```
Generate a hackathon-ready README section for this project.

Include:
1. Problem statement
2. Solution overview
3. IBM Bob's role in the workflow
4. Step-by-step workflow
5. How to run the analyzer
6. Before/after modernization results
7. Demo script for judges
8. Judging artifacts location
9. Limitations and next steps

Mention that Bob IDE was used to validate findings, implement fixes,
generate tests, and create documentation.
```

## Prompt 6: Judge Summary
```
Generate a concise judge summary from the modernization reports.

Make it easy for judges to understand:
1. What the agent does
2. Why it matters for enterprise software teams
3. How IBM Bob is central to the workflow
4. What changed after Bob-assisted implementation
5. Measurable improvement shown by before/after scans
```
"""
        (self.out / "bob-prompts.md").write_text(content, encoding="utf-8")

    # ── Judge Summary ──────────────────────────────────────────────────────

    def _write_judge_summary(self, result: ModernizationResult) -> None:
        p = result.profile
        critical = result.critical_count
        high = result.high_count
        total = len(result.findings)

        lines = [
            "# Judge Summary — Bob Modernization Navigator\n",
            "## What It Does",
            "Bob Modernization Navigator is a Python CLI agent that scans legacy Java/Spring Boot "
            "and Node.js repositories and generates actionable modernization reports. "
            "It integrates with IBM Bob IDE to implement fixes, add tests, and produce documentation.\n",
            "## Why It Matters",
            "Enterprise teams waste thousands of hours manually auditing legacy codebases. "
            "This agent automates the discovery phase and uses Bob to accelerate the fix phase — "
            "compressing a multi-sprint effort into a hackathon demo.\n",
            "## IBM Bob's Role",
            "| Stage | Bob Action |",
            "|---|---|",
            "| Analysis | Bob explains findings and recommends implementation order |",
            "| Implementation | Bob implements the safest high-impact fix |",
            "| Testing | Bob generates focused unit tests for changed components |",
            "| Documentation | Bob generates README, judge summary, and PR descriptions |\n",
            "## Scan Results\n",
            f"| Metric | Value |",
            f"|---|---|",
            f"| Project type | {p.project_type} |",
            f"| Total findings | **{total}** |",
            f"| Critical | 🔴 {critical} |",
            f"| High | 🟠 {high} |",
            f"| Tests present | {p.has_tests} |",
            f"| CI/CD configured | {p.has_ci} |\n",
            "## Demo Story",
            "1. Run the scanner — findings appear in seconds.",
            "2. Open Bob IDE — paste Prompt 1 to get the prioritized fix plan.",
            "3. Paste Prompt 2 — Bob implements the SQL injection fix.",
            "4. Paste Prompt 3 — Bob adds tests proving the fix.",
            "5. Re-run scanner — compare before/after finding counts.",
            "6. Export Bob task sessions → `bob_sessions/`\n",
        ]

        (self.out / "judge-summary.md").write_text("\n".join(lines), encoding="utf-8")

    # ── HTML Dashboard ─────────────────────────────────────────────────────

    def _write_dashboard(self, result: ModernizationResult) -> None:
        counts = {sev.value: 0 for sev in Severity}
        for f in result.findings:
            counts[f.severity.value] += 1

        rows = ""
        for f in result.findings_sorted:
            emoji = SEVERITY_EMOJI.get(f.severity, "")
            rows += (
                f"<tr class='sev-{f.severity.value}'>"
                f"<td>{emoji} {f.severity.value}</td>"
                f"<td>{f.category.value}</td>"
                f"<td>{f.title}</td>"
                f"<td><code>{f.file_path or 'N/A'}</code></td>"
                f"<td>{f.recommendation or 'N/A'}</td>"
                f"</tr>\n"
            )

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Modernization Dashboard</title>
<style>
  body {{ font-family: system-ui, sans-serif; margin: 2rem; background: #f8f9fa; color: #212529; }}
  h1 {{ color: #1a1a2e; }}
  .cards {{ display: flex; gap: 1rem; margin: 1.5rem 0; flex-wrap: wrap; }}
  .card {{ padding: 1.2rem 2rem; border-radius: 8px; color: #fff; min-width: 120px; text-align: center; }}
  .card .num {{ font-size: 2.5rem; font-weight: 700; }}
  .card .label {{ font-size: 0.85rem; opacity: 0.85; }}
  .critical {{ background: #dc3545; }} .high {{ background: #fd7e14; }}
  .medium {{ background: #ffc107; color: #212529; }} .low {{ background: #0d6efd; }}
  table {{ border-collapse: collapse; width: 100%; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,.1); }}
  th {{ background: #343a40; color: #fff; padding: .7rem 1rem; text-align: left; }}
  td {{ padding: .6rem 1rem; border-bottom: 1px solid #dee2e6; font-size: .9rem; }}
  tr:hover {{ background: #f1f3f5; }}
  .sev-critical td:first-child {{ color: #dc3545; font-weight: 600; }}
  .sev-high td:first-child {{ color: #fd7e14; font-weight: 600; }}
  .sev-medium td:first-child {{ color: #856404; font-weight: 600; }}
  code {{ background: #e9ecef; padding: 1px 4px; border-radius: 3px; font-size: .82rem; }}
</style>
</head>
<body>
<h1>🔍 Modernization Dashboard</h1>
<p>Repository: <code>{result.profile.repo_path}</code> &nbsp;|&nbsp;
   Type: <strong>{result.profile.project_type}</strong> &nbsp;|&nbsp;
   Total findings: <strong>{len(result.findings)}</strong></p>
<div class="cards">
  <div class="card critical"><div class="num">{counts['critical']}</div><div class="label">Critical</div></div>
  <div class="card high"><div class="num">{counts['high']}</div><div class="label">High</div></div>
  <div class="card medium"><div class="num">{counts['medium']}</div><div class="label">Medium</div></div>
  <div class="card low"><div class="num">{counts['low']}</div><div class="label">Low</div></div>
</div>
<table>
  <thead><tr><th>Severity</th><th>Category</th><th>Title</th><th>File</th><th>Recommendation</th></tr></thead>
  <tbody>{rows}</tbody>
</table>
</body>
</html>"""
        (self.out / "dashboard.html").write_text(html, encoding="utf-8")
