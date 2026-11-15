---
name: terminology
description: KV cache 領域容易混淆的術語表：KV cache、prefix caching、Prompt Cache 與 prompt caching、PagedAttention、RadixAttention、TTFT 等
sources: [S1, S2, S3, S4, S5, S6]
---

# 術語表（Wiki 內統一用法）

| 術語 | 在本 Wiki 指什麼 | 來源 |
|---|---|---|
| **KV cache** | 單一請求生成過程中，存起來重用的每個 token 的 key / value [C01] | S3 |
| **prefill / decode** | 先處理整個輸入並建立 KV cache；之後一次生成一個 token [C03] | S3 |
| **TTFT** | 時間到第一個 token；prefill 延遲決定它 [C41] | S4 |
| **PagedAttention** | KV cache 的**記憶體排法**：切成固定大小 block，可不連續 [C08] | S1 |
| **prefix caching** | **跨請求**重用「輸入開頭相同」的 KV [C05] | S2、S4、S6 |
| **Automatic Prefix Caching (APC)** | vLLM 的 prefix caching 實作，用 block hash [C10] | S6 |
| **RadixAttention** | SGLang 的 prefix caching 實作，用 radix tree [C13] | S2 |
| **Prompt Cache**（大寫、專有名詞） | S3 論文提出的系統：以 schema 做**非 prefix** 的模組化重用 [C25] | S3 |
| **prompt caching**（小寫、功能名） | 商用 API 的功能，快取的是 prefix，以 `cache_control` 控制 [C19] | S5 |
| **full KV reuse** | 直接拼接各 chunk 預先算好的 KV，忽略 cross-attention [C29] | S4 |
| **CacheBlend** | 重用 KV 後再選擇性重算約 15% token [C30] | S4 |

## 容易混淆的地方
- [C36] **Prompt Cache**（S3 的系統，非 prefix、模組化）與 **prompt caching**（S5 的 API 功能，prefix 式）只差大小寫與一個字母，但是兩個東西。這是本 Wiki 對 S3 與 S5 的整理，不是任一來源的原文。 [S3][S5]
- **PagedAttention 是記憶體排法，prefix caching 是重用策略**；它們屬於不同層次，S2 說 RadixAttention 與 paged attention 相容。 [C37][S2]
- 「快取」不等於「變快」：Prompt Cache 只降 TTFT [C26]，長輸出的多輪對話幾乎沒加速 [C18]。
