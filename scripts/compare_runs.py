"""
compare_runs.py — Compares two modernization scan outputs (before/after).

Usage:
  python scripts/compare_runs.py modernization-output-before modernization-output-after
"""

import re
import sys
from pathlib import Path


def extract_counts(report_path: Path) -> dict:
    """Parse a modernization-report.md and extract severity counts."""
    if not report_path.exists():
        return {}
    content = report_path.read_text(encoding="utf-8")
    counts = {}
    for severity in ("critical", "high", "medium", "low"):
        # Look for table rows like "| 🔴 Critical | 3 |"
        m = re.search(rf"\|\s*.*{severity}.*\|\s*(\d+)\s*\|", content, re.IGNORECASE)
        counts[severity] = int(m.group(1)) if m else 0
    return counts


def main():
    if len(sys.argv) != 3:
        print("Usage: python scripts/compare_runs.py <before-dir> <after-dir>")
        sys.exit(1)

    before_dir = Path(sys.argv[1])
    after_dir = Path(sys.argv[2])

    before = extract_counts(before_dir / "modernization-report.md")
    after = extract_counts(after_dir / "modernization-report.md")

    if not before:
        print(f"❌ Could not read before report from: {before_dir}")
        sys.exit(1)
    if not after:
        print(f"❌ Could not read after report from: {after_dir}")
        sys.exit(1)

    print("\n╔══════════════════════════════════════════════════════╗")
    print("║         Modernization — Before vs After              ║")
    print("╠══════════════════╦══════════╦══════════╦════════════╣")
    print("║ Severity         ║  Before  ║  After   ║  Δ Change  ║")
    print("╠══════════════════╬══════════╬══════════╬════════════╣")

    total_before, total_after = 0, 0
    for sev in ("critical", "high", "medium", "low"):
        b = before.get(sev, 0)
        a = after.get(sev, 0)
        delta = a - b
        arrow = f"▼ {abs(delta)}" if delta < 0 else (f"▲ {delta}" if delta > 0 else "—")
        total_before += b
        total_after += a
        print(f"║ {sev.capitalize():<16} ║ {b:>8} ║ {a:>8} ║ {arrow:>10} ║")

    print("╠══════════════════╬══════════╬══════════╬════════════╣")
    total_delta = total_after - total_before
    arrow = f"▼ {abs(total_delta)}" if total_delta < 0 else (f"▲ {total_delta}" if total_delta > 0 else "—")
    print(f"║ {'TOTAL':<16} ║ {total_before:>8} ║ {total_after:>8} ║ {arrow:>10} ║")
    print("╚══════════════════╩══════════╩══════════╩════════════╝\n")

    if total_delta < 0:
        pct = round(abs(total_delta) / total_before * 100) if total_before else 0
        print(f"✅ Improvement: {abs(total_delta)} findings resolved ({pct}% reduction)\n")
    elif total_delta == 0:
        print("⚠️  No change in finding count between runs.\n")
    else:
        print(f"❌ Finding count increased by {total_delta}. Review new findings.\n")


if __name__ == "__main__":
    main()
