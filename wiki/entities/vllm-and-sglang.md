---
title: "vLLM 與 SGLang（現代 LLM 推理引擎基線）"
type: "entity"
sources:
  - "raw/01-cacheblend-2405.16444v3.md"
  - "raw/03-lmcache-2510.09665v2.md"
updated: "2026-11-23"
---

# vLLM 與 SGLang

**vLLM**（PagedAttention）與 **SGLang**（RadixAttention）是目前開源界最主流的高吞吐 LLM 推理引擎，也是多數 KV Cache Reuse 研究的實作載體與對照基線：

- **內建 Prefix Caching 機制**：兩者皆支援自動前綴快取，跨請求重用完全相同的輸入前綴 `[CacheBlend, §3.2, §7.1, p.3, 11]`。
- **在多區塊 RAG 場景的局限**：[CacheBlend](../papers/cacheblend.md) 指出，Prefix Caching 僅能重用輸入中的第 1 個 chunk；當同一 chunk 出現於不同前綴之後時快取會失效 `[CacheBlend, §3.2, §7.2, p.3, 12]`。
- **分頁記憶體對跨層級／跨節點搬運的挑戰**：[LMCache](../papers/lmcache.md) 指出，vLLM 與 SGLang 的分頁記憶體將 KV 切分為 **16–64 KB**（如 vLLM 在 Llama-3.1-8B 上採 16 tokens／層 = 62.5 KB）的小頁，雖然提升 GPU 記憶體利用率，但原生逐頁 CPU offloading 僅達 **88 Gbps**（對比 LMCache chunk 搬運 **400 Gbps**），且原生 NIXL 逐頁 PD 分離傳輸效率較低（平均 TTFT 比 LMCache 慢 1.53–1.84×），亦缺乏跨機分層儲存支援 `[LMCache, §3.1.1, §3.2, §8.5–8.6, §8.8, Table 5, p.4–5, 13, 15]`。
- **標準化整合**：vLLM 團隊與 [LMCache 系統](../entities/lmcache-system.md) 團隊共同維護 KV Connector API，實現零侵入式（out-of-tree）掛載；SGLang 亦已整合 LMCache 作為多層級外部儲存後端 `[LMCache, §6, §8.8, p.8–9, 15]`。

## 相關頁面
- [CacheBlend 論文筆記](../papers/cacheblend.md)
- [LMCache 論文筆記](../papers/lmcache.md)
- [LMCache 系統架構](../entities/lmcache-system.md)
- [KV Cache Reuse 領域總覽](../overview.md)
- [跨論文方法全景對照](../syntheses/kv-reuse-landscape.md)
