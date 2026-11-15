---
name: prefix-caching
description: 跨請求重用「開頭相同」的 KV cache：原理、vLLM 的 block hash 做法、SGLang 的 RadixAttention 做法與實測數字
sources: [S2, S6, S4]
---

# Prefix caching（跨請求重用開頭相同的 KV）

## 為什麼 prefix 可以重用
- [C05] KV cache 的計算只依賴前面的 tokens，所以有相同 prompt prefix 的請求可以重用 KV cache。 [S2]
- [C12] 因此 prefix caching 不會改變模型輸出。 [S6]
- [C29] 但只有「開頭」那一段能重用；若相同內容出現在輸入中間，就不是 prefix。 [S4]

## 做法 A：vLLM Automatic Prefix Caching（block + hash）
- [C10] 每個 block 的 hash 由父 block 的 hash、block 內 tokens 與額外資訊組成，所以 hash 代表「從開頭到這個 block」的整段 prefix。 [S6]
- [C11] 命中就 ref count 加 1；free queue 的 head 是 LRU，配置新 block 時被淘汰；`cache_salt` 混入第一個 block 的 hash 以隔離不同使用者。 [S6]

## 做法 B：SGLang RadixAttention（radix tree）
- [C13] 請求結束後不丟棄 KV，保留在 radix tree；LRU 淘汰最近最少使用的 leaf；每個節點有 reference counter，執行中的請求用到的節點不可淘汰。 [S2]
- [C37] 論文中 KV 以非連續 paged 方式存放，page 大小為 1 個 token；與 continuous batching、paged attention、tensor parallelism 相容。 [S2]
- [C14] cache-aware scheduling：最長共享 prefix 優先；離線時以 DFS 順序可達最佳 hit rate；貪婪排程可能造成 starvation。 [S2]

## 效果（S2 的實測）
- [C15] 最高 6.4× 吞吐、最高 3.7× 延遲降低（對 Guidance、vLLM v0.2.5、LMQL）；hit rate 50%–99%；排程平均達最佳 hit rate 的 96%。 [S2]
- [C16] 沒有可重用 prefix 時，管理成本可忽略：100 個請求 74.3 秒中只花 0.2 秒（< 0.3%）。 [S2]
- [C17] 在 Chatbot Arena 一個月：hit rate 52.4%（LLaVA-NeXT-34B）、74.1%（Vicuna-33B）；Vicuna-33B 首 token 延遲平均降低 1.7×。 [S2]
- [C18] 長輸出的多輪對話幾乎沒有加速，因為 decode 時間主導。 [S2]

## 兩種做法的差異（整理）
| | vLLM APC | SGLang RadixAttention |
|---|---|---|
| 辨識方式 | block hash 鏈 [C10] | radix tree [C13] |
| 淘汰 | free queue head = LRU block [C11] | LRU，先淘汰 leaf [C13] |
| 粒度 | block（以填滿的 block 為單位） [S6] | 論文中 page = 1 token [C37] |
| 排程 | 文件未描述 | cache-aware，最長共享 prefix 優先 [C14] |
