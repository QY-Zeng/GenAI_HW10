---
title: "Compute-I/O Pipelining（計算與 I/O 管線化）"
type: "concept"
sources:
  - "raw/01-cacheblend-2405.16444v3.md"
  - "raw/03-lmcache-2510.09665v2.md"
updated: "2026-11-23"
---

# Compute-I/O Pipelining（計算與 I/O 管線化）

## 核心概念
KV Cache 容量動輒數十至數百 GB，遠超 GPU HBM 上限（[LMCache](../papers/lmcache.md) 企業遙測顯示非 GPU 快取占比快速超過 GPU 記憶體 `[LMCache, §2.2, Fig. 3, p.3]`），必須卸載至 CPU DRAM、NVMe SSD 或遠端儲存。**Compute-I/O Pipelining** 將 GPU 上的逐層計算與較慢儲存層的 KV 搬運重疊，避免 I/O 直接疊加至 [TTFT](../entities/llm-serving-metrics.md)。

## 1. 逐層載入與選擇性重算重疊（CacheBlend）
[CacheBlend](../papers/cacheblend.md) 證明只要單層選擇性重算延遲 $T_{\text{recompute}} \le T_{\text{load}}$，透過雙執行緒將第 $i$ 層 `prefill_layer` 與第 $i+1$ 層 `fetch_kv` 重疊，即可完全隱藏重算開銷 `[CacheBlend, §5–6, p.7–9]`：
- 4K 上下文於 NVMe SSD 上，Llama-7B 重算 15% 僅需 3 ms／層、載入需 16 ms／層（完全隱藏）；Llama-70B 重算需 7 ms／層、載入 4 ms／層（無法完全隱藏）`[CacheBlend, §5, p.8]`。
- Loading Controller 依 $\max(r\%, r^*\%)$（$r^* = 15\%$）決定重算比例，或於固定 15% 下挑選滿足 $T_{\text{recompute}} \ge T_{\text{load}}$ 的最便宜儲存層 `[CacheBlend, §5.1, Fig. 10, p.8]`。

## 2. 企業級批次搬運、多層級管線與零複製（LMCache）
[LMCache](../papers/lmcache.md) 進一步解決分頁記憶體（16–64 KB 小頁）造成頻寬嚴重閒置的系統瓶頸（Table 1：64 KB 僅 4 GB/s vs. 16 MB 達 49 GB/s `[LMCache, §3.1.1, Table 1, p.4]`）：
- **Chunk 級批次聚合（預設 256 tokens）**：透過客製 CUDA kernel 將零散頁面聚合進連續 GPU streaming buffer，再以 DMA 整塊傳輸，使 CPU 載入頻寬從 vLLM 原生 **88 Gbps** 暴增至 **400 Gbps（4.5×）** `[LMCache, §5.1, §8.6, Table 5, p.6, 13]`。
- **兩層重疊機制**：(1) **Layer-wise Pipelining** 使用獨立 CUDA streams 與固定單層大小 GPU buffer 重疊第 $i$ 層計算與第 $i+1$ 層載入；(2) **Async Compute & Prefetch** 利用請求排隊空檔預取遠端快取，並使端到端延遲縮減 **1.46×** `[LMCache, §5.2, §8.6, Fig. 13, p.6–7, 14]`。
- **最小化資料複製**：多目標寫入採用 **Zero-Copy Reference Counting**；GPU 空閒頁池採 `Start`/`Current`/`End` 三指標 **Dynamic Offloading** 平衡重複率與記憶體分配停頓 `[LMCache, §5.3, Fig. 7, p.7–8]`。
- **自適應載入交叉點**：B200 敏感度實驗顯示，32 Gbps 網路下需超過 **256K tokens** 載入才快於重算，64–128 Gbps 則全長度皆勝出 `[LMCache, §8.7, Fig. 15, p.14–15]`。

## 相關頁面
- [CacheBlend 論文筆記](../papers/cacheblend.md)
- [LMCache 論文筆記](../papers/lmcache.md)
- [LMCache 系統架構](../entities/lmcache-system.md)
- [Selective KV Recomputation](./selective-kv-recomputation.md)
- [KV Cache Reuse 領域總覽](../overview.md)
