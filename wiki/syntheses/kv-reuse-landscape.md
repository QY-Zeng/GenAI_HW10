---
title: "KV Cache Reuse 跨論文方法全景對照"
type: "synthesis"
sources:
  - "raw/01-cacheblend-2405.16444v3.md"
  - "raw/02-droidspeak-2411.02820v3.md"
  - "raw/03-lmcache-2510.09665v2.md"
updated: "2026-11-23"
---

# KV Cache Reuse 跨論文方法全景對照

本頁隨論文逐篇 Ingest 動態維護，橫向比較不同 KV Cache Reuse 系統的適用場景、模型限制、重用粒度、位置處理與量化效益。

| 論文／系統 | 核心場景 | 模型限制 | 重用／修正粒度 | 位置／狀態對齊策略 | 核心代表數據 | 出處 |
| --- | --- | --- | --- | --- | --- | --- |
| [CacheBlend](../papers/cacheblend.md)（EuroSys '25） | RAG 多區塊非前綴知識融合 | 同模型 | Token 級選擇性重算（HKVD 5–18%，預設 15%，漸進過濾） | RoPE 單次旋轉矩陣校正 | TTFT 降 **2.2–3.3×**、吞吐升 **2.8–5×**、品質損 ≤ 0.02 | `[CacheBlend, §4.3, §7.2–7.3, p.6–7, 12]` |
| [DroidSpeak](../papers/droidspeak.md)（2024／NSDI '26） | 多代理／多微調模型共享相同上下文 | 同底模、**同架構**微調變體 | Layer 級單一連續區間重算（`recompute→reuse→recompute→reuse`，離線帕累托剖析） | 單一切換點傳送 [E Cache](../concepts/e-cache-transition-overhead.md) | Prefill 延遲降 **1.7–2.6×**、吞吐升 **2–3×**、記憶體降 **1.5×** | `[DroidSpeak, §4.2, §5.2–5.3, Fig. 1, p.1, 7, 10]` |
| [LMCache](../papers/lmcache.md)（2025） | 企業級跨查詢卸載（CPU/SSD/遠端）與 PD 分離 | 同模型（跨引擎／跨節點，支援 vLLM & SGLang） | 256-token 跨層 Chunk 批次搬運、零複製與三指標動態卸載（精確前綴重用） | 精確前綴匹配 + 標準化 KV Connector & Controller API | 單機吞吐升 **2.3–14×**（跨情境最高 **15×**）、TTFT 降 **1.9–8.1×**、載入頻寬 **400 Gbps** | `[LMCache, Abstract, §5–8, Table 5, p.1, 6–14]` |

## 相關頁面
- [KV Cache Reuse 領域總覽](../overview.md)
- [跨文獻張力與差異彙整](./conflicts-and-tensions.md)
- [LMCache 系統架構](../entities/lmcache-system.md)
- [vLLM 與 SGLang](../entities/vllm-and-sglang.md)
