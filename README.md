# GenAI_HW10 — KV Cache Reuse LLM Wiki 與教學 HTML 簡報

本專案依據課程第 10 單元《把你的工作拆成 AI 能做的流程：Loop、Graph 與 Workflow Prototype》，以「**先討論、後生成**」建立 **KV Cache Reuse（KV 快取重用）** 主題的 LLM Wiki（收錄 5 篇核心論文），並透過 **10 關 Graph Workflow**（含可執行腳本關卡、獨立唯讀子代理審查與無頭 Chrome 溢出驗證）產出可實際瀏覽的 12 頁互動式教學 HTML 簡報。

## 快速導覽
- 🎞️ **教學型 HTML 簡報（線上預覽）**：[點此開啟 GitHub Pages 簡報](https://qy-zeng.github.io/GenAI_HW10/topic-kv-cache-reuse/deck.html)（或開啟 [topic-kv-cache-reuse/deck.html](topic-kv-cache-reuse/deck.html)）
  - 支援鍵盤 `←` / `→` / `Space` 翻頁、`G` 鍵網格總覽與列印匯出 PDF。
- 📚 **LLM Wiki 知識庫入口**：
  - 員工手冊（規則檔，3,231／12,000 字元）：[AGENTS.md](AGENTS.md)（[CLAUDE.md](CLAUDE.md) 透過 `@AGENTS.md` 共用）
  - 目錄索引與領域總覽：[wiki/index.md](wiki/index.md) ｜ [wiki/overview.md](wiki/overview.md) ｜ [wiki/log.md](wiki/log.md)
  - 跨論文對照與張力彙整：[wiki/syntheses/kv-reuse-landscape.md](wiki/syntheses/kv-reuse-landscape.md) ｜ [wiki/syntheses/conflicts-and-tensions.md](wiki/syntheses/conflicts-and-tensions.md)
- 🔁 **Graph Workflow 與驗證報告**：
  - Workflow 規格：[.agents/workflows/topic-slides.md](.agents/workflows/topic-slides.md)
  - 交件檢查總報告：[topic-kv-cache-reuse/report.md](topic-kv-cache-reuse/report.md)
  - 獨立子代理忠實度審查紀錄：[topic-kv-cache-reuse/fidelity_review.md](topic-kv-cache-reuse/fidelity_review.md)

## 收錄之 5 篇核心論文（依技術演進順序逐篇 Ingest）
1. **CacheBlend**（`arXiv:2405.16444v3`, EuroSys '25）— [筆記](wiki/papers/cacheblend.md)
2. **DroidSpeak**（`arXiv:2411.02820v3`, 2024／NSDI '26）— [筆記](wiki/papers/droidspeak.md)
3. **LMCache**（`arXiv:2510.09665v2`, 2025）— [筆記](wiki/papers/lmcache.md)
4. **RelayCaching**（`arXiv:2603.13289v1`, 2026）— [筆記](wiki/papers/relaycaching.md)
5. **Cross-Model KV Cache Transfer**（`arXiv:2608.03893v1`, NVIDIA, 2026）— [筆記](wiki/papers/cross-model-kv-transfer.md)

## 可執行驗證腳本（`scripts/`）
```bash
python scripts/lint_wiki.py                                      # Wiki 健康度與 SHA-256 唯讀校驗 (9/9 PASS)
python scripts/gate1_check_coverage.py topic-kv-cache-reuse      # Gate 1: 檢索覆蓋率與知識邊界 (16 頁, 5/5 論文 PASS)
python scripts/gate2_check_drafts.py topic-kv-cache-reuse        # Gate 2: 逐頁稿出處、數據與字數密度 (12 頁 PASS)
python scripts/gate3_check_html.py topic-kv-cache-reuse          # Gate 3: HTML 結構、頁尾出處與零越權數值漂移 (PASS)
python scripts/check_overflow_headless.py topic-kv-cache-reuse   # 無頭 Chrome 1280×720 實測 (12/12 頁 0px 溢出 PASS)
```
