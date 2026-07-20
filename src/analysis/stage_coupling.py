"""
Stage coupling (D53).

Reads `.workbuddy/memory/YYYY-MM-DD.md` and computes the
cross-cluster coupling of stages: given the clusters from D51,
how many of the pair co-occurrences cross cluster boundaries?

Provides:
  - per-cluster stats (size, internal_edges, density)
  - cross-cluster edges
  - modularity score = 1 - (cross / total)
  - top 10 cross-cluster pairs
"""

from __future__ import annotations

import argparse
import json
import re
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from itertools import combinations
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


def collect_file_stages(memory_dir: Path) -> list:
    if not memory_dir.is_dir():
        return []
    out: list = []
    for p in memory_dir.glob("*.md"):
        stages = _stages_in(_safe_read(p))
        if stages:
            out.append(sorted(set(stages)))
    return out


def build_pair_counts(file_stages: list) -> dict:
    pair_counts: dict = defaultdict(int)
    for stages in file_stages:
        for a, b in combinations(stages, 2):
            pair_counts[frozenset({a, b})] += 1
    return pair_counts


def greedy_cluster(pair_counts: dict, all_stages: set) -> list:
    sorted_pairs = sorted(pair_counts.items(), key=lambda x: -x[1])
    stage_to_cluster: dict = {}
    clusters: list = []
    for pair, _c in sorted_pairs:
        a, b = list(pair)
        ca = stage_to_cluster.get(a)
        cb = stage_to_cluster.get(b)
        if ca is None and cb is None:
            new_id = len(clusters)
            clusters.append({a, b})
            stage_to_cluster[a] = new_id
            stage_to_cluster[b] = new_id
        elif ca is None and cb is not None:
            clusters[cb].add(a)
            stage_to_cluster[a] = cb
        elif ca is not None and cb is None:
            clusters[ca].add(b)
            stage_to_cluster[b] = ca
        else:
            if ca == cb:
                continue
            target, source = (ca, cb) if ca < cb else (cb, ca)
            for s in clusters[source]:
                stage_to_cluster[s] = target
            clusters[target].update(clusters[source])
            clusters[source] = set()
    for s in all_stages:
        if s not in stage_to_cluster:
            new_id = len(clusters)
            clusters.append({s})
            stage_to_cluster[s] = new_id
    return [c for c in clusters if c]


@dataclass
class ClusterCoupling:
    cid_a: int
    cid_b: int
    n_cross_edges: int
    sample_pairs: list


@dataclass
class CouplingReport:
    n_clusters: int
    n_total_edges: int
    n_internal_edges: int
    n_cross_edges: int
    modularity: float
    top_cross: list

    def to_dict(self) -> dict:
        return {
            "n_clusters": self.n_clusters,
            "n_total_edges": self.n_total_edges,
            "n_internal_edges": self.n_internal_edges,
            "n_cross_edges": self.n_cross_edges,
            "modularity": self.modularity,
            "top_cross": [asdict(c) for c in self.top_cross],
        }


def count_internal_edges(cluster: set, pair_counts: dict) -> int:
    total = 0
    for a, b in combinations(sorted(cluster), 2):
        total += pair_counts.get(frozenset({a, b}), 0)
    return total


