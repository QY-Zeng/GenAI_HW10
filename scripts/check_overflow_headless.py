#!/usr/bin/env python3
"""
Headless Chromium/Edge Layout & Overflow Verifier for deck.html.
Renders every slide at native 1280x720 in real browser engine and verifies:
- hOverflow == 0 (scrollHeight <= clientHeight)
- wOverflow == 0 (scrollWidth <= clientWidth)
- overlap == 0 (content never collides with .slide-source footer)
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BROWSERS = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
]


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python scripts/check_overflow_headless.py <topic_dir>")
        return 2

    deck = (ROOT / sys.argv[1] / "deck.html").resolve()
    if not deck.exists():
        print(f"[FAIL] Missing {deck}")
        return 1

    browser = next((b for b in BROWSERS if b.exists()), None)
    if browser is None:
        print("[WARN] No headless Chrome/Edge found.")
        return 2

    url = deck.as_uri() + "?audit=1"
    cmd = [
        str(browser),
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=1280,720",
        "--virtual-time-budget=2000",
        "--dump-dom",
        url,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    m = re.search(r'<pre id="audit-out"[^>]*>(.*?)</pre>', proc.stdout, flags=re.DOTALL)
    if not m:
        print("[FAIL] Could not extract #audit-out from headless DOM dump.")
        if proc.stderr:
            print(proc.stderr[:600])
        return 1

    rows = json.loads(m.group(1))
    failures = []
    for r in rows:
        status = "PASS" if (r["hOverflow"] <= 0 and r["wOverflow"] <= 0 and r["overlap"] <= 0) else "OVERFLOW"
        print(f"Slide {r['slide']:02d}: hOverflow={r['hOverflow']}px, wOverflow={r['wOverflow']}px, footerOverlap={r['overlap']}px [{status}]")
        if status != "PASS":
            failures.append(r)

    if failures:
        print(f"[FAIL] {len(failures)} slide(s) overflowed at 1280x720.")
        return 1

    print(f"[PASS] All {len(rows)} slides verified with 0px overflow and 0px footer overlap at 1280x720.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
