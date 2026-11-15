---
name: index
description: KV Cache LLM Wiki 首頁：主題、閱讀順序、頁面清單與來源狀態
sources: [S1, S2, S3, S4, S5, S6]
---

# KV Cache LLM Wiki

**主題**：LLM 推論時的 KV cache，以及跨請求重用 KV 的各種做法（記憶體管理、prefix caching、非 prefix 重用、商用 API）。
**讀者**：沒有 LLM 推論背景的人。
**建立日期**：2026-11-15。規則見 [schema](schema.md)。

## 建議閱讀順序
1. [kv-cache](concepts/kv-cache.md) — 是什麼、為什麼能加速、代價
2. [memory-and-paging](concepts/memory-and-paging.md) — 記憶體問題與 PagedAttention
3. [prefix-caching](concepts/prefix-caching.md) — 開頭相同就重用（vLLM APC、RadixAttention）
4. [non-prefix-reuse](concepts/non-prefix-reuse.md) — 不在開頭怎麼辦（Prompt Cache、CacheBlend）
5. [api-prompt-caching](concepts/api-prompt-caching.md) — API 的 prompt caching 怎麼用
6. [terminology](concepts/terminology.md) — 容易混淆的術語

## 來源（6 篇，皆為一手）
| ID | 來源 | 類型 | 驗證狀態 |
|---|---|---|---|
| S1 | [PagedAttention / vLLM](sources/s1-pagedattention-vllm.md)（SOSP 2023） | 論文 | 原文片段；部分數字僅擷取，未採用 |
| S2 | [SGLang / RadixAttention](sources/s2-sglang-radixattention.md)（NeurIPS 2024） | 論文 | 全文 |
| S3 | [Prompt Cache](sources/s3-prompt-cache.md)（MLSys 2024） | 論文 | 全文 |
| S4 | [CacheBlend](sources/s4-cacheblend.md)（EuroSys 2025） | 論文 | 全文 |
| S5 | [Anthropic prompt caching](sources/s5-anthropic-prompt-caching.md) | 官方文件 | 全文（2026-11-15 取得） |
| S6 | [vLLM Automatic Prefix Caching](sources/s6-vllm-automatic-prefix-caching.md) | 官方文件 | 部分為擷取摘要 |

## 品質控管
- 主張帳本：[claims.json](claims.json)（43 條，標示驗證狀態）
- 衝突紀錄：[lint/conflicts.md](lint/conflicts.md)（8 項）
- 檢查器：`tools/check.py`（wiki lint 與簡報逐頁檢查）
- 執行紀錄：[logs/run-001.md](logs/run-001.md)
