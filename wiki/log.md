---
title: "KV Cache Reuse LLM Wiki 變更日誌"
type: "log"
sources:
  - "raw/01-cacheblend-2405.16444v3.md"
updated: "2026-11-23"
---

# Wiki 操作日誌 (`log.md`)

| 日期 | 操作 | 對象 | 摘要 |
| --- | --- | --- | --- |
| 2026-11-23 | `init` | 專案架構 | 建立 `AGENTS.md`、`CLAUDE.md`、`scripts/lint_wiki.py` 與目錄骨架。 |
| 2026-11-23 | `raw` | 5 篇論文 | 歸檔 5 篇唯讀論文原文至 `raw/` 並建立 `MANIFEST.sha256`。 |
| 2026-11-23 | `ingest (1/5)` | `cacheblend.md` | 匯入 CacheBlend（EuroSys '25），建立基礎概念頁（Selective Recomputation、RoPE Alignment、Compute-I/O Pipelining）、實體頁（Metrics、vLLM/SGLang）、`overview.md` 與 `kv-reuse-landscape.md`。 |
