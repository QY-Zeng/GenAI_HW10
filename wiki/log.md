---
title: "KV Cache Reuse LLM Wiki 變更日誌"
type: "log"
sources:
  - "raw/01-cacheblend-2405.16444v3.md"
  - "raw/02-droidspeak-2411.02820v3.md"
  - "raw/03-lmcache-2510.09665v2.md"
  - "raw/04-relaycaching-2603.13289v1.md"
updated: "2026-11-23"
---

# Wiki 操作日誌 (`log.md`)

| 日期 | 操作 | 對象 | 摘要 |
| --- | --- | --- | --- |
| 2026-11-23 | `init` | 專案架構 | 建立 `AGENTS.md`、`CLAUDE.md`、`scripts/lint_wiki.py` 與目錄骨架。 |
| 2026-11-23 | `raw` | 5 篇論文 | 歸檔 5 篇唯讀論文原文至 `raw/` 並建立 `MANIFEST.sha256`。 |
| 2026-11-23 | `ingest (1/5)` | `cacheblend.md` | 匯入 CacheBlend（EuroSys '25），建立基礎概念頁、實體頁、`overview.md` 與 `kv-reuse-landscape.md`。 |
| 2026-11-23 | `ingest (2/5)` | `droidspeak.md` | 匯入 DroidSpeak，新增 `e-cache-transition-overhead.md`，增量更新重算概念頁、指標頁與綜合頁。 |
| 2026-11-23 | `ingest (3/5)` | `lmcache.md` | 匯入 LMCache，新增 `lmcache-system.md` 與 `conflicts-and-tensions.md`，增量更新管線化與推理引擎頁。 |
| 2026-11-23 | `ingest (4/5)` | `relaycaching.md` | 匯入 RelayCaching，新增 `kv-deviation-metrics.md`，補入 CacheBlend vs RelayCaching 跨文獻張力並增量更新概念與綜合頁。 |