def build_coupling(pair_counts: dict, clusters: list) -> CouplingReport:
    n_total = sum(pair_counts.values())
    stage_to_cid = {s: i for i, c in enumerate(clusters) for s in c}
    n_internal = 0
    n_cross = 0
    cross_pairs: dict = defaultdict(list)
    for pair, c in pair_counts.items():
        a, b = list(pair)
        ca = stage_to_cid.get(a)
        cb = stage_to_cid.get(b)
        if ca is None or cb is None:
            continue
        if ca == cb:
            n_internal += c
        else:
            n_cross += c
            lo, hi = (ca, cb) if ca < cb else (cb, ca)
            if len(cross_pairs[(lo, hi)]) < 3:
                cross_pairs[(lo, hi)].append((a, b, c))
    cross_sorted = sorted(cross_pairs.items(),
                            key=lambda x: -sum(p[2] for p in x[1]))
    top_cross: list = []
    for (ca, cb), pairs in cross_sorted[:10]:
        n = sum(p[2] for p in pairs)
        top_cross.append(ClusterCoupling(
            cid_a=ca, cid_b=cb, n_cross_edges=n,
            sample_pairs=pairs,
        ))
    modularity = 1 - (n_cross / n_total) if n_total else 1.0
    return CouplingReport(
        n_clusters=len(clusters),
        n_total_edges=n_total,
        n_internal_edges=n_internal,
        n_cross_edges=n_cross,
        modularity=modularity,
        top_cross=top_cross,
    )


def render_markdown(report: CouplingReport, cluster_stats: list) -> str:
    out: list[str] = ["# Stage Coupling", ""]
    out.append(f"*Generated by `src.analysis.stage_coupling` on "
                f"{time.strftime('%Y-%m-%d %H:%M:%S')}*\n")
    if report.n_total_edges == 0:
        out.append("*(no data)*\n")
        return "\n".join(out)
    out.append("## Summary\n")
    out.append(f"- **Clusters**: {report.n_clusters}")
    out.append(f"- **Total pair-edges**: {report.n_total_edges}")
    out.append(f"- **Internal edges**: {report.n_internal_edges}")
    out.append(f"- **Cross-cluster edges**: {report.n_cross_edges}")
    out.append(f"- **Modularity** (1 - cross/total): "
                f"{report.modularity:.2%}")
    out.append("")
    out.append("## Per-cluster stats\n")
    out.append("| cluster | size | internal_edges | density |")
    out.append("|---|---|---|---|")
    for cid, size, iedges, dens in cluster_stats:
        out.append(f"| C{cid:02d} | {size} | {iedges} | "
                    f"{dens:.2%} |")
    out.append("")
    if report.top_cross:
        out.append("## Top 10 cross-cluster edges\n")
        out.append("| pair | edges | sample stages |")
        out.append("|---|---|---|")
        for c in report.top_cross:
            sample = ", ".join(
                f"{a}<->{b}({n})" for a, b, n in c.sample_pairs)
            out.append(f"| {c.cid_a:02d} <-> {c.cid_b:02d} | "
                        f"{c.n_cross_edges} | {sample} |")
        out.append("")
    return "\n".join(out)


def render_json(report: CouplingReport) -> dict:
    return {"report": report.to_dict()}


def main() -> int:
    p = argparse.ArgumentParser(
        description="Stage cross-cluster coupling")
    p.add_argument("--memory_dir", type=Path,
                   default=Path("../.workbuddy/memory"))
    p.add_argument("--out", type=Path,
                   default=Path("report/stage_coupling.md"))
    p.add_argument("--out_json", type=Path,
                   default=Path("report/stage_coupling.json"))
    args = p.parse_args()
    file_stages = collect_file_stages(args.memory_dir)
    all_stages = {s for fs in file_stages for s in fs}
    pair_counts = build_pair_counts(file_stages)
    clusters = greedy_cluster(pair_counts, all_stages)
    report = build_coupling(pair_counts, clusters)
    cluster_stats: list = []
    for cid, c in enumerate(clusters):
        n = len(c)
        n_int = count_internal_edges(c, pair_counts) if n > 1 else 0
        dens = (2 * n_int / (n * (n - 1))) if n > 1 else 0.0
        cluster_stats.append((cid, n, n_int, dens))
    cluster_stats.sort(key=lambda x: -x[1])
    md = render_markdown(report, cluster_stats=cluster_stats)
    print(f"[coupling] {report.n_clusters} clusters; "
          f"modularity={report.modularity:.2%} "
          f"(internal={report.n_internal_edges}, "
          f"cross={report.n_cross_edges})")
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
