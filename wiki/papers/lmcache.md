---
title: "LMCache：企業級 LLM 推理的高效能分散式 KV Cache 層"
type: "paper"
sources:
  - "raw/03-lmcache-2510.09665v2.md"
updated: "2026-11-23"
---

# LMCache: An Efficient KV Cache Layer for Enterprise-Scale LLM Inference

- **原始來源**：[03-lmcache-2510.09665v2.md](../../raw/03-lmcache-2510.09665v2.md)（`arXiv:2510.09665v2`，2025 年 12 月）
- **作者與單位**：Yuhan Liu*、Jiayi Yao*、Yihua Cheng* 等（Tensormesh Inc.、University of Chicago）
- **開源系統**：[LMCache 系統架構頁](../entities/lmcache-system.md)（`https://github.com/LMCache/LMCache`），亦為 [CacheBlend](./cacheblend.md) 與 [DroidSpeak](./droidspeak.md) 的底層實作載體

## 1. 真實世界趨勢與三大系統挑戰
- **真實遙測統計（5 週企業用量）**：使用者數成長 **23.21×**、總 KV Cache 儲存量成長 **5.57×**，超出 GPU HBM 容量的非 GPU 快取占比快速飆升；且超過 **19%** 使用者對 GPU 以外儲存的 token 平均重用超過 **1.5 次** `[LMCache, §2.2, Fig. 1, 3–4, p.1, 3]`。
- **兩大核心應用場景**：(1) **Context Caching（跨查詢快取卸載）**與 (2) **Prefill–Decode（PD）Disaggregation（跨引擎／跨 GPU 傳輸）**`[LMCache, §1, §2.3, Fig. 2, p.1, 3–4]`。
- **三大系統瓶頸**：
  1. **分頁記憶體下的 I/O 低效**：傳統 `torch.save/load` 速度低於 1 GB/s；而 [vLLM 與 SGLang](../entities/vllm-and-sglang.md) 的 PagedAttention 將 KV 切成 **16–64 KB** 零散小頁（如 Llama-3.1-8B 每頁 62.5 KB = 16 tokens × 1 layer），遠小於打滿網路頻寬所需的 **16 MB**（Table 1：64 KB 僅 4 GB/s，16 MB 達 49 GB/s）或 PCIe 5.0 所需的 1–2 MB `[LMCache, §3.1.1, Table 1, Footnote 2, p.4, 6]`。
  2. **追趕高速演進的推理引擎**：2025 年平均每週發布 15–20 個新開源權重模型（每 4 天一個代表性模型），SWA、MLA 等新注意力核頻繁改變 GPU 記憶體佈局 `[LMCache, §3.1.2, §6, p.4, 8]`。
  3. **欠缺一等公民管理介面**：查詢路由器需要全域 KV 位置進行 cache-aware routing，金融與代理企業亦要求顯式 `pin`、`compress` 與 `move` API `[LMCache, §3.1.3, p.4–5]`。

## 2. 核心架構與最佳化
- **批次化與管線化資料搬運（詳見 [Compute-I/O Pipelining](../concepts/compute-io-pipelining.md)）**：
  - **可組態 Chunk 批次搬運**：預設每 chunk 合併 **256 tokens** 跨層資料，經客製 CUDA kernel 聚合至連續 GPU streaming buffer 再由 DMA 整塊搬運，將 CPU 載入頻寬從 vLLM 原生 88 Gbps 拉升至 **400 Gbps（4.5×）** `[LMCache, §5.1, §8.6, Table 5, p.6, 13]`。
  - **延遲解碼存儲（Delayed Decode Storing）**：解碼過程累積滿一個 chunk 再批次寫出，避免逐 token 小寫入 `[LMCache, §5.1, p.6]`。
  - **雙層計算–I/O 重疊**：逐層 CUDA stream 管線化（僅需單層固定 GPU buffer）＋排隊期間非同步預取（async prefetch），使端到端延遲降低 **1.46×** `[LMCache, §5.2, §8.6, Fig. 13, p.6–7, 14]`。
  - **最小化複製**：多目標寫入採類似 OS PCB 計數器的 **Zero-Copy Reference Counting**；GPU 空閒頁池採三指標（`Start`/`Current`/`End`）**Dynamic Offloading** 平衡重複率與分配停頓 `[LMCache, §5.3, Fig. 7, p.7–8]`。
