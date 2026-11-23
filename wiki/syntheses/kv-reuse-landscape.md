---
title: "KV Cache Reuse 跨論文方法全景對照"
type: "synthesis"
sources:
  - "raw/01-cacheblend-2405.16444v3.md"
updated: "2026-11-23"
---

# KV Cache Reuse 跨論文方法全景對照

本頁隨論文逐篇 Ingest 動態維護，橫向比較不同 KV Cache Reuse 系統的適用場景、重用粒度、位置處理、修正策略與量化效益。

| 論文／系統 | 核心場景 | 模型限制 | 重用／修正粒度 | 位置對齊策略 | 核心代表數據 | 出處 |
| --- | --- | --- | --- | --- | --- | --- |
| [CacheBlend](../papers/cacheblend.md)（EuroSys '25） | RAG 多區塊非前綴知識融合 | 同模型 | Token 級選擇性重算（HKVD 5–18%，預設 15%，漸進過濾） | RoPE 單次旋轉矩陣校正 | TTFT 降 **2.2–3.3×**、吞吐升 **2.8–5×**、品質損 ≤ 0.02 | `[CacheBlend, §4.3, §7.2–7.3, p.6–7, 12]` |

## 相關頁面
- [KV Cache Reuse 領域總覽](../overview.md)
- [vLLM 與 SGLang](../entities/vllm-and-sglang.md)
- [RoPE 位置對齊](../concepts/rope-position-alignment.md)
