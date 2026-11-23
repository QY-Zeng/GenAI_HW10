---
title: "KV Cache Reuse 跨文獻張力、前提差異與爭議彙整"
type: "synthesis"
sources:
  - "raw/01-cacheblend-2405.16444v3.md"
  - "raw/03-lmcache-2510.09665v2.md"
  - "raw/04-relaycaching-2603.13289v1.md"
updated: "2026-11-23"
---

# 跨文獻張力、前提差異與爭議彙整

本頁遵循 [AGENTS.md](../../AGENTS.md) 的矛盾處理原則：**不強行選邊站，並陳各方數據、實驗條件與適用前提**，協助讀者與下游簡報準確掌握每項結論的成立邊界。

## 張力 1：CacheBlend 的 HKVD 選擇性重算——在靜態 RAG 近乎無損，但在動態 MAS 明顯掉點
- **涉及頁面**：[CacheBlend](../papers/cacheblend.md)、[RelayCaching](../papers/relaycaching.md)、[KV 偏差衡量指標](../concepts/kv-deviation-metrics.md)
- **雙方證據並陳**：
  - **[CacheBlend](../papers/cacheblend.md)**（靜態多區塊 RAG）：以 5%–18%（預設 15%）HKVD 選擇性重算，在 2WikiMQA、Musique、SAMSum、MultiNews 上 F1／Rouge-L 損失 ≤ **0.02**（Yi-34B 甚至 ≤ 0.002），同時 TTFT 降低 **2.2–3.3×** `[CacheBlend, §7.2–7.3, Fig. 12, 16, p.12]`。
  - **[RelayCaching](../papers/relaycaching.md)**（動態多代理 Decode-to-Prefill）：將 CacheBlend（取 20% value-norm 偏差）應用於 GSM8K 與 MMLU 多代理鏈時，GSM8K 準確率從 Full Prefill 的 84.69–85.97% 下滑至 **74.73–77.56%**（MMLU 3-agent 由 73.20% 降至 64.71%）；且在 12K tokens 長序列下因固定比例重算呈線性成長（1.08 s vs RelayCaching 0.42 s）`[RelayCaching, §5.2–5.3, Table 1, Fig. 8, Appendix B.3, p.7, 14]`。
- **差異根因**：
  1. **獨立預計算 vs. 解碼接力的偏差幾何不同**：Independent KV 的 Value Norm 大幅偏移（0.588），但 Decoding KV 的 Value Norm 高達 0.926、真正偏移的是 **Value Cosine 方向（0.800）** `[RelayCaching, §3.1, Fig. 2, p.3]`。
  2. **缺少下游影響力與尾端邊界考量**：RelayCaching 消融證實單靠偏差值仍會漏掉語意樞紐與段末邊界 token `[RelayCaching, §5.4, Table 3, p.8]`。
  3. **固定比例 vs. 均值相對門檻**：固定比例隨序列線性成長，而偏差 token 數本身具次線性稀疏性 `[RelayCaching, §5.3, p.7–8]`。

## 張力 2：遠端儲存載入 KV 究竟比重新 Prefill 快還是慢？
- **涉及頁面**：[LMCache](../papers/lmcache.md)
- **雙方證據並陳**：
  - **正向生產證據**：[LMCache](../papers/lmcache.md) §9 指出，受惠於 S3 Express 等高速物件儲存（~1 GB/s），Company C 從遠端載入 KV 反而比重新 Prefill 降低 **22–32% TTFT** `[LMCache, §9, p.15]`。
  - **負向頻寬交叉點**：同文 §8.7 在 B200 上測得 **32 Gbps** 頻寬下，須超過 **256K tokens** 載入才快於重新 Prefill；須達 **64–128 Gbps** 才全序列長度勝出 `[LMCache, §8.7, Fig. 15, p.14–15]`。
- **差異根因**：取決於 GPU 算力、儲存／網路頻寬與上下文長度的交叉點，必須採用自適應載入策略。

## 張力 3：長上下文截斷（Context Truncation）與 Prefix Caching 的內在衝突
- **涉及頁面**：[LMCache](../papers/lmcache.md)
- **差異現象**：實務上常用滑動視窗保留最新 token 來節省記憶體，但 LMCache 在 Company F 實測此舉會讓前綴快取命中率從 **~85% 暴跌至 ~45%**，顯示動態改動前綴會直接瓦解前綴雜湊重用 `[LMCache, §9, p.15]`。

## 相關頁面
- [跨論文方法全景對照](./kv-reuse-landscape.md)
- [KV Cache Reuse 領域總覽](../overview.md)
