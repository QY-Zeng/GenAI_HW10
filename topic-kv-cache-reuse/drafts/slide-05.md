# Slide 05：LMCache：走出單張 GPU 的企業級 KV Cache 層

- **頁碼**：05 / 12
- **來源卡片**：`cards/card-03-lmcache.md`
- **Wiki 出處**：`wiki/papers/lmcache.md`

## 核心內容
- **企業實測痛點**：5 週遙測使用者增 **23.21×**、KV 儲存量增 **5.57×** 遠超 GPU HBM；但 PagedAttention 的 **16–64 KB** 零散小頁嚴重拖垮頻寬（64 KB 僅 **4 GB/s** vs 16 MB 達 **49 GB/s**）`[LMCache, §2.2, §3.1.1, Table 1, Fig. 1, 3, p.1, 3–4]`。
- **三大系統工程支柱**：
  1. **Chunk 批次搬運（預設 256 tokens）**：以客製 CUDA kernel 聚合成連續 streaming buffer 再由 DMA 搬運，CPU 載入頻寬達 **400 Gbps**（較 vLLM 原生 **88 Gbps** 快 **4.5×**）`[LMCache, §5.1, §8.6, Table 5, p.6, 13]`。
  2. **雙層管線＋零複製**：逐層 CUDA stream 重疊＋排隊非同步預取（E2E 降 **1.46×**），搭配參考計數 Zero-Copy 與三指標 Dynamic Offloading `[LMCache, §5.2–5.3, §8.6, Fig. 7, 13, p.6–8, 14]`。
  3. **雙標準化介面**：KV Connector API（獲 NVIDIA Dynamo、llm-d、AIBrix、KServe 採用）＋ Controller API（`lookup`/`move`/`pin`/`compress`）`[LMCache, §6–7, Table 2–3, p.8–10]`。
- **核心成效**：單機 CPU Offloading 降 **1.9–8.1×** TTFT、升 **2.3–14×** 吞吐（跨情境最高 **15×**）；PD 分離較 vLLM 原生降 **1.53–1.84×** TTFT `[LMCache, Abstract, §8.2, §8.5, Fig. 8, 12, p.1, 11, 13–14]`。
- **頁尾出處**：`wiki/papers/lmcache.md`｜`[LMCache, §2.2–8.6, Table 1, 5, Fig. 8, 12–13, p.3–14]`
