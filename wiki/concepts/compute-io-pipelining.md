---
title: "Compute-I/O Pipelining（計算與 I/O 管線化）"
type: "concept"
sources:
  - "raw/01-cacheblend-2405.16444v3.md"
updated: "2026-11-23"
---

# Compute-I/O Pipelining（計算與 I/O 管線化）

## 核心概念
KV Cache 容量動輒數十至數百 GB，必須卸載（offload）至 CPU DRAM、NVMe SSD 甚至遠端儲存。若採同步阻塞載入，搬運延遲會直接疊加在 [TTFT](../entities/llm-serving-metrics.md) 上。**Compute-I/O Pipelining** 將「GPU 上的逐層計算」與「下一層 KV Cache 從較慢儲存裝置載入 GPU」重疊執行，將 I/O 或重算延遲互相隱藏。

## 逐層載入與選擇性重算管線（CacheBlend）
[CacheBlend](../papers/cacheblend.md) 指出：只要單層選擇性重算延遲 $T_{\text{recompute}}$ 小於或等於單層 KV 載入延遲 $T_{\text{load}}$，透過雙執行緒逐層管線化（第 $i$ 層執行 `prefill_layer`，同時第 $i+1$ 層執行 `fetch_kv`，計算前以 `synchronize()` 同步），即可讓重算額外延遲完全歸零 `[CacheBlend, §5, §6, p.7–9]`：

- **案例對比**：4K 上下文於 NVMe SSD 上，Llama-7B 重算 15% tokens 需 3 ms／層、載入需 16 ms／層（重算完全被隱藏）；但 Llama-70B 重算 15% 需 7 ms／層、載入僅 4 ms／層（載入不足以完全隱藏重算）`[CacheBlend, §5, p.8]`。
- **Loading Controller 決策公式**：
  - 給定儲存裝置時，選取 $\max(r\%, r^*\%)$（其中 $r^*$ 預設 15% 保底品質，而 $r\%$ 滿足 $T_{\text{recompute}} = T_{\text{load}}$）`[CacheBlend, §5.1, Fig. 10(a), p.8]`。
  - 給定固定重算比例（15%）時，從候選儲存層中挑選滿足 $T_{\text{recompute}} \ge T_{\text{load}}$ 且成本 $C_{\text{store}}$ 最低的裝置（例如較便宜的 SSD 而非昂貴的 GPU HBM）`[CacheBlend, §5.1, Fig. 10(b), p.8]`。

## 相關頁面
- [CacheBlend 論文筆記](../papers/cacheblend.md)
- [Selective KV Recomputation](./selective-kv-recomputation.md)
- [LLM 推理系統效能指標](../entities/llm-serving-metrics.md)
- [KV Cache Reuse 領域總覽](../overview.md)
