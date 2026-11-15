---
name: s1-pagedattention-vllm
description: PagedAttention / vLLM 論文（SOSP 2023）：把 OS 的分頁概念用在 KV cache 記憶體管理，減少浪費、提高 batch size 與吞吐
sources: [S1]
---

# S1 — Efficient Memory Management for LLM Serving with PagedAttention

- 書目：Kwon et al., SOSP 2023；arXiv 2309.06180（v1，2023-09-12）
- 取得方式：WebSearch 回傳的論文原文片段（arXiv PDF、ar5iv）與 WebFetch 對 PDF 的擷取（2026-11-15）
- 驗證狀態：**一手，但不是全文逐頁讀過。** 原文片段確認的 claim 標為 `snippet`；只出現在 WebFetch 擷取摘要（由工具的小模型整理）的標為 `extract-only`，**未獨立驗證，不得用於簡報數字**。

## 重點（claim）
- [C06] 以 13B 模型跑在 40GB A100：約 65% 記憶體是不變的模型權重；activation 只佔一小部分，所以 KV cache 的管理方式決定最大 batch size。 [S1 Fig.1 與其說明；snippet]
- [C08] PagedAttention 把每個請求的 KV cache 切成固定大小的 block，block 不必存放在連續空間；類比：block = page、token = byte、request = process。 [S1 §1；snippet]
- [C09] vLLM 達成「接近零浪費」的 KV cache 記憶體，吞吐比 FasterTransformer、Orca 等最新系統高 2–4×（同等延遲），且不影響準確度。 [S1 摘要與 §1；snippet]
- [C40] 可在 block 粒度做記憶體共享，跨同一請求的不同序列、甚至跨請求。 [S1 §1；snippet]
- [C38] （extract-only）既有系統中，只有約 20.4%–38.2% 的 KV cache 記憶體實際存放 token states。 [擷取摘要，未於原文片段中看到]
- [C42] （extract-only）parallel sampling 以 reference count 與 block 級 copy-on-write 共享 prompt 的 KV；預設 block 大小 16 tokens。 [擷取摘要，未於原文片段中看到]

## 使用時要小心
- 2–4× 是「與同等延遲下的 FasterTransformer、Orca 比」，不是和今天的 vLLM 或其他引擎比。
- C38、C42 的數字我個人印象與這篇論文相符，但依 schema 規則 2 沒有一手全文佐證，所以不採用。若要採用，需補讀全文。
