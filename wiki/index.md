---
title: "KV Cache Reuse LLM Wiki 索引"
type: "index"
sources:
  - "raw/01-cacheblend-2405.16444v3.md"
updated: "2026-11-23"
---

# KV Cache Reuse LLM Wiki 目錄索引

本知識庫依據 [AGENTS.md](../AGENTS.md) 維護，記錄 **KV Cache Reuse（KV 快取重用）** 領域論文的技術演進、核心概念、系統實體與跨文獻張力。

## 領域總覽
- [KV Cache Reuse 領域全景總覽](overview.md) — 領域問題定義與技術演進主軸。

## 單篇論文筆記 (`papers/`)
- [CacheBlend](papers/cacheblend.md) — RAG 多區塊非前綴 KV Cache 融合、HKVD 選擇性重算與載入管線化（EuroSys '25）。

## 核心概念 (`concepts/`)
- [Selective KV Recomputation](concepts/selective-kv-recomputation.md) — 以少量關鍵 token／層重算換取品質與延遲帕累托最優。
- [RoPE Position Alignment](concepts/rope-position-alignment.md) — 非前綴或跨位置重用 KV Cache 時的旋轉位置編碼對齊機制。
- [Compute-I/O Pipelining](concepts/compute-io-pipelining.md) — 將 GPU 計算與較慢儲存層 KV 載入重疊以隱藏延遲。

## 系統與指標實體 (`entities/`)
- [LLM 推理系統效能指標](entities/llm-serving-metrics.md) — TTFT、Throughput 等核心系統指標定義。
- [vLLM 與 SGLang](entities/vllm-and-sglang.md) — 現代分頁推理引擎與 Prefix Caching 基線。

## 跨文獻綜合與張力對照 (`syntheses/`)
- [跨論文方法全景對照](syntheses/kv-reuse-landscape.md) — 橫向比較各系統場景、粒度、位置處理與加速比。