- **標準化雙介面設計（詳見 [LMCache 系統架構](../entities/lmcache-system.md)）**：
  - **KV Connector API**（7 個 Scheduler／Model Runner 函式，與 vLLM 團隊共同維護），已獲 NVIDIA Dynamo、RedHat llm-d、ByteDance AIBrix、vLLM Production Stack、KServe 採用 `[LMCache, §6, Table 2, p.8–9]`。
  - **Controller API**（集中式 Manager + 每實例 Worker），提供 `lookup`、`move`、`clear`、`pin/unpin`、`compress/decompress` 與 `batched_p2p_lookup` `[LMCache, §7, Table 3, p.9–10]`。

## 3. 關鍵實驗結果與生產經驗
- **單機 CPU Offloading（8×H100，500 GB DRAM，5 模型含 Qwen3-Coder-480B-FP8）**：QPS=1 時 TTFT 降 **1.9–8.1×**、ITL 降 **7%–92%**；相同 TTFT 下吞吐量高於最強基線 **2.3–14×**（整體跨情境最高達 **15×**）`[LMCache, Abstract, §8.2, Fig. 8, p.1, 11]`。
- **企業真實流量回放（Company F & G）**：高 QPS 下 TTFT 降 **3.7–6.8×**、ITL 降 **19%–58%** `[LMCache, §8.3, Fig. 9–10, p.12]`。
- **遠端集中儲存（15 Gbps）與 PD 分離（NVLink）**：遠端儲存吞吐升 **1.3–3×**；PD 分離較 vLLM 原生 NIXL 逐頁傳輸降低平均 TTFT **1.53–1.84×**、平均 ITL **1.12–1.66×**（總時間 3.68 s vs 4.47 s）`[LMCache, §8.4–8.5, §8.6, Fig. 11–12, 14, p.12–14]`。
- **SGLang 整合（Qwen3-32B, 2×H100）**：與 SGLang 原生 CPU offloading 效能相當，但額外提供跨層級與遠端分散儲存能力 `[LMCache, §8.8, Fig. 16, p.15]`。
- **生產現場五大教訓（§9）**：
  1. 現代高速物件儲存（如 S3 Express 近 1 GB/s）使 Company C 遠端載入 KV 反而比重新 Prefill 降低 **22–32% TTFT** `[LMCache, §9, p.15]`。
  2. 滑動視窗 **Context Truncation** 會破壞前綴匹配，使 Company F 快取命中率從 **~85% 腰斬至 ~45%** `[LMCache, §9, p.15]`。
  3. 動態可重用上下文（coding 助理、多輪對話、RAG）使 Company G 實測命中率意外高達 **50%** `[LMCache, §9, p.16]`。
  4. 容器化（Docker/K8s）與「Python + 客製 CUDA 最佳化」比全面重寫 Rust 更有利社群快速迭代（已支援 8+ 新後端與 NVIDIA/AMD/Ascend/TPU 四類加速器）`[LMCache, §9, p.16]`。

> [!WARNING] ⚠️ 跨文獻張力／差異
> - **遠端儲存載入 vs. 重新 Prefill 的延遲交叉點**：LMCache §9 生產案例（Company C）指出現代物件儲存可降低 22–32% TTFT `[LMCache, §9, p.15]`；但同文 §8.7 在 B200 上的敏感度分析顯示，當網路頻寬偏低（**32 Gbps**）時，唯有上下文超過 **256K tokens** 載入才快過重新 Prefill，直到 **64–128 Gbps** 才全面勝出 `[LMCache, §8.7, Fig. 15, p.14–15]`。這意味著「遠端載入一定比較快」並不無條件成立，系統須依網路頻寬與序列長度做自適應決策（詳見 [跨文獻張力與差異彙整](../syntheses/conflicts-and-tensions.md)）。

## 4. 相關頁面
- [LMCache 系統架構](../entities/lmcache-system.md)
- [Compute-I/O Pipelining](../concepts/compute-io-pipelining.md)
- [跨文獻張力與差異彙整](../syntheses/conflicts-and-tensions.md)
- [跨論文方法全景對照](../syntheses/kv-reuse-landscape.md)
