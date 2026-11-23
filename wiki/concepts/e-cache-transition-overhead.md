---
title: "E-Cache Transition Overhead（E 快取切換開銷與誤差傳播）"
type: "concept"
sources:
  - "raw/02-droidspeak-2411.02820v3.md"
updated: "2026-11-23"
---

# E-Cache Transition Overhead（E 快取切換開銷與誤差傳播）

## 什麼是 E Cache？
在 Transformer 每一層開頭，輸入 token 的隱藏狀態向量（embedding vector，記為 $E$）會被線性投影為 $Q, K, V$。[DroidSpeak](../papers/droidspeak.md) 將每一層的 $K, V$ 稱為 **KV cache**，將該層輸入的隱藏狀態 $E$ 稱為 **E cache** `[DroidSpeak, §2.1, Fig. 2, p.2]`。

## 為何「從重用切回重算」代價高昂？
當模型在某一層直接重用發送端的 KV Cache 時，該層只輸出最後一個生成 token 的狀態，無法提供完整上下文給下一層；因此一旦後續某個**轉換層（transition layer）**想從「重用 KV」切換回「重新計算 KV」，接收端必須從發送端載入該層完整上下文的 **E cache** 作為重算起點 `[DroidSpeak, §4.1, Fig. 9, p.6]`。這帶來雙重瓶頸：

1. **容量與傳輸開銷（Efficiency Challenge）**：
   - 現代 LLM 廣泛採用 GQA（Grouped-Query Attention）壓縮 KV head 數量，但 E cache 仍維持完整隱藏維度。
   - E cache 體積在 Mistral-7B／Llama-3-8B 上高達 KV Cache 的 **2×**，在 Llama-3.1-70B 上更達 **4×**，跨節點儲存與傳輸成本遠高於單純傳送 KV Cache `[DroidSpeak, §4.1, p.6–7]`。
2. **累積誤差放大（Accuracy Challenge）**：
   - 發送端（baseline model）的 E cache 本身就與接收端（specialized model）存在偏差；每多一次 `reuse → recompute` 切換，就會再次注入外部 E cache 誤差並傳播至後續所有層。
   - 實驗證實，在相同重算層數下，只重算散落關鍵層（多次切換）的 F1 分數始終遜於重算**單一連續區塊**（至多一次切換）`[DroidSpeak, §4.1, Fig. 10–11, p.7]`。

## 工程解法
[DroidSpeak](../papers/droidspeak.md) 因此採用 `recompute → reuse → recompute → reuse` 連續區間設計，將 `reuse → recompute` 切換次數嚴格限制在**最多 1 次**，透過離線帕累托剖析找出最小連續重算區塊 `[DroidSpeak, §4.2–4.3, p.7–8]`。

## 相關頁面
- [DroidSpeak 論文筆記](../papers/droidspeak.md)
- [Selective KV Recomputation](./selective-kv-recomputation.md)
- [KV Cache Reuse 領域總覽](../overview.md)
