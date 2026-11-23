---
title: "CacheBlend：面向 RAG 的快取知識融合與選擇性 KV 重算"
type: "paper"
sources:
  - "raw/01-cacheblend-2405.16444v3.md"
updated: "2026-11-23"
---

# CacheBlend: Fast Large Language Model Serving for RAG with Cached Knowledge Fusion

- **原始來源**：[01-cacheblend-2405.16444v3.md](../../raw/01-cacheblend-2405.16444v3.md)（`arXiv:2405.16444v3`，EuroSys '25）
- **作者與單位**：Jiayi Yao、Hanchen Li、Yuhan Liu、Siddhant Ray、Yihua Cheng、Qizheng Zhang、Kuntai Du、Shan Lu、Junchen Jiang（University of Chicago、CUHK Shenzhen、Stanford、Microsoft Research）
- **開源實作**：整合於 [LMCache](https://github.com/LMCache/LMCache)（於 [vLLM](../entities/vllm-and-sglang.md) 上實作約 3K 行 Python，`[CacheBlend, §6, p.9]`）

## 1. 核心痛點與動機
- **RAG 多區塊輸入瓶頸**：在長上下文 RAG 場景中（例如 4,000 tokens），Llama-34B 或 Llama-70B 在單張 A40 GPU 上執行完整 Prefill 需時 3–6 秒，成為 [TTFT](../entities/llm-serving-metrics.md) 與系統吞吐量的主要瓶頸 `[CacheBlend, §2, p.3]`。
- **Prefix Caching 的不足**：[vLLM 與 SGLang](../entities/vllm-and-sglang.md) 等既有系統只重用位於輸入最前端（prefix）的文字區塊；當 RAG 同時檢索多個文字區塊（chunks）並串接時，僅第 1 個 chunk 能命中前綴快取，其餘非前綴 chunks 全數被迫重新 Prefill `[CacheBlend, §3.2, Fig. 1(b), p.2–4]`。
- **Full KV Reuse（如 PromptCache）的品質崩潰**：直接拼接獨立預計算的各 chunk KV Cache，即使透過 buffer 修正位置編碼，仍完全忽略不同 chunk 之間的 **cross-attention**（例如將「Messi 進 13 球」與「Ronaldo 進 8 球」分開預算後直接拼接，導致模型胡言亂語），使 forward attention matrix 產生巨大偏差 `[CacheBlend, §3.3, Fig. 3–4, p.4–5]`。

## 2. 核心機制設計
CacheBlend 結合兩大核心技術以同時取得「接近 Full KV Reuse 的速度」與「媲美 Full KV Recompute 的品質」：
1. **Token 層級選擇性重算（[Selective KV Recomputation](../concepts/selective-kv-recomputation.md)）**：
   - 定義每個 token 的 **KV deviation** $\Delta_{\text{kv}}(KV_i, KV_i^{\text{full}})[j] = |KV_i[j] - KV_i^{\text{full}}[j]|$ 與層級 **attention deviation** $\Delta_{\text{attn}}(A_i, A_i^{\text{full}}) = \|A_i - A_i^{\text{full}}\|_2$ `[CacheBlend, §4.1, Table 1, p.5]`。
   - 受限於 attention sparsity，每層僅約 **10–15%** 的 **HKVD（High-KV-Deviation）tokens** 貢獻絕大多數偏差；且相鄰層的 HKVD token 排名具高度 Spearman 相關性 `[CacheBlend, §4.3, Fig. 6–8, p.6–7]`。
   - 採用 **Gradual Filtering（漸進式過濾）**：第 1 層重算全部 token 以找出 $r_1\%$ 高偏差 token，第 2 層僅重算這些 token 並再篩出 $r_2\%$，逐層收斂，避免為了找 HKVD 而先做完整 Prefill `[CacheBlend, §4.3, Fig. 9, p.7]`。
2. **位置編碼修正（[RoPE 位置對齊](../concepts/rope-position-alignment.md)）**：
   - 針對非前綴 chunk 的預計算 K 向量，利用 RoPE 僅依賴相對距離的特性，以旋轉矩陣 $R_{\Theta, m}^d$ 一次性校正位置，額外開銷可忽略 `[CacheBlend, Footnote 3, p.6; Appendix A, p.16]`。
3. **計算與載入管線化（[Compute-I/O Pipelining](../concepts/compute-io-pipelining.md)）**：
   - 系統分為 **Loading Controller**、**KV Cache Store**（512-token chunk 雜湊索引，百萬 chunks 僅佔 16 MB CPU RAM）與 **Fusor** 三模組 `[CacheBlend, §5.1, §6, Fig. 11, p.8–9]`。
   - 以雙執行緒將「第 $i$ 層部分重算（`prefill_layer`）」與「第 $i+1$ 層從 SSD／RAM 載入 KV Cache（`fetch_kv`）」重疊執行；Loading Controller 依 $T_{\text{recompute}}$ 與 $T_{\text{load}}$ 挑選最佳重算比例（保底 $r^* = 15\%$）或最低成本儲存裝置 `[CacheBlend, §5.1, Fig. 10, p.8]`。

## 3. 關鍵實驗結果
- **實驗環境**：Runpod（2× NVIDIA A40、128 GB RAM、1 TB NVMe SSD 實測 4.8 GB/s）；模型為 Mistral-7B、Yi-34B（8-bit）、Llama-70B（8-bit）；資料集涵蓋 2WikiMQA、Musique、SAMSum、MultiNews 及 6,000 筆合成 RAG 查詢 `[CacheBlend, §7.1, p.10–11]`。
- **延遲與吞吐量**：相較 Full KV Recompute 與 Prefix Caching，CacheBlend 降低 **2.2–3.3× TTFT**，並於相同 TTFT 下提升 **2.8–5× 吞吐量**（相較 Prefix Caching 最高達 **3.3×**）`[CacheBlend, §7, §7.2, Fig. 12, Fig. 14, p.10–12]`。
- **生成品質**：F1 與 Rouge-L 降幅控制在 **≤ 0.01–0.03**（Fig. 12 內 ≤ 0.02）；相較 Full KV Reuse，QA 任務 F1 提升 **0.1–0.2**、摘要任務 Rouge-L 提升 **0.03–0.25**（整體 0.15–0.35）`[CacheBlend, §1, §7, §7.2, p.2, 10, 12]`。
- **敏感度分析**：在 Yi-34B 上僅需 **5%–18%** 重算比例即可將品質損失壓在 **≤ 0.002**，對應 **4.1–6.6×** TTFT 縮減；且隨 batch size 增大，Prefill 占比提高使加速效益更顯著 `[CacheBlend, §7.3, Fig. 15–16, p.12]`。
- **與其他 RAG 模式對比**：相較 LangChain MapReduce 降低 **2–5× TTFT** 且 F1 更高；相較 MapRerank 品質大幅領先 `[CacheBlend, §7.2, Fig. 13, p.10, 12]`。

## 4. 限制與後續連結
- 僅適用於 Transformer 架構，尚未驗證於 Mamba、Griffin 等狀態空間或混合架構 `[CacheBlend, §9, p.13]`。
- 尚未測試多節點跨機 KV 共享與 DistServe 等新式分離架構，亦聚焦於靜態離線預計算的文字區塊 `[CacheBlend, §9, p.13]`。
- 延伸閱讀：[KV Cache Reuse 領域總覽](../overview.md)、[跨論文方法全景對照](../syntheses/kv-reuse-landscape.md)。
