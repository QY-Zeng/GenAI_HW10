#!/usr/bin/env python3
"""把 Wiki 的所有 Markdown 與 claims.json 打包成單一 HTML（site/wiki.html）。"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
deck_url = sys.argv[1] if len(sys.argv) > 1 else ""

files = [
    ("index", "index.md"), ("schema", "schema.md"),
    ("kv-cache", "concepts/kv-cache.md"), ("memory-and-paging", "concepts/memory-and-paging.md"),
    ("prefix-caching", "concepts/prefix-caching.md"), ("non-prefix-reuse", "concepts/non-prefix-reuse.md"),
    ("api-prompt-caching", "concepts/api-prompt-caching.md"), ("terminology", "concepts/terminology.md"),
    ("s1-pagedattention-vllm", "sources/s1-pagedattention-vllm.md"), ("s2-sglang-radixattention", "sources/s2-sglang-radixattention.md"),
    ("s3-prompt-cache", "sources/s3-prompt-cache.md"), ("s4-cacheblend", "sources/s4-cacheblend.md"),
    ("s5-anthropic-prompt-caching", "sources/s5-anthropic-prompt-caching.md"), ("s6-vllm-automatic-prefix-caching", "sources/s6-vllm-automatic-prefix-caching.md"),
    ("conflicts", "lint/conflicts.md"), ("log", "log.md"), ("graph", "logs/graph.md"), ("run-001", "logs/run-001.md"),
]
TITLES = {
    "index": "首頁", "schema": "Schema（規則）", "kv-cache": "KV cache", "memory-and-paging": "記憶體與 PagedAttention",
    "prefix-caching": "Prefix caching", "non-prefix-reuse": "非 prefix 重用", "api-prompt-caching": "API 的 prompt caching",
    "terminology": "術語表", "s1-pagedattention-vllm": "S1 PagedAttention", "s2-sglang-radixattention": "S2 SGLang",
    "s3-prompt-cache": "S3 Prompt Cache", "s4-cacheblend": "S4 CacheBlend", "s5-anthropic-prompt-caching": "S5 Anthropic 文件",
    "s6-vllm-automatic-prefix-caching": "S6 vLLM APC", "conflicts": "衝突紀錄", "log": "Ingest 紀錄",
    "graph": "Loop / graph 設計", "run-001": "執行紀錄與反思",
}
pages = {}
for pid, rel in files:
    text = (ROOT / rel).read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    front, body = (m.group(1), m.group(2)) if m else ("", text)
    desc = re.search(r"^description:\s*(.*)$", front, re.M)
    pages[pid] = {"title": TITLES[pid], "path": rel, "desc": desc.group(1).strip() if desc else "", "md": body.strip()}

claims = json.load(open(ROOT / "claims.json", encoding="utf-8"))["claims"]
groups = [
    {"title": "開始", "ids": ["index", "schema"]},
    {"title": "概念頁", "ids": ["kv-cache", "memory-and-paging", "prefix-caching", "non-prefix-reuse", "api-prompt-caching", "terminology"]},
    {"title": "來源頁", "ids": [i for i, _ in files if i.startswith("s") and i[1].isdigit()]},
    {"title": "品質控管", "ids": ["claims", "conflicts", "log"]},
    {"title": "流程與反思", "ids": ["graph", "run-001"]},
]
src_map = {f"S{i}": pid for pid, _ in files for i in range(1, 7) if pid.startswith(f"s{i}-")}
pages_for_nav = dict(pages); pages_for_nav["claims"] = {"title": "主張帳本", "path": "claims.json", "desc": "", "md": ""}
data = {"pages": pages_for_nav, "order": [i for i, _ in files], "groups": groups, "claims": claims, "srcMap": src_map}
blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")

tpl = (ROOT / "tools" / "wiki.template.html").read_text(encoding="utf-8")
out = tpl.replace("__DATA__", blob).replace("__DECK_URL__", deck_url)
(ROOT / "site" / "wiki.html").write_text(out, encoding="utf-8")
print("wrote site/wiki.html", len(out), "bytes;", len(pages), "pages;", len(claims), "claims")
