---
name: s6-vllm-automatic-prefix-caching
description: vLLM 官方設計文件 Automatic Prefix Caching：以 block hash 鏈做 prefix 重用、ref count 與 free queue 淘汰、cache_salt 隔離
sources: [S6]
---

# S6 — vLLM Design Doc: Automatic Prefix Caching

- 位置：`docs.vllm.ai/en/latest/design/prefix_caching/`
- 取得方式：搜尋結果中的文件原文片段，加上 WebFetch 對該頁的擷取（2026-11-15）。**注意：WebFetch 這次回傳的是工具產生的擷取摘要，不是全文原文。** 下列 claim 都有對應的原文片段佐證，或標註為「僅擷取」。
- 驗證狀態：一手（官方文件），部分為擷取

## 重點（claim）
- [C10] APC 以 hash 辨識可重用的 KV block：每個 block 的 hash 由「父 block 的 hash、這個 block 的 tokens、額外 hash（例如 LoRA ID；多模態輸入會帶入圖片 hash）」組成，因此一個 block 的 hash 代表從開頭到它為止的整段 prefix。 [S6 Overview/Hashing，原文片段已確認]
- [C11] 命中時，被重用的 block 的 reference count 加 1，並從 free queue 移除避免被淘汰；配置新 block 時從 free queue 的 head 取出，那就是 LRU block，若它是快取 block 就會被 evict；請求結束後釋放的 block 以相反順序放到 queue 尾端，所以請求的最後一個 block 先被淘汰。`cache_salt` 會被混進第一個 block 的 hash，只有 salt 相同的請求才能重用，用來隔離不同使用者。 [S6 Operations、Cache Isolation；free queue 順序與 cache_salt 目的為擷取內容]
- [C12] Prefix caching 不會改變模型輸出（文件稱它幾乎是免費的午餐）。預設 hash 演算法自 v0.11 起為 sha256；舊版的 hash key 不保證無碰撞。 [S6]

## 使用時要小心
- vLLM 以 **block** 為單位比對（block 要填滿才會被快取），與 S2 論文中 RadixAttention 的 token 級 page（page 大小 1）粒度不同。第三方文件顯示 SGLang 現行實作的 page 大小可設定，表示實作已隨時間演進，不要把論文當作現行程式碼的描述。見 `lint/conflicts.md` L6。
