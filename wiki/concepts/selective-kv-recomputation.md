---
title: "Selective KV Recomputation（選擇性 KV 重算）"
type: "concept"
sources:
  - "raw/01-cacheblend-2405.16444v3.md"
updated: "2026-11-23"
---

# Selective KV Recomputation（選擇性 KV 重算）

## 定義與核心直覺
在無法直接無損重用既有 KV Cache（例如非前綴拼接、模型微調差異或動態前綴變動）時，**選擇性 KV 重算**在「完全重算（高延遲、高品質）」與「直接全盤重用（低延遲、低品質）」之間取得帕累托最優平衡：只針對最關鍵的少數 token 或少數網路層重新計算 KV，其餘部分沿用快取。

## Token 層級選擇性重算（CacheBlend）
在 [CacheBlend](../papers/cacheblend.md) 中，RAG 多區塊輸入會因缺少跨區塊 cross-attention 而導致全重用品質大幅下降；但由於注意力矩陣具高度稀疏性（attention sparsity），每層只有約 **10–15%** 的 **High-KV-Deviation（HKVD）tokens** 承載了絕大多數偏差 `[CacheBlend, §4.3, Fig. 6–7, p.6–7]`：

- **計算量成正比**：每層只對被選中的 $r\%$ tokens 計算 $Q_i, K_i, V_i$，再與未選中 tokens 的預存 KV 拼接進行注意力計算，使計算開銷嚴格縮減為完整 Prefill 的 $r\%$ `[CacheBlend, §4.2, Fig. 5, p.5–6]`。
- **跨層相關性與漸進過濾（Gradual Filtering）**：相鄰兩層的高偏差 token 具高度 Spearman 排名相關性，因此可透過首層全算＋後續逐層遞減比例 $r_1\% > r_2\% > \dots$ 動態篩出 HKVD tokens，無須預知 Ground-Truth KV `[CacheBlend, §4.3, Fig. 8–9, p.7]`。
- **品質與速度表現**：在 5%–18% 重算比例（系統預設下限 $r^* = 15\%$）下即可將 F1／Rouge-L 損失控制在 0.002–0.02 內，降低 2.2–3.3× TTFT `[CacheBlend, §5.1, §7.2–7.3, Fig. 16, p.8, 12]`。

## 相關頁面
- [CacheBlend 論文筆記](../papers/cacheblend.md)
- [Compute-I/O Pipelining](./compute-io-pipelining.md)
- [RoPE 位置對齊](./rope-position-alignment.md)
- [KV Cache Reuse 領域總覽](../overview.md)
