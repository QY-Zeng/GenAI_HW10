---
title: "KV Deviation Metrics（KV 偏差衡量指標與子空間敏感度）"
type: "concept"
sources:
  - "raw/01-cacheblend-2405.16444v3.md"
  - "raw/04-relaycaching-2603.13289v1.md"
  - "raw/05-cross-model-kv-transfer-2608.03893v1.md"
updated: "2026-11-23"
---

# KV Deviation Metrics（KV 偏差衡量指標與子空間敏感度）

在 KV Cache Reuse 領域中，「用什麼指標來衡量近似 KV 的好壞」歷經了三個層次的深化——從**數值大小誤差**、走向**方向與下游影響力**，再走向**注意力敏感子空間的誤差落點**。

## 1. 絕對數值／範數偏差（[CacheBlend](../papers/cacheblend.md) — 靜態 RAG 融合）
- 定義 token 級 **KV deviation** $\Delta_{\text{kv}}(KV_i, KV_i^{\text{full}})[j] = |KV_i[j] - KV_i^{\text{full}}[j]|$，並以 forward attention matrix 的 L2 差衡量注意力偏差 `[CacheBlend, §4.1, Table 1, p.5]`。
- 適用於靜態獨立預計算區塊（Independent KV 的 Value Norm 僅 0.588），但若直接移用於動態 Decode-to-Prefill 會錯失主導偏差 `[RelayCaching, §3.1, §5.2, Fig. 2, p.3, 7]`。

## 2. Value Cosine 方向偏差＋累計注意力影響力（[RelayCaching](../papers/relaycaching.md) — 動態 MAS）
- 在 Decode-to-Prefill 重用中，Key/Value Norm（0.947 / 0.926）與 Key Cosine（0.935）皆高度一致，唯獨 **Value Cosine（0.800）** 為主要偏差指標，且呈現跨模型通用的**中層 U 型曲線**與 **> 0.9** 相鄰層 Spearman 相關 `[RelayCaching, §3.1–3.3, Fig. 2–4, Appendix A, p.3–4, 11–13]`。
- 消融證實單靠偏差值仍會使 GSM8K 掉至 79.68%，須結合累計注意力影響分數（$I_{\text{inf-score}}$）與尾端 10 token（$I_{\text{inf-suffix}}$）才可回升至 **84.84%** `[RelayCaching, §5.4, Table 3, p.8]`。

## 3. 重建指標 $R^2$ 失靈 vs. Attention-Output Cosine 與誤差落點（[Cross-Model KV Transfer](../papers/cross-model-kv-transfer.md)）
- 跨模型轉移研究發現了一個顛覆直覺的現象：校準集 $R_K^2$ 雖然適合在同一配對內挑選 top-$k$ 源層，但**完全無法預測跨配對的下游準確率**——在 12 組 matched-KV 配對評估（6 組 S→L + 6 組 L→S）上，校準集 $R_K^2$ 與 HellaSwag 保留率的 Pearson 相關性竟然是 **$r = -0.20$**（例如 Llama 3.1 8B→70B 與 70B→8B 擁有相同 $R_K^2 = 0.84$，保留率卻分別是 94% 與 37%）`[Cross-Model KV, §4.5, p.7–8]`。
- **真正決定品質的是「誤差落點（Error Placement）」，而非誤差大小**：
  - 注意力機制並非對每個維度等權看待，而是以目標 Query 矩陣 $\mathbf{Q}_h$ 評分 Key 並加權 Value。
  - **Attention-Output Cosine**（映射 KV 與真實 KV 所算出注意力輸出之餘弦相似度）與 HellaSwag 保留率的相關性達 **$r = +0.57$** `[Cross-Model KV, §4.5, p.7–8]`。
  - 透過將 K 誤差投影至 $\mathbf{Q}_h$ 右奇異向量定義 **K-concentration**（>1 代表誤差集中在注意力讀取的方向），證實 MLP 之所以能在 Ministral 失敗配對救回 **+24.3 至 +36.8 pp**，本質是將誤差重新分配至注意力忽略的子空間（$\Delta \text{K-conc} \approx -2.5$、$\Delta \text{cosine} \approx +0.45$）`[Cross-Model KV, §4.5, Table 4, p.8]`。

## 相關頁面
- [CacheBlend](../papers/cacheblend.md) ｜ [RelayCaching](../papers/relaycaching.md) ｜ [Cross-Model KV Transfer](../papers/cross-model-kv-transfer.md)
- [跨文獻張力與差異彙整](../syntheses/conflicts-and-tensions.md)
- [KV Cache Reuse 領域總覽](../overview.md)
