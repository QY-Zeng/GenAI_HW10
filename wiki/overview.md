---
title: "KV Cache Reuse 領域全景總覽"
type: "overview"
sources:
  - "raw/01-cacheblend-2405.16444v3.md"
  - "raw/02-droidspeak-2411.02820v3.md"
  - "raw/03-lmcache-2510.09665v2.md"
  - "raw/04-relaycaching-2603.13289v1.md"
updated: "2026-11-23"
---

# KV Cache Reuse（KV 快取重用）領域全景總覽

大型語言模型（LLM）在長上下文 RAG、多輪對話、多代理協作與多模型路由場景中，**Prefill 階段的重複計算**與 [Prefill 干擾](./entities/llm-serving-metrics.md) 已成為延遲（TTFT／ITL）與算力成本的核心瓶頸 `[CacheBlend, §2, p.3; DroidSpeak, §2.3, p.4; LMCache, §2.2, p.3; RelayCaching, §1, p.1]`。

## 技術演進脈絡（持續更新中）
1. **單模型非前綴多區塊融合 — [CacheBlend](./papers/cacheblend.md)（EuroSys '25）**：
   - 突破 [vLLM 與 SGLang](./entities/vllm-and-sglang.md) 僅限前綴快取的限制，提出 **Token 層級[選擇性 KV 重算](./concepts/selective-kv-recomputation.md)**（HKVD 5%–18%）搭配 [RoPE 位置對齊](./concepts/rope-position-alignment.md) 與 [Compute-I/O 管線化](./concepts/compute-io-pipelining.md)，降 2.2–3.3× TTFT、升 2.8–5× 吞吐 `[CacheBlend, §4–7, p.5–12]`。
2. **同底模微調模型跨 LLM 共享 — [DroidSpeak](./papers/droidspeak.md)（2024／NSDI '26）**：
   - 推進至「同底模不同微調模型」，揭示平均僅 11% 層為關鍵層，為規避 [E-Cache 切換開銷](./concepts/e-cache-transition-overhead.md) 設計單一切換點連續層重算，降 1.7–2.6× Prefill 延遲、升 2–3× 吞吐 `[DroidSpeak, §3–5, p.4–11]`。
3. **企業級分散式 KV 快取基礎設施 — [LMCache](./papers/lmcache.md)（2025）**：
   - 將 KV Cache 打造為 LLM 推理的一等公民資料層（[LMCache 系統架構](./entities/lmcache-system.md)），以 256-token chunk 批次搬運（400 Gbps）、雙層管線化、Zero-Copy 與標準化 Connector / Controller API 支援跨查詢卸載與 PD 分離，最高提升 **15× 吞吐量** `[LMCache, Abstract, §5–8, Table 5, p.1, 6–14]`。
4. **多代理動態 Decode-to-Prefill 重用 — [RelayCaching](./papers/relaycaching.md)（2026）**：
   - 針對多代理系統中上游解碼輸出成為下游非前綴輸入的 $O(M^2)$ 級聯冗餘，揭示 Value Cosine 為主導偏差（[KV 偏差衡量指標](./concepts/kv-deviation-metrics.md)）與 U 型中層結構，透過層區間剖析＋雙準則 Token 選擇達成 **>80%** 重用率與 **4.71×–9.2×** TTFT 加速 `[RelayCaching, §3–5, Table 1–2, Fig. 8, p.3–8]`。

## 延伸導覽
- [跨論文方法全景對照](./syntheses/kv-reuse-landscape.md)
- [跨文獻張力與差異彙整](./syntheses/conflicts-and-tensions.md)
- [Wiki 目錄索引](./index.md)
