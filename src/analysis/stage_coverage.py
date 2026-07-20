"""
Stage coverage (D44).

Computes per-stage coverage across the project:
  - in_code: Dxx is implemented in src/analysis/*.py
  - in_tests: Dxx has a test_*.py file
  - in_docs: Dxx is mentioned in README.md
  - in_memory: Dxx is mentioned in .workbuddy/memory/

Reports which stages are well-covered vs orphan.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional


_STAGE_ID_RE = re.compile(r"\bD(\d+)\b")
_ISO_DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})\.md$")


def _safe_read(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _parse_date(p: Path) -> Optional[object]:
    from datetime import date
    m = _ISO_DATE_RE.match(p.name)
    if not m:
        return None
    try:
        return date(int(m.group(1)), int(m.group(2)),
                    int(m.group(3)))
    except ValueError:
        return None


def _stages_in(text: str) -> list[str]:
    out: list[str] = []
    for line in text.splitlines():
        if line.startswith("##") and not line.startswith("###"):
            for sid in _STAGE_ID_RE.findall(line):
                out.append(f"D{sid}")
    return out


def _normalize_did(s: str) -> str:
    m = re.match(r"^D(\d+)$", s)
    if not m:
        return s
    n = int(m.group(1))
    return f"D{n:02d}" if n < 10 else f"D{n}"


@dataclass
class CoverageReport:
    n_stages: int
    n_project: int
    n_documented: int
    n_orphan: int
    n_missing: int
    details: dict

    def to_dict(self) -> dict:
        return {
            "n_stages": self.n_stages,
            "n_project": self.n_project,
            "n_documented": self.n_documented,
            "n_orphan": self.n_orphan,
            "n_missing": self.n_missing,
            "details": self.details,
        }


def build_coverage(project_root: Path) -> CoverageReport:
    src = project_root / "src" / "analysis"
    tests = project_root / "tests"
    readme = project_root / "README.md"
    memory_dir = project_root / ".workbuddy" / "memory"
    project_stages: set = set()
    if src.is_dir():
        for f in src.glob("*.py"):
            for s in _stages_in(_safe_read(f)):
                project_stages.add(_normalize_did(s))
    test_stages: set = set()
    if tests.is_dir():
        for f in tests.glob("test_*.py"):
            for s in _stages_in(_safe_read(f)):
                test_stages.add(_normalize_did(s))
    readme_stages: set = set()
    if readme.exists():
        for s in _stages_in(_safe_read(readme)):
            readme_stages.add(_normalize_did(s))
    mem_stages: set = set()
    if memory_dir.is_dir():
        for p in memory_dir.glob("*.md"):
            for s in _stages_in(_safe_read(p)):
                mem_stages.add(_normalize_did(s))
    all_stages = project_stages | test_stages | readme_stages | mem_stages
    documented = project_stages & test_stages
    orphan = (project_stages | test_stages | readme_stages) - mem_stages
    missing = (readme_stages | mem_stages) - project_stages
    return CoverageReport(
        n_stages=len(all_stages),
        n_project=len(project_stages),
        n_documented=len(documented),
        n_orphan=len(orphan),
        n_missing=len(missing),
        details={
            "project_stages": sorted(project_stages),
            "test_stages": sorted(test_stages),
            "readme_stages": sorted(readme_stages),
            "memory_stages": sorted(mem_stages),
            "documented": sorted(documented),
            "orphan": sorted(orphan),
            "missing": sorted(missing),
        },
    )


def render_markdown(report: CoverageReport) -> str:
    lines: list = ["# Stage Coverage", ""]
    lines.append(f"- **Total stages**: {report.n_stages}")
    lines.append(f"- **In project (src/)**: {report.n_project}")
    lines.append(f"- **Documented (project + tests)**: "
                  f"{report.n_documented}")
    lines.append(f"- **Orphan (no memory)**: {report.n_orphan}")
    lines.append(f"- **Missing (memory/docs but not in code)**: "
                  f"{report.n_missing}")
    lines.append("")
    lines.append("## Project stages")
    lines.append(", ".join(report.details["project_stages"]) or "(none)")
    lines.append("")
    lines.append("## Documented stages")
    lines.append(", ".join(report.details["documented"]) or "(none)")
    lines.append("")
    lines.append("## Orphan stages (no memory mention)")
    lines.append(", ".join(report.details["orphan"]) or "(none)")
    lines.append("")
    lines.append("## Missing stages (mentioned but not implemented)")
    lines.append(", ".join(report.details["missing"]) or "(none)")
    lines.append("")
    return "\n".join(lines)


def render_json(report: CoverageReport) -> dict:
    return {"report": report.to_dict()}


def main() -> int:
    p = argparse.ArgumentParser(description="Stage coverage report")
    p.add_argument("--project_root", type=Path, default=Path("."))
    p.add_argument("--out", type=Path,
                   default=Path("report/stage_coverage.md"))
    p.add_argument("--out_json", type=Path,
                   default=Path("report/stage_coverage.json"))
    args = p.parse_args()
    report = build_coverage(args.project_root)
    md = render_markdown(report)
    print(f"[coverage] project={report.n_project}; "
          f"doc={report.n_documented}; "
          f"orphan={report.n_orphan}; "
          f"missing={report.n_missing}")
    print(md)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(md, encoding="utf-8")
    print(f"Wrote Markdown -> {args.out}")
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(
        json.dumps(render_json(report), indent=2, ensure_ascii=False),
        encoding="utf-8")
    print(f"Wrote JSON     -> {args.out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
