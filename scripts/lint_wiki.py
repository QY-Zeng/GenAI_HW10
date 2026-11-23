#!/usr/bin/env python3
"""
LLM Wiki Research-Quality Lint Script.
Enforces all rules defined in AGENTS.md so that "done" is verified by code, not AI intuition.
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI_DIR = ROOT / "wiki"
RAW_DIR = ROOT / "raw"
AGENTS_MD = ROOT / "AGENTS.md"
GEMINI_MD = ROOT / "GEMINI.md"
CLAUDE_MD = ROOT / "CLAUDE.md"
INDEX_MD = WIKI_DIR / "index.md"
LOG_MD = WIKI_DIR / "log.md"
CONFLICTS_MD = WIKI_DIR / "syntheses" / "conflicts-and-tensions.md"

MAX_AGENTS_CHARS = 12000
REQUIRED_FM_KEYS = {"title", "type", "sources", "updated"}
CITATION_RE = re.compile(
    r"\[[^\]]+?(?:§\s*\d|Section\s+\d|Table\s+\d|Fig\.?\s*\d|Figure\s+\d|p\.\s*\d+|Appendix\s+[A-Z])[^\]]*?\]"
)
MD_LINK_RE = re.compile(r"!?\[([^\]]*)\]\(([^)]+)\)")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def parse_frontmatter(text: str) -> dict[str, object] | None:
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        return None
    parts = re.split(r"^---\s*$", text, maxsplit=2, flags=re.MULTILINE)
    if len(parts) < 3:
        return None
    fm_block = parts[1].strip()
    data: dict[str, object] = {}
    current_key: str | None = None
    for line in fm_block.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if re.match(r"^\s*-\s+", line) and current_key:
            val = re.sub(r"^\s*-\s+", "", line).strip().strip('"').strip("'")
            if not isinstance(data.get(current_key), list):
                data[current_key] = []
            data[current_key].append(val)  # type: ignore[union-attr]
        elif ":" in line:
            k, v = line.split(":", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            current_key = k
            if v == "":
                data[k] = []
            elif v.startswith("[") and v.endswith("]"):
                inner = v[1:-1].strip()
                data[k] = [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()]
            else:
                data[k] = v
    return data


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    checks_passed = 0

    # 1. Rule file governance
    if not AGENTS_MD.exists():
        errors.append("Missing AGENTS.md at project root.")
    else:
        agents_text = AGENTS_MD.read_text(encoding="utf-8")
        char_len = len(agents_text)
        if char_len > MAX_AGENTS_CHARS:
            errors.append(f"AGENTS.md length ({char_len} chars) exceeds Antigravity limit ({MAX_AGENTS_CHARS}).")
        else:
            checks_passed += 1
            print(f"[PASS] AGENTS.md exists and is {char_len}/{MAX_AGENTS_CHARS} chars.")

    if GEMINI_MD.exists():
        errors.append("GEMINI.md exists alongside AGENTS.md (rule conflict risk).")
    else:
        checks_passed += 1
        print("[PASS] No conflicting GEMINI.md found.")

    if not CLAUDE_MD.exists():
        errors.append("Missing CLAUDE.md shim.")
    elif "@AGENTS.md" not in CLAUDE_MD.read_text(encoding="utf-8"):
        errors.append("CLAUDE.md does not reference @AGENTS.md.")
    else:
        checks_passed += 1
        print("[PASS] CLAUDE.md correctly delegates to @AGENTS.md.")

    # 2. raw/ read-only integrity check
    manifest_path = RAW_DIR / "MANIFEST.sha256"
    raw_files = sorted(
        p for p in RAW_DIR.glob("*") if p.is_file() and p.name != "MANIFEST.sha256"
    )
    if not manifest_path.exists():
        warnings.append("raw/MANIFEST.sha256 not yet generated.")
    else:
        recorded: dict[str, str] = {}
        for line in manifest_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            digest, fname = line.split("  ", 1)
            recorded[fname] = digest
        manifest_ok = True
        for rf in raw_files:
            actual = sha256_file(rf)
            if rf.name not in recorded:
                errors.append(f"raw/{rf.name} is missing from raw/MANIFEST.sha256.")
                manifest_ok = False
            elif recorded[rf.name] != actual:
                errors.append(f"raw/{rf.name} checksum mismatch (read-only boundary violated).")
                manifest_ok = False
        for fname in recorded:
            if not (RAW_DIR / fname).exists():
                errors.append(f"raw/{fname} listed in MANIFEST.sha256 is missing on disk.")
                manifest_ok = False
        if manifest_ok and recorded:
            checks_passed += 1
            print(f"[PASS] raw/ read-only SHA-256 manifest verified ({len(recorded)} source files).")

    # 3. Collect all wiki markdown files
    wiki_files = sorted(WIKI_DIR.rglob("*.md"))
    content_files = [
        p for p in wiki_files if p not in (INDEX_MD, LOG_MD)
    ]

    # Track incoming links (normalized absolute paths)
    incoming_links: dict[Path, set[Path]] = {p.resolve(): set() for p in wiki_files}
    conflict_pages: list[Path] = []
    broken_links: list[str] = []

    for wf in wiki_files:
        rel = wf.relative_to(ROOT).as_posix()
        text = wf.read_text(encoding="utf-8")

        # Frontmatter check
        fm = parse_frontmatter(text)
        if fm is None:
            errors.append(f"{rel}: Missing YAML frontmatter.")
        else:
            missing_keys = REQUIRED_FM_KEYS - set(fm.keys())
            if missing_keys:
                errors.append(f"{rel}: Frontmatter missing keys: {sorted(missing_keys)}.")
            sources = fm.get("sources")
            if isinstance(sources, list):
                for src in sources:
                    if src == "none":
                        continue
                    src_path = (ROOT / src).resolve()
                    if not src_path.exists():
                        errors.append(f"{rel}: Frontmatter source '{src}' does not exist.")

        # Citation granularity check on content pages
        if wf in content_files:
            if not CITATION_RE.search(text):
                errors.append(
                    f"{rel}: Missing chapter/table/figure/page-level citation (e.g., [Paper, §X, Table Y, p.Z])."
                )

        # Paper pages must reference a raw/ source file
        if wf.parent == WIKI_DIR / "papers":
            has_raw_link = False
            for _, target in MD_LINK_RE.findall(text):
                clean_target = target.split("#", 1)[0].strip()
                if clean_target and "raw/" in clean_target:
                    resolved = (wf.parent / clean_target).resolve()
                    if resolved.exists():
                        has_raw_link = True
            if not has_raw_link:
                errors.append(f"{rel}: Paper note must link to its corresponding file in raw/.")

        # Link integrity check
        for _, target in MD_LINK_RE.findall(text):
            target = target.strip()
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            clean_target = target.split("#", 1)[0]
            if not clean_target:
                continue
            resolved = (wf.parent / clean_target).resolve()
            if not resolved.exists():
                broken_links.append(f"{rel} -> {target}")
            elif resolved in incoming_links and resolved != wf.resolve():
                incoming_links[resolved].add(wf.resolve())

        # Conflict / tension marker tracking
        if "跨文獻張力" in text and wf != CONFLICTS_MD:
            conflict_pages.append(wf)

    if broken_links:
        for bl in broken_links:
            errors.append(f"Broken internal link: {bl}")
    else:
        checks_passed += 1
        print(f"[PASS] Zero broken links across {len(wiki_files)} wiki pages.")

    # 4. Index & Log synchronization and orphan detection
    if not INDEX_MD.exists():
        errors.append("Missing wiki/index.md.")
    else:
        index_text = INDEX_MD.read_text(encoding="utf-8")
        index_targets: set[Path] = set()
        for _, target in MD_LINK_RE.findall(index_text):
            clean = target.split("#", 1)[0].strip()
            if clean and not clean.startswith(("http://", "https://", "#")):
                index_targets.add((INDEX_MD.parent / clean).resolve())

        missing_from_index = [
            cf.relative_to(ROOT).as_posix()
            for cf in content_files
            if cf.resolve() not in index_targets
        ]
        if missing_from_index:
            errors.append(f"Pages missing from wiki/index.md: {missing_from_index}")
        else:
            checks_passed += 1
            print(f"[PASS] wiki/index.md is synchronized with all {len(content_files)} content pages.")

    # Orphan check (must have at least 1 incoming link from a page OTHER than index.md/log.md, or at least index.md + 1 peer)
    orphans: list[str] = []
    for cf in content_files:
        peers = {
            src for src in incoming_links[cf.resolve()]
            if src not in (INDEX_MD.resolve(), LOG_MD.resolve())
        }
        if not peers and len(content_files) > 1:
            orphans.append(cf.relative_to(ROOT).as_posix())
    if orphans:
        errors.append(f"Orphan pages with no peer cross-links: {orphans}")
    elif content_files:
        checks_passed += 1
        print(f"[PASS] Zero orphan pages (all {len(content_files)} content pages have peer incoming links).")

    # Log sync check
    if not LOG_MD.exists():
        errors.append("Missing wiki/log.md.")
    else:
        log_text = LOG_MD.read_text(encoding="utf-8")
        paper_files = sorted((WIKI_DIR / "papers").glob("*.md"))
        missing_in_log = [
            pf.name for pf in paper_files if pf.stem not in log_text and pf.name not in log_text
        ]
        if missing_in_log:
            errors.append(f"Papers not recorded in wiki/log.md: {missing_in_log}")
        else:
            checks_passed += 1
            print(f"[PASS] wiki/log.md records all {len(paper_files)} ingested papers.")

    # 5. Cross-paper conflict consolidation check
    if conflict_pages:
        if not CONFLICTS_MD.exists():
            errors.append(
                f"Conflict markers found in {[p.name for p in conflict_pages]}, but {CONFLICTS_MD.relative_to(ROOT)} does not exist."
            )
        else:
            conflicts_text = CONFLICTS_MD.read_text(encoding="utf-8")
            untracked = [
                p.name for p in conflict_pages
                if p.name not in conflicts_text and p.stem not in conflicts_text
            ]
            if untracked:
                errors.append(
                    f"Pages with conflict markers not cross-referenced in conflicts-and-tensions.md: {untracked}"
                )
            else:
                checks_passed += 1
                print(
                    f"[PASS] All {len(conflict_pages)} pages with cross-paper tensions are consolidated in syntheses/conflicts-and-tensions.md."
                )

    print("\n--- Lint Summary ---")
    print(f"Checks passed: {checks_passed}")
    print(f"Warnings: {len(warnings)}")
    for w in warnings:
        print(f"  [WARN] {w}")
    print(f"Errors: {len(errors)}")
    for e in errors:
        print(f"  [ERROR] {e}")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
