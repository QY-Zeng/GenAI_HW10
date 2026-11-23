---
title: "RoPE Position Alignment（旋轉位置編碼對齊）"
type: "concept"
sources:
  - "raw/01-cacheblend-2405.16444v3.md"
updated: "2026-11-23"
---

# RoPE Position Alignment（旋轉位置編碼對齊）

## 為何 KV 重用必須處理 RoPE？
現代 Transformer LLM 普遍採用 **Rotary Positional Embedding（RoPE）**，將 token 的絕對位置 $m$ 透過旋轉矩陣 $\mathbf{R}_{\Theta, m}^d$ 直接編碼進 Query 與 Key 向量中（Value 向量則不含位置編碼）。當快取的 KV 被搬移到不同的序列位置時，原本的 Key 帶有舊位置旋轉角度，若未經對齊將破壞注意力分數的相對距離關係。

## 1. 預計算區塊的單次旋轉校正（CacheBlend）
在 [CacheBlend](../papers/cacheblend.md) 中，每個 RAG 文字區塊皆獨立預計算 KV Cache；當多個 chunk 在執行期依任意順序拼接時：
- 透過證明 RoPE 內積 $q_{m+l}^\top k_m$ 僅依賴相對距離 $l$ 而與絕對位置 $m$ 無關（Proposition A.1），CacheBlend 只需將預存的 K 向量乘上一次相對旋轉矩陣，即可恢復正確的位置編碼 `[CacheBlend, Footnote 3, p.6; Appendix A, p.16]`。
- 由於每個 chunk 只需執行一次矩陣旋轉乘法，延遲開銷幾乎可忽略，但仍須搭配 [選擇性 KV 重算](./selective-kv-recomputation.md) 來修復跨區塊 cross-attention `[CacheBlend, §3.3, §4.3, p.4, 6]`。

## 相關頁面
- [CacheBlend 論文筆記](../papers/cacheblend.md)
- [KV Cache Reuse 領域總覽](../overview.md)
- [跨論文方法全景對照](../syntheses/kv-reuse-landscape.md)
