#!/usr/bin/env python3
"""KV Cache Wiki 檢查器。

用法：
  python3 tools/check.py wiki              # Wiki lint（ingest 後執行）
  python3 tools/check.py slides FILE.html  # 簡報逐頁檢查（每頁 data-claims 要對得回帳本）

規則（對應 schema.md）：
  W1 概念頁引用的每個 [C##] 都必須存在於 claims.json
  W2 帳本每個 claim 都必須出現在某個 sources/ 或 concepts/ 頁面
  W3 概念頁引用 extract-only claim -> 警告（簡報不得使用）
  W4 概念頁內，帶數字的事實行必須有 [C##] 或 [S#] 標註
  S1 每張投影片必須有 data-claims（claim id 清單，或 "none" 代表純解說）
  S2 投影片不得引用 extract-only 或不存在的 claim
  S3 投影片文字中的每個數字，必須出現在它所引用 claim 的 numbers 清單中
     （class="nocheck" 的元素例外，用於頁碼與「示意用」的假想數字，且必須有文字標明是示意）
"""
import json, re, sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = {c["id"]: c for c in json.load(open(ROOT / "claims.json", encoding="utf-8"))["claims"]}
CID = re.compile(r"\[?C(\d{2})\]?")


def wiki():
    errors, warns = [], []
    pages = sorted((ROOT / "sources").glob("*.md")) + sorted((ROOT / "concepts").glob("*.md"))
    seen = set()
    for p in pages:
        text = p.read_text(encoding="utf-8")
        body = text.split("---", 2)[-1]
        for m in re.finditer(r"\[C(\d{2})\]", body):
            cid = "C" + m.group(1)
            seen.add(cid)
            if cid not in LEDGER:
                errors.append(f"W1 {p.name}: {cid} 不在帳本")
            elif LEDGER[cid]["status"] == "extract-only" and p.parent.name == "concepts":
                warns.append(f"W3 {p.name}: 引用 extract-only {cid}（簡報不得使用）")
        if p.parent.name == "concepts":
            for i, line in enumerate(body.splitlines(), 1):
                if re.search(r"\d", line) and line.lstrip().startswith(("-", "|")):
                    if not re.search(r"\[(C\d{2}|S\d)\]", line) and "解說" not in line and "只差大小寫" not in line:
                        warns.append(f"W4 {p.name}:{i} 含數字但無標註：{line.strip()[:60]}")
    for cid in LEDGER:
        if cid not in seen:
            errors.append(f"W2 {cid} 沒有出現在任何頁面")
    return errors, warns


class SlideParser(HTMLParser):
    VOID = {"br", "img", "hr", "meta", "link", "input"}

    def __init__(self):
        super().__init__()
        self.slides = []      # (index, claims_attr, text)
        self.stack = []       # (tag, is_nocheck)
        self.cur = None
        self.depth_slide = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = (a.get("class") or "").split()
        if tag in self.VOID:
            return
        if tag == "section" and "slide" in cls:
            self.cur = {"i": len(self.slides) + 1, "claims": a.get("data-claims"), "text": []}
            self.depth_slide = len(self.stack)
        nocheck = "nocheck" in cls
        self.stack.append((tag, nocheck))

    def handle_endtag(self, tag):
        if tag in self.VOID or not self.stack:
            return
        self.stack.pop()
        if self.cur is not None and len(self.stack) == self.depth_slide and tag == "section":
            self.slides.append(self.cur)
            self.cur = None

    def handle_data(self, data):
        if self.cur is None or any(nc for _, nc in self.stack):
            return
        if any(t in ("script", "style") for t, _ in self.stack):
            return
        self.cur["text"].append(data)


def numbers_in(text):
    return re.findall(r"\d+(?:[.,]\d+)*", text)


def slides(path):
    errors, warns = [], []
    html = Path(path).read_text(encoding="utf-8")
    ps = SlideParser()
    ps.feed(html)
    if not ps.slides:
        errors.append("S0 找不到任何 <section class=\"slide\">")
    for s in ps.slides:
        i, attr = s["i"], s["claims"]
        if attr is None:
            errors.append(f"S1 第 {i} 頁缺 data-claims")
            continue
        ids = [] if attr.strip() == "none" else [x.strip() for x in attr.split(",") if x.strip()]
        allowed = []
        for cid in ids:
            c = LEDGER.get(cid)
            if not c:
                errors.append(f"S2 第 {i} 頁引用不存在的 {cid}")
                continue
            if c["status"] == "extract-only":
                errors.append(f"S2 第 {i} 頁引用 extract-only 的 {cid}")
            allowed += c["numbers"]
        text = " ".join(s["text"])
        # 精確比對：把 claim 的 numbers 拆成數字 token（去掉逗號），投影片的每個數字 token 必須完全相等
        allowed_tokens = {t.replace(",", "") for a in allowed for t in numbers_in(a)}
        for n in numbers_in(text):
            if n.replace(",", "") not in allowed_tokens:
                errors.append(f"S3 第 {i} 頁數字 {n} 不在引用 claim 的 numbers 內（引用：{attr}）")
        if not ids and numbers_in(text):
            warns.append(f"S3 第 {i} 頁標為 none 但含數字，已逐一視為錯誤")
    return errors, warns, len(ps.slides)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "wiki"
    if mode == "wiki":
        e, w = wiki()
        n = "Wiki"
    else:
        e, w, k = slides(sys.argv[2])
        n = f"簡報（{k} 頁）"
    print(f"== {n} 檢查 ==")
    for x in w:
        print("WARN ", x)
    for x in e:
        print("ERROR", x)
    print(f"結果：{len(e)} 個錯誤、{len(w)} 個警告")
    sys.exit(1 if e else 0)
