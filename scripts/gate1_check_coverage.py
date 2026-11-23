#!/usr/bin/env python3
"""
Gate 1: Coverage Check for Graph Slide Workflow.
Checks topic-<slug>/sources.md:
- At least 3 valid wiki/ pages referenced (stop-condition from lecture slide p.41/43)
- Strictly stays inside wiki/ knowledge boundary
- Verifies paper coverage when multiple papers exist in wiki/papers/
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI_DIR = ROOT / "wiki"
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
PATH_RE = re.compile(r"`(wiki/[a-zA-Z0-9_./-]+\.md)`")


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python scripts/gate1_check_coverage.py <topic_dir>")
        return 2

    topic_dir = (ROOT / sys.argv[1]).resolve()
    sources_md = topic_dir / "sources.md"
    if not sources_md.exists():
        print(f"[FAIL] Missing {sources_md}")
        return 1

    text = sources_md.read_text(encoding="utf-8")
    referenced: set[Path] = set()
    outside_wiki: list[str] = []

    for _, target in LINK_RE.findall(text):
        target = target.split("#", 1)[0].strip()
        if not target or target.startswith(("http://", "https://")):
            if target.startswith(("http://", "https://")):
                outside_wiki.append(target)
            continue
        resolved = (sources_md.parent / target).resolve()
        if resolved.exists():
            if WIKI_DIR.resolve() in resolved.parents:
                referenced.add(resolved)
            else:
                outside_wiki.append(target)
        else:
            print(f"[FAIL] Broken source link in sources.md: {target}")
            return 1

    for match in PATH_RE.findall(text):
        resolved = (ROOT / match).resolve()
        if resolved.exists() and WIKI_DIR.resolve() in resolved.parents:
            referenced.add(resolved)

    errors: list[str] = []
    if outside_wiki:
        errors.append(f"Knowledge boundary violation (external/non-wiki sources): {outside_wiki}")
    if len(referenced) < 3:
        errors.append(f"Insufficient coverage: only {len(referenced)} wiki pages found (minimum 3 required -> STOP).")

    all_papers = sorted((WIKI_DIR / "papers").glob("*.md"))
    covered_papers = [p for p in all_papers if p.resolve() in referenced]
    if len(all_papers) >= 3 and len(covered_papers) < len(all_papers):
        missing = [p.name for p in all_papers if p not in covered_papers]
        errors.append(f"Not all wiki papers covered in sources.md; missing: {missing}")

    print(f"[INFO] Valid wiki/ pages in sources.md: {len(referenced)}")
    print(f"[INFO] Papers covered: {len(covered_papers)}/{len(all_papers)}")
    if errors:
        for e in errors:
            print(f"[FAIL] {e}")
        return 1

    print("[PASS] Gate 1 (Coverage & Knowledge Boundary) passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
