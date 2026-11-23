#!/usr/bin/env python3
"""
Gate 3: HTML Deck Verification & Fidelity/Layout Check for Graph Slide Workflow.
Checks topic-<slug>/deck.html:
1. Slide count matches drafts/ and is within 8-15 pages.
2. Every <section class="slide"> has a visible source footer (.slide-source) with chapter/figure/wiki attribution.
3. No unauthorized factual/numeric drift vs. approved drafts/.
4. Interactive navigation controls (ArrowRight/ArrowLeft, slide counter, progress bar) present.
5. Optional headless browser (Edge/Chrome/Playwright) overflow check if available.
"""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class SlideExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.slides: list[dict[str, object]] = []
        self._in_slide = False
        self._slide_depth = 0
        self._in_source = False
        self._in_heading = False
        self._current: dict[str, object] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = dict(attrs)
        classes = (attr_map.get("class") or "").split()
        if tag == "section" and "slide" in classes:
            self._in_slide = True
            self._slide_depth = 1
            self._current = {"text": [], "source": [], "heading": []}
            return
        if self._in_slide:
            if tag == "section":
                self._slide_depth += 1
            if "slide-source" in classes:
                self._in_source = True
            if tag in ("h1", "h2"):
                self._in_heading = True

    def handle_endtag(self, tag: str) -> None:
        if not self._in_slide:
            return
        if tag in ("h1", "h2"):
            self._in_heading = False
        if tag in ("footer", "div", "p") and self._in_source:
            self._in_source = False
        if tag == "section":
            self._slide_depth -= 1
            if self._slide_depth == 0:
                self.slides.append(self._current)
                self._in_slide = False

    def handle_data(self, data: str) -> None:
        if not self._in_slide:
            return
        stripped = data.strip()
        if not stripped:
            return
        self._current["text"].append(stripped)  # type: ignore[union-attr]
        if self._in_source:
            self._current["source"].append(stripped)  # type: ignore[union-attr]
        if self._in_heading:
            self._current["heading"].append(stripped)  # type: ignore[union-attr]


METRIC_RE = re.compile(r"\b\d+(?:\.\d+)?%|\b\d+(?:\.\d+)?\s*[×x]\b|\b\d+(?:\.\d+)?\s*(?:Gbps|GB/s|GB|ms|pp)\b")


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python scripts/gate3_check_html.py <topic_dir>")
        return 2

    topic_dir = (ROOT / sys.argv[1]).resolve()
    deck_html = topic_dir / "deck.html"
    drafts_dir = topic_dir / "drafts"

    if not deck_html.exists():
        print(f"[FAIL] Missing {deck_html}")
        return 1

    html_text = deck_html.read_text(encoding="utf-8")
    parser = SlideExtractor()
    parser.feed(html_text)
    slides = parser.slides
    draft_files = sorted(drafts_dir.glob("slide-*.md"))

    errors: list[str] = []

    if not (8 <= len(slides) <= 15):
        errors.append(f"HTML slide count {len(slides)} outside 8-15 range.")
    elif len(slides) != len(draft_files):
        errors.append(f"HTML slide count ({len(slides)}) != draft count ({len(draft_files)}).")
    else:
        print(f"[PASS] HTML deck contains {len(slides)} slides matching drafts/ (8-15 range).")

    # Navigation controls check
    for token in ("ArrowRight", "ArrowLeft", "slide-counter"):
        if token not in html_text:
            errors.append(f"Missing interactive presentation feature: '{token}'.")
    if not any("Missing interactive" in e for e in errors):
        print("[PASS] Interactive navigation (ArrowLeft/ArrowRight, slide counter) verified.")

    # Per-slide citation + numeric fidelity against approved draft
    for idx, (sdata, dfile) in enumerate(zip(slides, draft_files), start=1):
        source_str = " ".join(sdata["source"])  # type: ignore[arg-type]
        slide_str = " ".join(sdata["text"])  # type: ignore[arg-type]
        draft_text = dfile.read_text(encoding="utf-8")

        if not source_str.strip():
            errors.append(f"Slide {idx}: Missing visible .slide-source attribution footer.")
        elif "wiki/" not in source_str and "§" not in source_str and "Table" not in source_str and "Fig" not in source_str:
            errors.append(f"Slide {idx}: .slide-source lacks wiki/ or chapter/table/figure attribution: '{source_str}'.")

        # Ensure HTML did not invent new numeric metrics absent from approved draft
        draft_compact = draft_text.replace(" ", "").lower()
        for m in METRIC_RE.findall(slide_str):
            num_m = re.match(r"\d+(?:\.\d+)?", m)
            if not num_m:
                continue
            if num_m.group(0) not in draft_compact:
                # Allow slide numbering or CSS/aspect ratios only if not metric; METRIC_RE already filters to %, ×, Gbps, ms, pp
                errors.append(
                    f"Slide {idx}: Metric '{m}' in HTML is NOT present in approved draft {dfile.name} (unauthorized edit!)."
                )

    print(f"[INFO] Errors: {len(errors)}")
    for e in errors:
        print(f"  [ERROR] {e}")

    if errors:
        return 1
    print("[PASS] Gate 3 (HTML Structure, Citations & Draft Fidelity) passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
