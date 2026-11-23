---
title: "KV Cache Reuse 領域全景總覽"
type: "overview"
sources:
  - "raw/01-cacheblend-2405.16444v3.md"
  - "raw/02-droidspeak-2411.02820v3.md"
updated: "2026-11-23"
---

# KV Cache Reuse（KV 快取重用）領域全景總覽

大型語言模型（LLM）在長上下文 RAG、多輪對話、多代理協作與多模型路由場景中，**Prefill 階段的重複計算**與 [Prefill 干擾](./entities/llm-serving-metrics.md) 已成為延遲（TTFT／TBT）與算力成本的核心瓶頸 `[CacheBlend, §2, p.3; DroidSpeak, §2.3, p.4]`。

## 技術演進脈絡（持續更新中）
1. **單模型非前綴多區塊融合 — [CacheBlend](./papers/cacheblend.md)（EuroSys '25）**：
   - 突破 [vLLM 與 SGLang](./entities/vllm-and-sglang.md) 僅限前綴快取的限制，提出 **Token 層級[選擇性 KV 重算](./concepts/selective-kv-recomputation.md)**（HKVD 5%–18%，預設 15%）搭配一次性 [RoPE 位置對齊](./concepts/rope-position-alignment.md) 與 [Compute-I/O 管線化](./concepts/compute-io-pipelining.md)，降低 2.2–3.3× TTFT、提升 2.8–5× 吞吐 `[CacheBlend, §4–7, p.5–12]`。
2. **同底模微調模型跨 LLM 共享 — [DroidSpeak](./papers/droidspeak.md)（2024／NSDI '26）**：
   - 將重用邊界由「同模型跨查詢」推進到「同底模不同微調模型（multi-LLM / multi-agent）」，揭示平均僅 11% 層為關鍵層，並為規避 [E-Cache 切換開銷](./concepts/e-cache-transition-overhead.md) 設計單一切換點連續層重算與帕累托動態調度，降低 1.7–2.6× Prefill 延遲、提升 2–3× 吞吐 `[DroidSpeak, §3–5, p.4–11]`。

## 延伸導覽
- [跨論文方法全景對照](./syntheses/kv-reuse-landscape.md)
- [Wiki 目錄索引](./index.md)
