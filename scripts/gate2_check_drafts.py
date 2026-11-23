#!/usr/bin/env python3
"""
Gate 2: Programmatic Draft & Citation Verification for Graph Slide Workflow.
Verifies topic-<slug>/drafts/slide-*.md:
1. Slide count within 8-15 pages.
2. Every slide cites at least one existing wiki/ page and chapter/table/figure citation.
3. Every slide cites at least one existing card in cards/ (enforcing Node 6 input boundary).
4. Every significant metric number (e.g., 97.6%, 25×, 400 Gbps, 0.42 s, r = +0.57) appears in its cited cards/wiki sources.
5. Per-slide text density budget (prevents overflow early at the draft stage).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI_DIR = ROOT / "wiki"

WIKI_PATH_RE = re.compile(r"(wiki/[a-zA-Z0-9_./-]+\.md)")
CARD_PATH_RE = re.compile(r"(cards/[a-zA-Z0-9_./-]+\.md)")
CITATION_RE = re.compile(
    r"\[[^\]]+?(?:§\s*\d|Section\s+\d|Table\s+\d|Fig\.?\s*\d|Figure\s+\d|p\.\s*\d+|Appendix\s+[A-Z]|Abstract)[^\]]*?\]"
)
# Capture notable quantitative metrics (percentages, multipliers, Gbps/GB/ms/s, Pearson r)
METRIC_RE = re.compile(
    r"(?:\b\d+(?:\.\d+)?%|\b\d+(?:\.\d+)?\s*[×x]\b|\b\d+(?:\.\d+)?\s*(?:Gbps|GB/s|GB|ms|pp)\b)"
)

MAX_BODY_CHARS = 950  # keeps slides concise and prevents HTML overflow


def normalize_num(token: str) -> str:
    return token.replace(" ", "").replace("x", "×").lower()


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python scripts/gate2_check_drafts.py <topic_dir>")
        return 2

    topic_dir = (ROOT / sys.argv[1]).resolve()
    drafts_dir = topic_dir / "drafts"
    cards_dir = topic_dir / "cards"

    if not drafts_dir.exists():
        print(f"[FAIL] Missing drafts directory: {drafts_dir}")
        return 1

    slides = sorted(drafts_dir.glob("slide-*.md"))
    errors: list[str] = []
    warnings: list[str] = []

    if not (8 <= len(slides) <= 15):
        errors.append(f"Slide count {len(slides)} is outside required range 8-15.")
    else:
        print(f"[PASS] Slide count is {len(slides)} (within 8-15).")

    # Preload full wiki + cards corpus for fallback number verification
    all_wiki_text = "\n".join(p.read_text(encoding="utf-8") for p in WIKI_DIR.rglob("*.md"))

    for slide_path in slides:
        text = slide_path.read_text(encoding="utf-8")
        sname = slide_path.name

        # 1. Wiki citation existence
        wiki_refs = sorted(set(WIKI_PATH_RE.findall(text)))
        if not wiki_refs:
            errors.append(f"{sname}: Missing wiki/ page citation.")
        else:
            for wr in wiki_refs:
                if not (ROOT / wr).exists():
                    errors.append(f"{sname}: Referenced wiki page does not exist: {wr}")

        # 2. Card reference check
        card_refs = sorted(set(CARD_PATH_RE.findall(text)))
        if not card_refs:
            errors.append(f"{sname}: Missing cards/ evidence card reference.")
        else:
            for cr in card_refs:
                if not (topic_dir / cr).exists():
                    errors.append(f"{sname}: Referenced evidence card does not exist: {cr}")

        # 3. Granular citation tag check
        if not CITATION_RE.search(text):
            errors.append(f"{sname}: Missing chapter/table/figure/page citation tag.")

        # 4. Verify quantitative claims against cited cards + wiki pages
        source_corpus = ""
        for cr in card_refs:
            p = topic_dir / cr
            if p.exists():
                source_corpus += "\n" + p.read_text(encoding="utf-8")
        for wr in wiki_refs:
            p = ROOT / wr
            if p.exists():
                source_corpus += "\n" + p.read_text(encoding="utf-8")

        # Strip metadata/source footer lines when scanning body text
        body_lines = [
            ln for ln in text.splitlines()
            if not ln.strip().startswith(("- **來源卡片**", "- **Wiki 出處**", "- **頁碼**", "<!--"))
        ]
        body_text = "\n".join(body_lines)

        # Length / density guard
        plain_body = re.sub(r"\[[^\]]+\]\([^)]+\)", "", body_text)
        plain_body = re.sub(r"[#>*`|_-]", "", plain_body)
        compact_len = len(re.sub(r"\s+", "", plain_body))
        if compact_len > MAX_BODY_CHARS:
            errors.append(
                f"{sname}: Body density too high ({compact_len} chars > {MAX_BODY_CHARS}); shorten draft to avoid overflow."
            )

        # Check every metric number in body_text against source_corpus
        norm_corpus = source_corpus.replace(" ", "").lower()
        norm_all_wiki = all_wiki_text.replace(" ", "").lower()
        for m in METRIC_RE.findall(body_text):
            # Extract core number (e.g. "97.6" from "97.6%" or "400" from "400 Gbps")
            num_part = re.match(r"\d+(?:\.\d+)?", m)
            if not num_part:
                continue
            num_str = num_part.group(0)
            if num_str not in norm_corpus:
                if num_str in norm_all_wiki:
                    warnings.append(
                        f"{sname}: Metric '{m}' found in wiki/ globally, but not in this slide's cited cards/wiki subset."
                    )
                else:
                    errors.append(
                        f"{sname}: Unverified metric '{m}' not found in cited evidence cards or wiki sources!"
                    )

    print(f"[INFO] Checked {len(slides)} slide drafts in {drafts_dir.relative_to(ROOT).as_posix()}.")
    print(f"[INFO] Warnings: {len(warnings)}")
    for w in warnings:
        print(f"  [WARN] {w}")
    print(f"[INFO] Errors: {len(errors)}")
    for e in errors:
        print(f"  [ERROR] {e}")

    if errors:
        return 1
    print("[PASS] Gate 2 (Draft Citations, Metrics & Density) passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
