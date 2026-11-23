---
title: "KV Cache Reuse 跨論文方法全景對照"
type: "synthesis"
sources:
  - "raw/01-cacheblend-2405.16444v3.md"
  - "raw/02-droidspeak-2411.02820v3.md"
  - "raw/03-lmcache-2510.09665v2.md"
  - "raw/04-relaycaching-2603.13289v1.md"
  - "raw/05-cross-model-kv-transfer-2608.03893v1.md"
updated: "2026-11-23"
---

# KV Cache Reuse 跨論文方法全景對照

本頁彙整 5 篇代表性論文的技術邊界、重用機制、位置／狀態對齊策略、代表數據與核心限制，構成整個知識庫的橫向對照中樞。

## 1. 五篇論文核心規格矩陣
| 論文／系統 | 核心場景 | 模型邊界 | 重用／修正機制 | 位置／狀態對齊 | 核心代表數據 | 關鍵限制 | 出處 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [CacheBlend](../papers/cacheblend.md)（EuroSys '25） | RAG 多區塊非前綴融合 | 同模型 | Token 級選擇性重算（HKVD 5–18%，預設 15%，漸進過濾）＋逐層 I/O 管線化 | RoPE 單次旋轉校正 | TTFT 降 **2.2–3.3×**、吞吐升 **2.8–5×**、品質損 ≤ 0.02 | 偏靜態預計算；動態 MAS 易掉點且線性擴展 | `[CacheBlend, §4.3, §7.2–7.3, p.6–7, 12]` |
| [DroidSpeak](../papers/droidspeak.md)（2024／NSDI '26） | 多微調模型共享上下文 | 同底模、**同架構**微調變體 | Layer 級單一連續區間重算（`recompute→reuse→recompute→reuse`，帕累托剖析） | 單一切換點傳送 [E Cache](../concepts/e-cache-transition-overhead.md) | Prefill 降 **1.7–2.6×**、吞吐升 **2–3×**、記憶體降 **1.5×** | 限同架構（同層數／維度）；E-cache 為 KV 的 2–4× | `[DroidSpeak, §4.1–4.2, §5.2–5.3, p.6–7, 10]` |
| [LMCache](../papers/lmcache.md)（2025） | 企業級跨查詢卸載與 PD 分離 | 同模型（跨引擎／跨節點，vLLM & SGLang） | 256-token 跨層 Chunk 批次搬運、雙層管線化、Zero-Copy、動態卸載 | 精確前綴匹配 + 標準化 KV Connector & Controller API | 單機吞吐升 **2.3–14×**（跨情境最高 **15×**）、TTFT 降 **1.9–8.1×**、頻寬 **400 Gbps** | 精確前綴對截斷敏感（85%→45%）；低頻寬短文不划算 | `[LMCache, Abstract, §5–9, Table 5, p.1, 6–15]` |
| [RelayCaching](../papers/relaycaching.md)（2026） | 多代理系統（MAS）Decode-to-Prefill 接力 | 同模型（同質 MAS） | 層×Token 雙維稀疏修正：U 型中層 $[L_{\text{start}}, L_{\text{end}}]$ + Value Cosine／注意力影響／尾端 10 tok | Pre-RoPE 儲存 + Relay Handoff 重施 RoPE + $h^{(L_{\text{start}})}$ | 重用率 **>80%**、5 代理 TTFT 降 **4.71×**、12K 長文降 **9.2×**（次線性） | 僅支援同質 MAS（同架構同權重） | `[RelayCaching, §4–5, Table 1–2, Fig. 8, Appendix C, p.4–8, 18]` |
| [Cross-Model KV Transfer](../papers/cross-model-kv-transfer.md)（NVIDIA, 2026） | 同家族跨尺寸模型切換／級聯／路由 | 同家族、**不同尺寸**（matched-KV：$n_{\text{kv}}, d_h$ 相同） | 閉式逐頭 Ridge 回歸 + top-$k$ 跨層源層選擇（失敗配對可換非線性 MLP） | 剝源 RoPE → 無位置內容空間映射 → 重施目標 RoPE | 4 組 Tier 1 保留 **73–98%**、S→L 加速 **2.7–25×**（32K 達 25×）；MLP 救回 **+24–37 pp** | 限同家族 dense matched-KV；每方向 Mapper 佔 4–12 GB；Tier 2 非線性配對 Ridge 失敗 | `[Cross-Model KV, §3–5, Table 1, 3, 5, 12, p.4–9, 17]` |

## 2. 三軸演進視角（供教學導讀與系統選型）
1. **空間與系統軸（怎麼存、怎麼搬？）**：從單機 GPU 內前綴快取（vLLM／SGLang）→ [LMCache](../papers/lmcache.md) 透過 Chunk 批次搬運、管線化與標準化 API 跨出 GPU、跨出單機，連結 CPU／SSD／遠端儲存與 PD 分離。
2. **語境與位置軸（前綴變了怎麼辦？）**：從嚴格前綴匹配 → [CacheBlend](../papers/cacheblend.md) 處理靜態 RAG 非前綴拼接（Token 級 HKVD）→ [RelayCaching](../papers/relaycaching.md) 處理多代理動態 Decode-to-Prefill 接力（U 型中層＋方向性餘弦＋影響力＋尾端修正）。
3. **模型邊界軸（換了模型還能重用嗎？）**：從單一模型 → [DroidSpeak](../papers/droidspeak.md) 同底模同架構微調模型（連續層重算＋單次 E-cache）→ [Cross-Model KV Transfer](../papers/cross-model-kv-transfer.md) 同家族跨尺寸模型（無梯度閉式線性 Ridge 映射＋內容空間 RoPE 解耦）。

## 相關頁面
- [KV Cache Reuse 領域總覽](../overview.md)
- [跨文獻張力與差異彙整](./conflicts-and-tensions.md)
- [Selective KV Recomputation](../concepts/selective-kv-recomputation.md)
- [KV 偏差衡量指標](../concepts/kv-deviation-metrics.md)
- [RoPE Position Alignment](../concepts/rope-position-alignment.md)
