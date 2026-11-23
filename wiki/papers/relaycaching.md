---
title: "RelayCaching：多代理系統中 Decode-to-Prefill KV Cache 重用與精準修正"
type: "paper"
sources:
  - "raw/04-relaycaching-2603.13289v1.md"
updated: "2026-11-23"
---

# RelayCaching: Accelerating LLM Collaboration via Decoding KV Cache Reuse

- **原始來源**：[04-relaycaching-2603.13289v1.md](../../raw/04-relaycaching-2603.13289v1.md)（`arXiv:2603.13289v1`，2026 年 2 月）
- **作者與單位**：Yingsheng Geng、Jiang Liu（BUPT）；Yuchong Gao（Tsinghua）；Weihong Wu（UESTC）；Guyue Liu（Peking University）
- **實作環境**：單張 NVIDIA H20（96 GB）、BF16、PyTorch 2.1.0、Transformers 4.50.2 `[RelayCaching, §5.1, Appendix B.4, p.6, 15]`

## 1. 核心痛點與動機
- **多代理級聯上下文冗餘（Cascading Context Redundancy）**：在多代理系統（MAS，如 Architect → Developer → Reviewer）中，上游代理動態生成的輸出（規格、推理鏈、程式碼）會嵌入下游代理帶有不同角色提示詞（prefix variation）的輸入中，導致傳統推理系統每輪皆須從頭重新 Prefill；在 $M$ 輪互動下，累積 Prefill 成本呈二次方成長 $O(M^2)$ `[RelayCaching, §1, Fig. 1, p.1–2]`。
- **既有快取典範失效**：
  - **Prefix Caching**（[vLLM 與 SGLang](../entities/vllm-and-sglang.md)）：要求嚴格前綴一致，遇角色切換即失效 `[RelayCaching, §1, §2.2, Fig. 1(a), p.1–3]`。
  - **Pre-computed Caching**（PromptCache、[CacheBlend](./cacheblend.md)、EPIC）：假設可離線預計算的靜態文件（如 RAG），無法處理執行期動態生成的代理輸出；且 CacheBlend 的 value-norm 檢測與固定比例重算在多代理動態情境表現受限 `[RelayCaching, §1, §2.2, §5.2, Fig. 1(b), p.1–3, 6–7]`。
  - **KVCOMM**：仰賴外部 anchor pool 檢索偏移量，隨代理數量與語境多樣性增加，重用率從 **88% 滑落至 70%**（GSM8K）`[RelayCaching, §2.3, §5.2, p.3, 7]`。

## 2. 三大實證觀察（詳見 [KV 偏差衡量指標](../concepts/kv-deviation-metrics.md)）
以 2WikiMQA 摘要問答管線（Mistral-7B-Instruct-v0.3 為主，並於 Appendix A 跨 Llama-3.1-8B、Qwen2.5-Coder-7B、DeepSeek-R1-Distill-Qwen-32B、Qwen3-30B-A3B、Qwen3-0.6B 共 6 模型驗證）發現 `[RelayCaching, §3, Appendix A, p.3–4, 11–13]`：
1. **宏觀高度對齊（Macro-Level Alignment）**：Decoding KV 與 Full-Prefill KV 的 Key Norm 達 **0.947**、Value Norm **0.926**、Key Cosine **0.935**，唯獨 **Value Cosine 為 0.800** 成為最敏感偏差指標；反觀獨立編碼（Independent KV）的 Value Norm 掉至 **0.588**，證實兩類重用偏差結構迥異 `[RelayCaching, §3.1, Fig. 2, p.3]`。
2. **層間 U 型相似度曲線（U-Shaped Layer Profile）**：淺層相似度極高、**中層**（負責推理與上下文整合）急劇下降、深層部分回升；Oracle 替換實驗證明僅修正中層即可回收絕大多數下游保真度 `[RelayCaching, §3.2, Fig. 3, Fig. 9, p.3–4, 12]`。
3. **Token 級稀疏性與跨層持續性**：僅少數位置（開頭邊界 token 與語意敏感 token）偏差大，且相鄰層 Spearman 排名相關性在進入中層後快速飆升並穩定於 **> 0.9** `[RelayCaching, §3.3, Fig. 4, Fig. 10, p.4, 13]`。

## 3. 核心機制設計（雙模組訓練無關修正）
- **上游解碼階段收集**：平行保存 **Pre-RoPE** 解碼 KV Cache（詳見 [RoPE 位置對齊](../concepts/rope-position-alignment.md)）、$L_{\text{start}}$ 層隱藏狀態 $h^{(L_{\text{start}})}$，以及累計注意力影響分數 $s_{\text{inf}}(j) = \sum_{t,\ell,h} \alpha_{t,\ell,h,j}$ `[RelayCaching, §4.2–4.3, Fig. 5, Eq. 6, p.5–6]`。
- **模組 1：Layer-Range Profiler（離線剖析，單一資料集如 2WikiMQA 即可跨任務泛化）**：
  - 找出關鍵中層區間 $[L_{\text{start}}, L_{\text{end}}]$ 與排名穩定偵測層 $L_{\text{det}}$（二階差分 $\alpha_\ell = \rho_\ell - 2\rho_{\ell-1} + \rho_{\ell-2}$ 由正轉負之下一層）`[RelayCaching, §4.2, Eq. 1–4, p.5]`。
  - 推論時：$[0, L_{\text{start}})$ 與 $(L_{\text{end}}, L_{\text{full}}]$ **直接跳過重用**；$[L_{\text{start}}, L_{\text{det}})$ 從 $h^{(L_{\text{start}})}$ 全算以執行偵測；$[L_{\text{det}}, L_{\text{end}}]$ 只對選中 token 執行稀疏修正（如 Llama-3.1-8B 剖析結果為 $L_{\text{start}}=1, L_{\text{det}}=3, L_{\text{end}}=18$）`[RelayCaching, §4.2, Table 5, p.5, 14]`。
