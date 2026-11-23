# 證據卡 03：LMCache

- **唯一來源頁**：`wiki/papers/lmcache.md`（嚴禁混入其他來源）
- **真實趨勢與痛點**：
  - 企業 5 週遙測：使用者數增 **23.21×**、KV 儲存量增 **5.57×**，非 GPU 快取遠超 HBM；**>19%** 使用者對 GPU 外 token 重用逾 **1.5×** `[LMCache, §2.2, Fig. 1, 3–4, p.1, 3]`。
  - PagedAttention 的 **16–64 KB** 零散小頁（如 Llama-3.1-8B 每頁 62.5 KB）導致網路頻寬嚴重閒置（Table 1：64 KB 僅 **4 GB/s** vs 16 MB 達 **49 GB/s**）`[LMCache, §3.1.1, Table 1, p.4]`。
  - 2025 年每週推出 15–20 個新模型，推理引擎快速變動且欠缺管理 API `[LMCache, §3.1.2–3.1.3, p.4–5]`。
- **核心架構與系統最佳化**：
  - **Chunk 級批次搬運（預設 256 tokens）**：以客製 CUDA kernel 聚合至連續 streaming buffer 再由 DMA 傳輸，CPU 載入頻寬達 **400 Gbps**（對比 vLLM 原生 **88 Gbps**，快 **4.5×**）`[LMCache, §5.1, §8.6, Table 5, p.6, 13]`。
  - **雙層重疊與零複製**：Layer-wise Pipelining + Async Prefetch（降 E2E 延遲 **1.46×**）；Zero-Copy Reference Counting + 三指標 Dynamic Offloading `[LMCache, §5.2–5.3, §8.6, Fig. 7, 13, p.6–8, 14]`。
  - **雙標準化介面**：KV Connector API（獲 NVIDIA Dynamo、RedHat llm-d、ByteDance AIBrix、vLLM Production Stack、KServe 採用）＋ Controller API（`lookup`、`move`、`pin/unpin`、`compress`、`p2p`）`[LMCache, §6–7, Table 2–3, p.8–10]`。
- **關鍵數據與生產教訓**：
  - 單機 CPU Offloading：TTFT 降 **1.9–8.1×**、ITL 降 **7%–92%**、吞吐升 **2.3–14×**（跨情境最高 **15×**）；企業真實流量 TTFT 降 **3.7–6.8×**、ITL 降 **19%–58%** `[LMCache, Abstract, §8.2–8.3, Fig. 8–10, p.1, 11–12]`。
  - PD 分離較 vLLM 原生 NIXL 降平均 TTFT **1.53–1.84×**、ITL **1.12–1.66×** `[LMCache, §8.5, Fig. 12, p.13–14]`。
  - 生產教訓：高速物件儲存（Company C）可降 **22–32% TTFT**，但 32 Gbps 低頻寬下須 >**256K tokens** 才快過 Prefill；Context Truncation 使 Company F 命中率從 **~85% 跌至 ~45%** `[LMCache, §8.7, §9, Fig. 15, p.14–15]`。
