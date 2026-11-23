---
title: "KV Deviation Metrics（KV 偏差衡量指標與關鍵位置定位）"
type: "concept"
sources:
  - "raw/01-cacheblend-2405.16444v3.md"
  - "raw/04-relaycaching-2603.13289v1.md"
updated: "2026-11-23"
---

# KV Deviation Metrics（KV 偏差衡量指標與關鍵位置定位）

要做到低成本的[選擇性 KV 重算](./selective-kv-recomputation.md)，核心問題在於：**如何用可觀測的偏差指標，準確抓出對最終輸出品質影響最大的網路層與 token？** 不同場景下的 KV 誤差呈現截然不同的幾何結構。

## 1. 絕對數值／範數偏差（CacheBlend — 靜態多區塊融合）
- [CacheBlend](../papers/cacheblend.md) 定義 token 級 **KV deviation** 為預計算 KV 與完整 Prefill KV 的絕對差 $\Delta_{\text{kv}}(KV_i, KV_i^{\text{full}})[j] = |KV_i[j] - KV_i^{\text{full}}[j]|$，並以 forward attention matrix 的 L2 差作為 **attention deviation** `[CacheBlend, §4.1, Table 1, p.5]`。
- 在靜態 RAG 獨立編碼區塊中（Independent KV），[RelayCaching](../papers/relaycaching.md) 亦證實其 **Value Norm** 會大幅偏離完整 Prefill（僅 0.588），因此基於數值大小／範數偏差的 HKVD 指標在靜態區塊融合場景相當有效 `[RelayCaching, §3.1, Fig. 2, p.3]`。

## 2. 方向性餘弦偏差＋下游影響力（RelayCaching — 動態 Decode-to-Prefill）
- 在多代理 Decode-to-Prefill 場景中，[RelayCaching](../papers/relaycaching.md) 系統性量測四大指標後發現：Key Norm（0.947）、Value Norm（0.926）與 Key Cosine（0.935）皆保持高度一致，唯有 **Value Cosine Similarity（0.800）** 出現顯著方向性擾動 `[RelayCaching, §3.1, Fig. 2, p.3]`。
- **單靠偏差值不夠**：GSM8K 消融實驗顯示，只依 Value Cosine 偏差選 token（$I_{\text{dev}}$）雖可把重用率推上 90.37%，準確率卻從 85.90% 跌至 **79.68%**；必須結合**累計注意力影響分數（$I_{\text{inf-score}}$）**與**段末 10 token 邊界修正（$I_{\text{inf-suffix}}$）**，才能把準確率拉回 **84.84%** 同時維持 **85.35%** 重用率 `[RelayCaching, §4.3, §5.4, Table 3, p.6, 8]`。
- **跨層結構化特徵**：Value Cosine 在深度方向呈 **U 型曲線**（中層最低、淺深層穩定），且相鄰層 token 偏差排名的 Spearman 相關係數進入中層後穩定 **> 0.9**，橫跨 0.6B 至 32B 六款模型皆成立 `[RelayCaching, §3.2–3.3, Appendix A, Fig. 3–4, 9–10, p.3–4, 11–13]`。

## 相關頁面
- [CacheBlend 論文筆記](../papers/cacheblend.md)
- [RelayCaching 論文筆記](../papers/relaycaching.md)
- [跨文獻張力與差異彙整](../syntheses/conflicts-and-tensions.md)
- [KV Cache Reuse 領域總覽](../overview.md)
