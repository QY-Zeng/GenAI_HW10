---
title: "KV Cache Reuse 領域全景總覽"
type: "overview"
sources:
  - "raw/01-cacheblend-2405.16444v3.md"
updated: "2026-11-23"
---

# KV Cache Reuse（KV 快取重用）領域全景總覽

大型語言模型（LLM）在長上下文 RAG、多輪對話、多代理協作與多模型路由場景中，**Prefill 階段的重複計算**已成為延遲（[TTFT](./entities/llm-serving-metrics.md)）與算力成本的核心瓶頸 `[CacheBlend, §2, p.3]`。

## 技術演進第一階段：突破單模型前綴限制
傳統推理引擎（[vLLM 與 SGLang](./entities/vllm-and-sglang.md)）的 Prefix Caching 只能重用嚴格位於序列開頭的相同前綴；然而在 RAG 中，多段檢索文字會以不同順序動態組合：
- **[CacheBlend](./papers/cacheblend.md)**（EuroSys '25）率先提出針對非前綴多區塊的 **Token 層級[選擇性 KV 重算](./concepts/selective-kv-recomputation.md)**，搭配一次性 [RoPE 位置對齊](./concepts/rope-position-alignment.md) 與 [Compute-I/O 管線化](./concepts/compute-io-pipelining.md)，在僅重算約 5%–18%（預設 15%）HKVD tokens 下，即可恢復跨區塊 cross-attention 並實現 2.2–3.3× TTFT 縮減與 2.8–5× 吞吐提升 `[CacheBlend, §4–7, p.5–12]`。

*(本總覽將隨後續論文 Ingest 持續增量擴充。)*

## 延伸導覽
- [跨論文方法全景對照](./syntheses/kv-reuse-landscape.md)
- [Wiki 目錄索引](./index.md)
