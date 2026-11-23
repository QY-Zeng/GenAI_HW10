---
title: "Selective KV Recomputation（選擇性 KV 重算）"
type: "concept"
sources:
  - "raw/01-cacheblend-2405.16444v3.md"
  - "raw/02-droidspeak-2411.02820v3.md"
updated: "2026-11-23"
---

# Selective KV Recomputation（選擇性 KV 重算）

## 定義與核心直覺
在無法直接無損重用既有 KV Cache（例如非前綴拼接、模型微調差異或動態前綴變動）時，**選擇性 KV 重算**在「完全重算（高延遲、高品質）」與「直接全盤重用（低延遲、低品質）」之間取得帕累托最優平衡：只針對最關鍵的少數 **token** 或少數 **網路層** 重新計算 KV，其餘部分沿用快取。

## 1. Token 層級選擇性重算（CacheBlend）
在 [CacheBlend](../papers/cacheblend.md) 中，RAG 多區塊輸入因缺少跨區塊 cross-attention 而導致全重用品質大幅下降；但受惠於注意力稀疏性（attention sparsity），每層只有約 **10–15%** 的 **High-KV-Deviation（HKVD）tokens** 承載了絕大多數偏差 `[CacheBlend, §4.3, Fig. 6–7, p.6–7]`：
- **計算量成正比**：每層僅對選中的 $r\%$ tokens 計算 $Q_i, K_i, V_i$，再拼接未選中 tokens 的快取執行注意力計算，使算力降為完整 Prefill 的 $r\%$ `[CacheBlend, §4.2, Fig. 5, p.5–6]`。
- **漸進過濾（Gradual Filtering）**：利用相鄰層 HKVD 排名的高度 Spearman 相關性，首層全算後逐層遞減比例 $r_1\% > r_2\% > \dots$ 動態篩選，在 5%–18% 重算比例（系統預設下限 15%）下將 F1／Rouge-L 損失壓在 0.002–0.02 內，降低 2.2–3.3× TTFT `[CacheBlend, §4.3, §5.1, §7.2–7.3, Fig. 8–9, 16, p.7–8, 12]`。

## 2. Layer 層級連續區塊重算（DroidSpeak）
在 [DroidSpeak](../papers/droidspeak.md) 的同底模跨微調模型場景中，偏差來源不是 token 跨區塊互動，而是微調權重對少數**關鍵層（平均 11% 層數）**的改變 `[DroidSpeak, §3.2.2, Fig. 7, p.5–6]`：
- 由於在非連續層切換回重算會觸發高昂的 [E-Cache 切換開銷與誤差傳播](./e-cache-transition-overhead.md)（E cache 達 KV Cache 的 2–4×），DroidSpeak 不採零散層重算，而改採最多僅含**單一切換點**的連續層重算模式 `recompute → reuse → recompute → reuse` `[DroidSpeak, §4.1–4.2, Fig. 10–11, p.6–7]`。
- 透過離線帕累托剖析決定連續重算區間，線上可依延遲 SLO 動態調整重算層數，降低 1.7–2.6× Prefill 延遲並提升 2–3× 吞吐量 `[DroidSpeak, §4.3–4.4, §5.2–5.3, p.7–11]`。

## 兩類重算粒度對照
| 維度 | Token 級（CacheBlend） | Layer 級連續區塊（DroidSpeak） |
| --- | --- | --- |
| 偏差來源 | 非前綴 chunk 缺失跨區塊 cross-attention | 同底模不同微調權重造成關鍵層漂移 |
| 重算單位 | 每層重算 5%–18%（預設 15%）HKVD tokens | 針對所有 token 重算單一連續關鍵層區間 |
| 切換狀態成本 | 單層保留 Precomputed + Updated KV（過層即丟） | 切換點需傳送 E cache（2–4× KV 大小），故限 1 次切換 |

## 相關頁面
- [CacheBlend 論文筆記](../papers/cacheblend.md)
- [DroidSpeak 論文筆記](../papers/droidspeak.md)
- [E-Cache 切換開銷](./e-cache-transition-overhead.md)
- [Compute-I/O Pipelining](./compute-io-pipelining.md)
- [KV Cache Reuse 領域總覽](../overview.md)
