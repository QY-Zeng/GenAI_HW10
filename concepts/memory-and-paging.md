---
name: memory-and-paging
description: KV cache 吃記憶體的問題與 PagedAttention 的解法（把 OS 分頁用到 KV cache），以及它與 prefix caching 的關係
sources: [S1, S3, S2]
---

# KV cache 的記憶體問題與 PagedAttention

## 問題
- [C06] 13B 模型在 40GB A100 上，約 65% 記憶體是不變的權重；KV cache 的管理方式決定最大 batch size。 [S1]
- [C07] 每個 token 的 KV cache 對 Llama 70B 約 2.5 MB（16-bit），所以長 context 很吃記憶體。 [S3]

## 解法：PagedAttention
- [C08] 把 KV cache 切成固定大小的 block，block 不必連續；block = page、token = byte、request = process。 [S1]
- [C09] 以此做到接近零浪費，吞吐比 FasterTransformer、Orca 高 2–4×（同等延遲），不影響準確度。 [S1]
- [C40] 並能在 block 粒度做共享，跨序列甚至跨請求。 [S1]

## 與 prefix caching 的關係
- PagedAttention 解決「記憶體怎麼排」，prefix caching 解決「哪些 KV 可以重用」。兩者可以組合：S2 說 RadixAttention 與 paged attention 相容 [C37]；S3 也指出 paged attention 可用來在 batch 內共享同一個 module 的指標以降低冗餘 [C43]。 [S2][S3]
