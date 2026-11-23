---
title: "RoPE Position Alignment（旋轉位置編碼對齊）"
type: "concept"
sources:
  - "raw/01-cacheblend-2405.16444v3.md"
  - "raw/04-relaycaching-2603.13289v1.md"
  - "raw/05-cross-model-kv-transfer-2608.03893v1.md"
updated: "2026-11-23"
---

# RoPE Position Alignment（旋轉位置編碼對齊）

## 為何 KV 重用必須處理 RoPE？
現代 Transformer LLM 普遍採用 **Rotary Positional Embedding（RoPE）**，將 token 絕對位置 $m$ 透過正交旋轉矩陣 $\mathbf{R}_{\Theta, m}^d$ 編碼進 Query 與 Key 向量（Value 向量不含位置編碼）。當快取的 Key 被移動到新位置或轉移至另一模型時，必須解耦或校正旋轉角度，否則將嚴重破壞長距離注意力與知識推理任務。

## 三篇論文的 RoPE 處理演進
1. **預計算區塊的單次相對旋轉校正（[CacheBlend](../papers/cacheblend.md)）**：
   - 利用 RoPE 內積 $q_{m+l}^\top k_m$ 僅依賴相對距離 $l$ 的性質（Proposition A.1），在 RAG 非前綴區塊拼接時對預存 Key 執行一次相對旋轉矩陣乘法即可校正，延遲開銷幾乎可忽略 `[CacheBlend, Footnote 3, p.6; Appendix A, p.16]`。
2. **Pre-RoPE 儲存＋接力重施旋轉（[RelayCaching](../papers/relaycaching.md)）**：
   - 上游代理於解碼階段直接保存尚未施加位置旋轉的 **Pre-RoPE Decoding KV Cache**；於 Relay Handoff 交棒給下游代理 Prefill 時，再依新位置重新施加 RoPE，避免重複反旋轉 `[RelayCaching, §4.2, Fig. 5, p.5]`。
3. **剝除源 RoPE → 無位置內容空間線性映射 → 重施目標 RoPE（[Cross-Model KV Transfer](../papers/cross-model-kv-transfer.md)）**：
   - 跨模型線性映射若直接擬合在含 RoPE 的 Key 上，位置旋轉會污染跨層 $R^2$ 對角線，並將權重綁死在 1,024-token 校準位置分布 `[Cross-Model KV, §2.3, §3.3, Fig. 2, p.3–5]`。
   - 該論文採完全解耦公式：$\hat{\mathbf{K}}_t = (\mathbf{K}_s \mathbf{R}_{\Theta_s}^{-1}(t)\mathbf{W}_K + \mathbf{b}_K)\mathbf{R}_{\Theta_t}(t)$。因 $\mathbf{R}_\Theta$ 為正交矩陣，反轉精確且成本極低；消融實驗顯示若推論時遺漏重施 RoPE，Qwen3 14B→32B 的 MMLU 會從 78.09% 崩跌至 **25.79%**、GSM8K 從 90.98% 崩跌至 **4.17%**；解耦後則可無縫支援不同 RoPE 參數並推廣至 **32K** 上下文 `[Cross-Model KV, §3.3, §4.3, Table 2, p.5–7]`。

## 相關頁面
- [CacheBlend](../papers/cacheblend.md) ｜ [RelayCaching](../papers/relaycaching.md) ｜ [Cross-Model KV Transfer](../papers/cross-model-kv-transfer.md)
- [KV Cache Reuse 領域總覽](../overview.md)
- [跨論文方法全景對照](../syntheses/kv-reuse-landscape.md)
