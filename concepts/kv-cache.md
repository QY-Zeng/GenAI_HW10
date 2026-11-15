---
name: kv-cache
description: KV cache 是什麼、prefill 與 decode 兩階段、為什麼可以快取而不影響準確度、以及記憶體代價（初學者主頁）
sources: [S1, S3, S4]
---

# KV cache（單一請求內的快取）

## 一句話
LLM 一次生成一個 token；生成每個新 token 都要用到「前面所有 token 的 key 與 value」。把這些 K、V 算一次就存起來、之後直接取用，就是 KV cache。

## 不用快取會怎樣
- [C02] 自回歸生成時，若不快取，每一步模型都以整個 prompt 加上已生成的 tokens 當輸入，attention states 全部重算。 [S3]

## 用了快取會怎樣
- [C01] 每個 token 的 K、V 只算一次，之後重用。 [S3]
- [C03] 先對輸入算好 K、V 並存起來（prefill phase）；之後每一步沿用快取，只算新 token 的 K、V 並附加進去（decode）。 [S3]
- [C35] 每一步的運算量約由 6nd²+4n²d 降為 6d²+4nd（n：序列長度，d：hidden size）。 [S3]
- [C04] 在因果語言模型中，使用 KV cache 不影響準確度，因為位置 i 的 attention 只依賴它前面的 tokens。 [S3]

## prefill 為什麼會慢
- [C33] 4K tokens 的輸入，在單張 A40 上 Llama-34B 的 prefill 約需 3 秒、Llama-70B 約 6 秒。 [S4]
- [C41] 使用者等到第一個字出現的時間稱為 TTFT；prefill 的延遲決定 TTFT。 [S4]

## 代價：記憶體
- [C06] 以 13B 模型跑在 40GB 的 A100 為例，約 65% 的記憶體是不變的模型權重；KV cache 隨每個請求配置與釋放，它怎麼被管理決定了最大 batch size。 [S1]
- [C07] 每個 token 的 KV cache 約佔：Falcon 1B 0.18 MB、Llama 7B 0.50 MB、Llama 70B 2.5 MB（16-bit）；Llama 70B 快取一個 1K tokens 的片段要 2.5 GB。 [S3]

## 與其他概念的關係
- 記憶體怎麼排 → [[memory-and-paging]]
- 跨請求重用開頭相同的部分 → [[prefix-caching]]
- 重用不在開頭的片段 → [[non-prefix-reuse]]
- 商用 API 的版本 → [[api-prompt-caching]]
- 名詞辨析 → [[terminology]]