- **模組 2：Dual-Criterion Token Selector（詳見 [Selective KV Recomputation](../concepts/selective-kv-recomputation.md)）**：
  - **偏差篩選 $I_{\text{dev}}$**：於 $L_{\text{det}}$ 挑出 Value Cosine 偏差 $d_{j,L_{\text{det}}} \ge 1.5 \cdot \mu_{\text{dev}}$ 的 token `[RelayCaching, §4.3.1, Eq. 5, p.6]`。
  - **影響力篩選 $I_{\text{inf-score}}$**：挑出累計注意力權重 $s_{\text{inf}}(j) \ge 1.45 \cdot \mu_{\text{inf}}$ 的關鍵語意 token `[RelayCaching, §4.3.2, Eq. 7, p.6]`。
  - **尾端修正 $I_{\text{inf-suffix}}$**：無條件納入重用段最末 **$K_{\text{suf}} = 10$** 個 token，彌補累計注意力偏向開頭的偏差並保護對後續新提示的局部注意力 `[RelayCaching, §4.3.2, Eq. 8–9, p.6, 14]`。

## 4. 關鍵實驗結果
- **準確率與重用率（Table 1 & Fig. 6，2–4 個代理）**：
  - GSM8K（Llama-3.1-8B）：Full Prefill `85.97 / 84.69 / 84.69`、RelayCaching **`84.84 / 85.50 / 85.17`**（反超或齊平 Full Prefill），重用率穩定 **> 80%**；反觀 CacheBlend 僅 `76.72 / 77.56 / 74.73`、EPIC 掉至 `58.73 / 66.46 / 58.42` `[RelayCaching, §5.2, Table 1, p.6–7]`。
  - MMLU（Llama-3.1-8B）：RelayCaching **`69.28 / 71.90 / 67.97`**（對齊 Full Prefill `71.24 / 73.20 / 66.67`）；HumanEval（Qwen2.5-Coder-7B）：RelayCaching **`82.61 / 85.09 / 87.58`** `[RelayCaching, Table 1, p.7]`。
- **TTFT 加速與次線性擴展（AIME24, Qwen3-0.6B）**：
  - 隨代理數從 Agent 2 增至 Agent 5，Full Prefill 從 85.2 ms 飆升至 493.9 ms（5.8×），RelayCaching 僅從 40.6 ms 增至 **104.8 ms**（2.6×），於 Agent 5 達成 **4.71×** 加速（索引選擇僅 0.5–0.8 ms）`[RelayCaching, §5.3, Table 2, p.7]`。
  - 累積長度拉至 **12,288 tokens** 時，Full Prefill 需 3.89 s、CacheBlend 需 1.08 s（固定比例線性成長），RelayCaching 僅需 **0.42 s**（次線性成長，較 Full 快 **9.2×**、較 CacheBlend 快 **2.5×**）`[RelayCaching, §5.3, Fig. 8, p.7–8]`。
- **消融實驗（GSM8K 2-Agent, Table 3）**：僅限層區間（46.88% 重用、85.90% Acc）→ 加 $I_{\text{dev}}$（90.37% 重用但 Acc 跌至 79.68%）→ 加 $I_{\text{inf-score}}$（85.84% 重用、81.65% Acc）→ 加上尾端 $I_{\text{inf-suffix}}$（**85.35% 重用、84.84% Acc**）`[RelayCaching, §5.4, Table 3, p.8]`。

> [!WARNING] ⚠️ 跨文獻張力／差異
> - **CacheBlend 在靜態 RAG vs. 動態 MAS 的表現落差**：[CacheBlend](./cacheblend.md) 在靜態多區塊 RAG 報告品質損失 ≤ 0.02 `[CacheBlend, §7.2, p.12]`；但 RelayCaching 將 CacheBlend（設定 20% value-norm 重算）直接用於動態多代理 Decode-to-Prefill 場景時，GSM8K 準確率由 85.97% 滑落至 74.73%–77.56%，且固定比例在 12K 長序列下呈線性成長（1.08 s vs RelayCaching 0.42 s）`[RelayCaching, §5.2–5.3, Table 1, Fig. 8, p.7]`。詳見 [跨文獻張力與差異彙整](../syntheses/conflicts-and-tensions.md)。

## 5. 限制與後續連結
- 目前僅支援**同質多代理系統（Homogeneous MAS）**，所有代理須共享完全相同的模型架構與權重；異質跨尺寸或跨家族代理留待未來研究 `[RelayCaching, Appendix C, p.18]`。
- 延伸閱讀：[KV 偏差衡量指標](../concepts/kv-deviation-metrics.md)、[跨論文方法全景對照](../syntheses/kv-reuse-landscape.md)。
