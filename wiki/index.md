---
title: "KV Cache Reuse LLM Wiki 索引"
type: "index"
sources:
  - "raw/01-cacheblend-2405.16444v3.md"
  - "raw/02-droidspeak-2411.02820v3.md"
  - "raw/03-lmcache-2510.09665v2.md"
  - "raw/04-relaycaching-2603.13289v1.md"
updated: "2026-11-23"
---

# KV Cache Reuse LLM Wiki 目錄索引

本知識庫依據 [AGENTS.md](../AGENTS.md) 維護，記錄 **KV Cache Reuse（KV 快取重用）** 領域論文的技術演進、核心概念、系統實體與跨文獻張力。

## 領域總覽
- [KV Cache Reuse 領域全景總覽](overview.md) — 領域問題定義與技術演進主軸。

## 單篇論文筆記 (`papers/`)
- [CacheBlend](papers/cacheblend.md) — RAG 多區塊非前綴 KV Cache 融合、HKVD 選擇性重算與載入管線化（EuroSys '25）。
- [DroidSpeak](papers/droidspeak.md) — 同底模微調模型間的選擇性連續層重算 KV Cache 共享（2024／NSDI '26）。
- [LMCache](papers/lmcache.md) — 企業級分散式 KV Cache 層、分層卸載、PD 分離與標準化管理介面（2025）。
- [RelayCaching](papers/relaycaching.md) — 多代理系統 Decode-to-Prefill KV 重用、U 型中層與雙準則稀疏修正（2026）。

## 核心概念 (`concepts/`)
- [Selective KV Recomputation](concepts/selective-kv-recomputation.md) — Token 級、Layer 級與層×Token 雙維度選擇性重算比較。
- [KV Deviation Metrics](concepts/kv-deviation-metrics.md) — KV 絕對值／範數偏差 vs Value Cosine、注意力影響力與 U 型曲線。
- [E-Cache Transition Overhead](concepts/e-cache-transition-overhead.md) — 從重用切回重算時 E Cache 的容量與誤差累積瓶頸。
- [RoPE Position Alignment](concepts/rope-position-alignment.md) — 單次旋轉校正與 Pre-RoPE 儲存／重施對齊機制。
- [Compute-I/O Pipelining](concepts/compute-io-pipelining.md) — 逐層計算重疊、Chunk 批次搬運、零複製與自適應載入交叉點。

## 系統與指標實體 (`entities/`)
- [LLM 推理系統效能指標](entities/llm-serving-metrics.md) — TTFT、TBT/ITL、E2E、Goodput 與 Prefill 干擾。
- [vLLM 與 SGLang](entities/vllm-and-sglang.md) — 現代分頁推理引擎、Prefix Caching 與分頁 I/O 瓶頸。
- [LMCache 系統架構](entities/lmcache-system.md) — KV Connector API、Controller API 與生態系採用。

## 跨文獻綜合與張力對照 (`syntheses/`)
- [跨論文方法全景對照](syntheses/kv-reuse-landscape.md) — 橫向比較各系統場景、粒度、位置處理與加速比。
- [跨文獻張力與差異彙整](syntheses/conflicts-and-tensions.md) — 並陳並剖析各論文的前提差異與爭議結論。
