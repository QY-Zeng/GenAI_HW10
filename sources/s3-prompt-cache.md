---
name: s3-prompt-cache
description: Prompt Cache 論文（MLSys 2024）：以 schema 與 prompt module 做「非 prefix」的 attention state 重用；含 KV cache 基礎說明、TTFT 數字、記憶體成本
sources: [S3]
---

# S3 — Prompt Cache: Modular Attention Reuse for Low-Latency Inference

- 書目：Gim, Chen, Lee, Sarda, Khandelwal, Zhong；MLSys 2024；arXiv 2311.04934（v2，2024-04-25）
- 取得方式：WebFetch 全文 `arxiv.org/pdf/2311.04934v2`（2026-11-15）
- 驗證狀態：**一手、全文已讀**
- 名稱注意：這是**一個系統的名字**（Prompt Cache），不是「API 的 prompt caching 功能」，兩者不同，見 `concepts/terminology.md`。

## 重點（claim）
- [C02] 自回歸生成時，若不快取，每一步模型都以「整個 prompt 加上已生成的 tokens」當輸入，attention states 重算。 [S3 §2.1、§2.2]
- [C01] KV Cache：每個 token 的 key / value 只算一次，之後重用；每次生成只需計算新 token 的 K、V。 [S3 §1、§2.2]
- [C03] 先對輸入算好 attention states 並存起來，稱為 prefill phase；後續每一步沿用快取，再把新 token 的 K、V 附加進去。 [S3 §2.2]
- [C35] 每一步的運算量約由 6nd²+4n²d 降為 6d²+4nd（n 為序列長度、d 為 hidden size）。 [S3 §2.2]
- [C04] 在因果（causal）語言模型中使用 KV Cache 不影響準確度，因為位置 i 的 attention 只依賴它前面的 tokens。 [S3 §2.2]
- [C25] Prompt Cache：用 schema（Prompt Markup Language, PML）定義可重用文字段（prompt modules），先算好 attention states 存起來，不同 prompt 命中時直接取用。難點是位置編碼讓 attention states 與位置有關；論文的觀察是 LLM 能處理不連續的 position IDs。 [S3 §1、§3]
- [C28] 各 module 獨立編碼，跨 module 的 attention 被遮蔽（masking effect）：module 語意獨立時可能降低雜訊，相依時品質可能變差。 [S3 §3.3]
- [C27] TTFT 改善：摘要與結論寫「GPU 最高 8×、CPU 最高 60×」；§5.2 的詳細範圍是 GPU 1.5×–10×（module 放 CPU 記憶體約 1.5–3×、放 GPU 記憶體約 5–10×）、CPU 20×–70×（AMD 20×、Intel 70×）。 [S3 摘要、§5.2、§6]
- [C26] 只降低 TTFT，後續每個 token 的生成時間不變：RTX 4090、Llama 7B、3K context，TTFT 從 900 ms 降到 90 ms，每 token 約 32 ms。 [S3 §5.4]
- [C07] 每個 token 的 KV cache 記憶體（16-bit）：Falcon 1B 0.18 MB、Llama 7B 0.50 MB、Llama 13B 0.78 MB、Llama 70B 2.5 MB；Llama 70B 快取一個 1K tokens 的 module 要 2.5 GB。 [S3 §5.5、Table 2]

## 使用時要小心
- 摘要/結論（8×、60×）與 §5.2（最高 10×、70×）數字不同；兩者並列時要說明脈絡。見 `lint/conflicts.md` L2。
- 論文自稱「沒有明顯準確度損失」，S2 與 S4 對此有不同看法，見 `lint/conflicts.md` L3。
- 實驗在 HuggingFace transformers 原型上、Llama2 / Falcon / MPT，不是生產環境。
