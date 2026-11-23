---
title: "RoPE Position Alignment（旋轉位置編碼對齊）"
type: "concept"
sources:
  - "raw/01-cacheblend-2405.16444v3.md"
  - "raw/04-relaycaching-2603.13289v1.md"
updated: "2026-11-23"
---

# RoPE Position Alignment（旋轉位置編碼對齊）

## 為何 KV 重用必須處理 RoPE？
現代 Transformer LLM 普遍採用 **Rotary Positional Embedding（RoPE）**，將 token 的絕對位置 $m$ 透過正交旋轉矩陣 $\mathbf{R}_{\Theta, m}^d$ 編碼至 Query 與 Key 向量中（Value 向量不含位置編碼）。當快取的 KV 被移至新位置時，必須校正 Key 的旋轉角度，否則將破壞注意力分數的相對距離不變性。

## 1. 預計算區塊的單次相對旋轉校正（CacheBlend）
在 [CacheBlend](../papers/cacheblend.md) 中，每個 RAG 文字區塊皆先以既定位置預計算 KV；拼接至新位置時，利用 RoPE 內積 $q_{m+l}^\top k_m$ 僅取決於相對距離 $l$ 的性質（Proposition A.1），對預存 Key 乘上一次相對旋轉矩陣即可完成對齊，額外開銷幾乎為零 `[CacheBlend, Footnote 3, p.6; Appendix A, p.16]`。

## 2. Pre-RoPE 儲存＋接力重施旋轉（RelayCaching）
在 [RelayCaching](../papers/relaycaching.md) 的多代理接力流程中，上游代理在解碼階段（Stage $i-1$）直接平行保存尚未施加位置旋轉的 **Pre-RoPE Decoding KV Cache**；待交棒至下游代理（Stage $i$）進行 Prefill 時（Relay Handoff），再依據該段文字於下游提示中的新位置重新施加 RoPE（RoPE Re-apply），隨後進入中層稀疏修正流程 `[RelayCaching, §4.2, Fig. 5, p.5]`。

## 相關頁面
- [CacheBlend 論文筆記](../papers/cacheblend.md)
- [RelayCaching 論文筆記](../papers/relaycaching.md)
- [KV Cache Reuse 領域總覽](../overview.md)
- [跨論文方法全景對照](../syntheses/kv-reuse-landscape.md)
