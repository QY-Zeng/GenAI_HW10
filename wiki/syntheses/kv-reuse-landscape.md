---
title: "KV Cache Reuse 跨論文方法全景對照"
type: "synthesis"
sources:
  - "raw/01-cacheblend-2405.16444v3.md"
  - "raw/02-droidspeak-2411.02820v3.md"
  - "raw/03-lmcache-2510.09665v2.md"
  - "raw/04-relaycaching-2603.13289v1.md"
updated: "2026-11-23"
---

# KV Cache Reuse 跨論文方法全景對照

本頁隨論文逐篇 Ingest 動態維護，橫向比較不同 KV Cache Reuse 系統的適用場景、模型限制、重用粒度、位置處理與量化效益。

| 論文／系統 | 核心場景 | 模型限制 | 重用／修正粒度 | 位置／狀態對齊策略 | 核心代表數據 | 出處 |
| --- | --- | --- | --- | --- | --- | --- |
| [CacheBlend](../papers/cacheblend.md)（EuroSys '25） | RAG 多區塊非前綴知識融合 | 同模型 | Token 級選擇性重算（HKVD 5–18%，預設 15%，漸進過濾） | RoPE 單次旋轉矩陣校正 | TTFT 降 **2.2–3.3×**、吞吐升 **2.8–5×**、品質損 ≤ 0.02 | `[CacheBlend, §4.3, §7.2–7.3, p.6–7, 12]` |
| [DroidSpeak](../papers/droidspeak.md)（2024／NSDI '26） | 多代理／多微調模型共享相同上下文 | 同底模、**同架構**微調變體 | Layer 級單一連續區間重算（`recompute→reuse→recompute→reuse`，離線帕累托剖析） | 單一切換點傳送 [E Cache](../concepts/e-cache-transition-overhead.md) | Prefill 延遲降 **1.7–2.6×**、吞吐升 **2–3×**、記憶體降 **1.5×** | `[DroidSpeak, §4.2, §5.2–5.3, Fig. 1, p.1, 7, 10]` |
| [LMCache](../papers/lmcache.md)（2025） | 企業級跨查詢卸載（CPU/SSD/遠端）與 PD 分離 | 同模型（跨引擎／跨節點，支援 vLLM & SGLang） | 256-token 跨層 Chunk 批次搬運、零複製與三指標動態卸載（精確前綴） | 精確前綴匹配 + 標準化 KV Connector & Controller API | 單機吞吐升 **2.3–14×**（跨情境最高 **15×**）、TTFT 降 **1.9–8.1×**、頻寬 **400 Gbps** | `[LMCache, Abstract, §5–8, Table 5, p.1, 6–14]` |
| [RelayCaching](../papers/relaycaching.md)（2026） | 同質多代理系統（MAS）Decode-to-Prefill 接力重用 | 同模型（同質 MAS） | 層×Token 雙維稀疏修正：U 型中層 $[L_{\text{start}}, L_{\text{end}}]$ + 偏差／影響力／尾端 10 tok | Pre-RoPE 儲存 + Relay Handoff 重新施加 RoPE + $h^{(L_{\text{start}})}$ | 重用率 **>80%**、5 代理 TTFT 降 **4.71×**、12K 長序列降 **9.2×**（次線性） | `[RelayCaching, §4–5, Table 1–2, Fig. 8, p.4–8]` |

## 相關頁面
- [KV Cache Reuse 領域總覽](../overview.md)
- [跨文獻張力與差異彙整](./conflicts-and-tensions.md)
- [Selective KV Recomputation](../concepts/selective-kv-recomputation.md)
- [KV 偏差衡量指標](../concepts/kv-deviation-metrics.md)
