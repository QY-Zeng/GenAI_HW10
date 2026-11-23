---
title: "Selective KV Recomputation（選擇性 KV 重算）"
type: "concept"
sources:
  - "raw/01-cacheblend-2405.16444v3.md"
  - "raw/02-droidspeak-2411.02820v3.md"
  - "raw/04-relaycaching-2603.13289v1.md"
updated: "2026-11-23"
---

# Selective KV Recomputation（選擇性 KV 重算）

## 定義與核心直覺
在無法直接無損重用既有 KV Cache（非前綴拼接、模型微調差異或動態前綴變動）時，**選擇性 KV 重算**在「完全重算（高延遲、高品質）」與「直接全盤重用（低延遲、低品質）」之間取得帕累托最優平衡：只針對最關鍵的少數 **token**、**網路層**，或兩者的**交集（層×token 二維稀疏區域）**重新計算 KV。

## 1. Token 層級選擇性重算（CacheBlend）
在 [CacheBlend](../papers/cacheblend.md) 的靜態 RAG 多區塊融合場景中，每層僅約 **10–15%** 的 **HKVD tokens** 承載主要 cross-attention 偏差 `[CacheBlend, §4.3, Fig. 6–7, p.6–7]`：
- 透過首層全算＋逐層遞減比例的 **Gradual Filtering**，以 **5%–18%**（預設下限 15%）重算比例將 F1／Rouge-L 損失壓在 0.002–0.02 內，降低 **2.2–3.3× TTFT** `[CacheBlend, §4.3, §5.1, §7.2–7.3, p.7–8, 12]`。

## 2. Layer 層級連續區塊重算（DroidSpeak）
在 [DroidSpeak](../papers/droidspeak.md) 的同底模跨微調模型場景中，平均僅 **11%** 層屬於對微調敏感的關鍵層；為避免多次切換帶來 [E-Cache 切換開銷](./e-cache-transition-overhead.md)（2–4× KV 大小與誤差累積），改採最多一次 `reuse → recompute` 切換的連續層重算模式 `recompute → reuse → recompute → reuse`，降 **1.7–2.6×** Prefill 延遲並升 **2–3×** 吞吐 `[DroidSpeak, §3.2.2, §4.1–4.2, §5.2–5.3, p.5–7, 10]`。

## 3. 層×Token 雙維度稀疏修正（RelayCaching）
在 [RelayCaching](../papers/relaycaching.md) 的動態多代理 Decode-to-Prefill 場景中，進一步結合「層維度」與「Token 維度」的結構稀疏性：
- **層維度**：依 U 型 Value Cosine 曲線，跳過淺層 $[0, L_{\text{start}})$ 與深層 $(L_{\text{end}}, L_{\text{full}}]$，僅在中層 $[L_{\text{start}}, L_{\text{end}}]$ 進行修正 `[RelayCaching, §4.2, Fig. 5, p.5]`。
- **Token 維度**：於單一穩定偵測層 $L_{\text{det}}$ 以均值相對門檻（非固定比例）結合 Value Cosine 偏差 $I_{\text{dev}}$、累計注意力影響力 $I_{\text{inf-score}}$ 與尾端 10 token $I_{\text{inf-suffix}}$ 一次定位關鍵 token 並沿用至 $L_{\text{end}}$，在 **>80%** 重用率下達成**次線性**長上下文擴展（12K tokens 時 0.42 s vs CacheBlend 1.08 s）`[RelayCaching, §4.3, §5.2–5.3, Fig. 8, p.6–8]`。

## 三類選擇性重算對照
| 維度 | Token 級（CacheBlend） | Layer 級連續區塊（DroidSpeak） | 層×Token 雙維稀疏（RelayCaching） |
| --- | --- | --- | --- |
| 偏差來源 | 非前綴 chunk 缺失跨區塊 cross-attention | 同底模微調權重造成關鍵層漂移 | 多代理動態解碼輸出之 prefix variation |
| 關鍵篩選訊號 | [KV 絕對偏差（HKVD）](./kv-deviation-metrics.md) | 離線帕累托層區間熱力圖 | U 型中層 + Value Cosine + 注意力影響 + 尾端 10 tok |
| 長上下文擴展性 | 固定比例（線性成長） | 固定層數比例（隨長度縮減約半） | 均值相對門檻（**次線性**成長） |

## 相關頁面
- [CacheBlend](../papers/cacheblend.md) ｜ [DroidSpeak](../papers/droidspeak.md) ｜ [RelayCaching](../papers/relaycaching.md)
- [KV 偏差衡量指標](./kv-deviation-metrics.md) ｜ [E-Cache 切換開銷](./e-cache-transition-overhead.md)
- [KV Cache Reuse 領域總覽](../overview.md)
