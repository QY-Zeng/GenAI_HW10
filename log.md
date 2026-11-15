---
name: log
description: Ingest 與討論紀錄：每篇來源在寫入前的討論結論（先討論、後生成）與生成後的結果
sources: [S1, S2, S3, S4, S5, S6]
---

# Ingest 紀錄（2026-11-15）

> 「討論」是寫入 Wiki 前，我先決定要抽什麼、要小心什麼；「生成」是實際寫了什麼。此處為摘要版。

| # | 來源 | 討論（寫入前） | 生成（寫入後） |
|---|---|---|---|
| 1 | S3 Prompt Cache | 這篇同時是「KV cache 基礎」與「非 prefix 重用」的來源；名字和 API 的 prompt caching 太像，需要在術語表分開。數字有摘要與 §5.2 兩組，先都記。 | s3 來源頁；C01–C04、C07、C25–C28、C35、C43；L2、L3 |
| 2 | S2 SGLang | 重點只取 RadixAttention，不寫語言前端。搜尋結果的二手數字與論文不同，要以全文為準。 | s2 來源頁；C05、C13–C18、C37、C39；L1、L6 |
| 3 | S4 CacheBlend | 要回答「prefix caching 不夠用時怎麼辦」。比較基線有兩種（full recompute 與 prefix caching），必須分清楚。 | s4 來源頁；C29–C34、C41；L4 |
| 4 | S5 Anthropic 文件 | 廠商文件會變，必須標取得日；不得從 API 行為推論底層實作。 | s5 來源頁；C19–C24；L5 |
| 5 | S6 vLLM APC | 本來想詳述淘汰順序，但抓到的是工具摘要不是原文，降級為 extract-only。 | s6 來源頁；C10–C12；L8 |
| 6 | S1 PagedAttention | 定位是「記憶體排法」，不是「重用策略」。2–4× 的基線是舊系統。部分數字無法在原文片段重現，不採用。 | s1 來源頁；C06、C08、C09、C38、C40、C42；L7 |

概念頁：kv-cache、memory-and-paging、prefix-caching、non-prefix-reuse、api-prompt-caching、terminology。
