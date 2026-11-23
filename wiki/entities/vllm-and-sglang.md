---
title: "vLLM 與 SGLang（現代 LLM 推理引擎基線）"
type: "entity"
sources:
  - "raw/01-cacheblend-2405.16444v3.md"
updated: "2026-11-23"
---

# vLLM 與 SGLang

**vLLM**（PagedAttention）與 **SGLang**（RadixAttention）是目前開源界最主流的高吞吐 LLM 推理引擎，也是多數 KV Cache Reuse 研究的實作載體與對照基線：

- **內建 Prefix Caching 機制**：兩者皆支援自動前綴快取，透過區塊雜湊（block hashing）或基數樹（radix tree）跨請求重用完全相同的輸入前綴，且不損害生成品質 `[CacheBlend, §3.2, §5.1, §7.1, p.3, 8, 11]`。
- **在多區塊 RAG 場景的局限**：[CacheBlend](../papers/cacheblend.md) 指出，vLLM 與 SGLang 的 Prefix Caching 僅能重用輸入中的第 1 個 chunk；當同一 chunk 出現於不同前綴之後時，快取會失效或必須儲存多份重複副本，導致在固定儲存空間下 cache miss 率偏高 `[CacheBlend, §3.2, §7.2, p.3, 12]`。
- **實作整合**：CacheBlend 直接基於 vLLM 實作 `fetch_kv`、`prefill_layer` 與 `synchronize` 三大介面以支援非前綴部分重算 `[CacheBlend, §6, p.9]`。

## 相關頁面
- [CacheBlend 論文筆記](../papers/cacheblend.md)
- [KV Cache Reuse 領域總覽](../overview.md)
- [跨論文方法全景對照](../syntheses/kv-reuse-landscape.md)
