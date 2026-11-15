---
name: s4-cacheblend
description: CacheBlend 論文（EuroSys 2025）：RAG 多 chunk 情境下，重用非 prefix 的 KV cache 並選擇性重算約 15% token 以保住品質
sources: [S4]
---

# S4 — CacheBlend: Fast LLM Serving for RAG with Cached Knowledge Fusion

- 書目：Yao et al.（University of Chicago 等）；EuroSys 2025（Microsoft Research 頁面標註 Best Paper Award）；arXiv 2405.16444（v2，2024-06-03）
- 取得方式：WebFetch 全文（Princeton 課程提供的 PDF，內容為 arXiv v2）與 Microsoft Research 發表頁（2026-11-15）。直接抓 arXiv 摘要頁一度失敗（URL 未曾出現在搜尋結果中，被工具拒絕），改抓上述兩個頁面。
- 驗證狀態：**一手、全文已讀**

## 重點（claim）
- [C33] prefill 很慢：4K tokens 的輸入，在單張 A40 上 Llama-34B 約需 3 秒、Llama-70B 約 6 秒。 [S4 §2]
- [C29] Prefix caching 只能重用輸入開頭那一段；RAG 會把多個檢索到的 chunk 放進輸入，只有第一個 chunk 是 prefix，其餘無法重用。Full KV reuse（如 S3 的做法）雖然快，卻忽略 chunk 之間的 cross-attention，可能答錯。 [S4 §1、§3]
- [C30] CacheBlend：重用預先算好的 KV cache，再「選擇性重算」少量 token（KV deviation 高的 HKVD tokens）。預設重算比例約 15%；論文經驗上 10–20% 通常足以保住品質；重算與載入下一層 KV 以 pipeline 重疊，因此不增加延遲。 [S4 §1、§4、§5]
- [C31] 結果：相較 full KV recompute，TTFT 降低 2.2–3.3×、吞吐提升 2.8–5×，品質下降不超過 0.01–0.03；同樣 TTFT 下吞吐最高比 prefix caching 高 3.3×（prefix caching 的基線做了「無載入延遲」的理想化假設，對它有利）。 [S4 摘要、§7]
- [C32] 實驗：Mistral-7B、Yi-34B、Llama-70B 三個模型，2WikiMQA、Musique、SAMSum、MultiNews 四個資料集，實作於 vLLM 之上。 [S4 §7.1]
- [C34] 限制：論文的觀察（如 attention 稀疏性）不一定適用 Mamba、Griffin 等非 transformer 架構；也未在 DistServe 等最新引擎上評估。 [S4 §9]

## 使用時要小心
- 同一篇論文的引言寫「相較 prefix caching 降低 TTFT 2.2–3.3×、三個資料集」，摘要與 §7 寫「相較 full KV recompute、四個資料集」。以 §7 的拆分為準，見 `lint/conflicts.md` L4。
- S4 對 S3 的評語（忽略 cross-attention 導致品質下降）是 S4 的立場，S3 自己的實驗與此不同。
