---
name: s2-sglang-radixattention
description: SGLang 論文（NeurIPS 2024）的 RadixAttention：以 radix tree 自動跨請求重用 KV cache、LRU 淘汰、cache-aware 排程與實測數字
sources: [S2]
---

# S2 — SGLang: Efficient Execution of Structured Language Model Programs

- 書目：Zheng et al., NeurIPS 2024；arXiv 2312.07104（v2，2024-06-06）
- 取得方式：WebFetch 全文 `arxiv.org/pdf/2312.07104`（2026-11-15）
- 驗證狀態：**一手、全文已讀**

## 這篇在講什麼
SGLang 是一個執行「多次 LLM 呼叫的程式」的系統，前端語言加上後端 runtime。與本主題相關的是 runtime 裡的 **RadixAttention**：自動、系統化地重用 KV cache。

## 重點（claim）
- [C05] KV cache 的計算只依賴「前面的 tokens」，因此有相同 prompt prefix 的請求可以重用 KV cache，減少重複計算與記憶體。 [S2 §3、附錄 A.1]
- [C13] 既有推論引擎在請求結束後會丟棄 KV cache；RadixAttention 改為把 prompt 與生成結果的 KV 保留在 radix tree 中，用 LRU 淘汰「最近最少使用的 leaf」，每個節點有 reference counter，正在執行的請求用到的節點不可被淘汰。 [S2 §1、§3]
- [C37] 論文中 radix tree 的 KV 以非連續的 paged 方式儲存，page 大小等於 1 個 token；RadixAttention 與 continuous batching、paged attention、tensor parallelism 相容。 [S2 §3]
- [C14] cache-aware scheduling 採「最長共享 prefix 優先」；離線情況下，以 DFS 順序走訪 radix tree 可達最佳 cache hit rate（Theorem 3.1）；貪婪排程可能造成 starvation（論文列為未來工作）。 [S2 §3、§8]
- [C15] 最高 6.4× 吞吐、最高 3.7× 延遲降低（對照 Guidance、vLLM v0.2.5、LMQL，跨多種 workload）；各 benchmark 的 cache hit rate 為 50%–99%；cache-aware 排程平均達到最佳 hit rate 的 96%。 [S2 §6.2]
- [C16] 沒有任何可重用 prefix 時開銷可忽略：跑 100 個請求花 74.3 秒，管理 RadixAttention 資料結構只用 0.2 秒（< 0.3%）。 [S2 §6.3]
- [C17] 在 Chatbot Arena 部署一個月：LLaVA-NeXT-34B 的 hit rate 52.4%、Vicuna-33B 為 74.1%；Vicuna-33B 的首 token 延遲平均降低 1.7×。 [S2 §6.2]
- [C18] multi-turn chat 且輸出很長時幾乎沒有加速：不同對話之間共享少，decode 時間主導；KV 重用主要降低的是 prefix（prefill）時間。 [S2 §6.2]
- [C39] 論文 Related Work 說 PromptCache「可模組化重用 beyond prefix，但準確度最高可能掉 43%」。這是 S2 的說法，與 S3 自己的結論（無明顯準確度損失）不一致，見 `lint/conflicts.md` L3。 [S2 §7]

## 使用時要小心
- 對照組是 **vLLM v0.2.5**（舊版）；論文註記 RadixAttention 之後已部分整合進 vLLM，所以 6.4× 不代表今天與最新 vLLM 的差距。
- 6.4× 是「最高」，不是平均，且包含 compressed FSM 等非 KV 重用的優化。簡報敘述必須寫「最高」並指明是多種 workload 的整體結果。
- 網路上轉述的 10×、5× 與「vLLM 0 hit rate」等表格不在論文中，不採用（見 `lint/conflicts.md` L1）。
