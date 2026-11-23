---
title: "KV Cache Reuse 跨文獻張力、前提差異與爭議彙整"
type: "synthesis"
sources:
  - "raw/01-cacheblend-2405.16444v3.md"
  - "raw/02-droidspeak-2411.02820v3.md"
  - "raw/03-lmcache-2510.09665v2.md"
  - "raw/04-relaycaching-2603.13289v1.md"
  - "raw/05-cross-model-kv-transfer-2608.03893v1.md"
updated: "2026-11-23"
---

# 跨文獻張力、前提差異與爭議彙整

本頁遵循 [AGENTS.md](../../AGENTS.md) 的矛盾處理原則：**不強行選邊站，並陳各方數據、實驗條件與適用前提**，集中對照 5 篇論文之間的四大核心張力與實驗邊界。

## 張力 1：靜態 RAG 選擇性重算（CacheBlend）套用至動態多代理（RelayCaching）的表現落差
- **涉及頁面**：[CacheBlend](../papers/cacheblend.md)、[RelayCaching](../papers/relaycaching.md)、[KV 偏差衡量指標](../concepts/kv-deviation-metrics.md)
- **雙方證據並陳**：
  - **[CacheBlend](../papers/cacheblend.md)**（靜態多區塊 RAG）：以 5%–18%（預設 15%）HKVD 選擇性重算，在 2WikiMQA、Musique、SAMSum、MultiNews 上品質損失 ≤ **0.02**（Yi-34B ≤ 0.002），同時 TTFT 降 **2.2–3.3×** `[CacheBlend, §7.2–7.3, Fig. 12, 16, p.12]`。
  - **[RelayCaching](../papers/relaycaching.md)**（動態多代理 Decode-to-Prefill）：將 CacheBlend（20% value-norm）用於 GSM8K 與 MMLU 多代理鏈時，GSM8K 準確率從 84.69–85.97% 掉至 **74.73–77.56%**（MMLU 3-agent 掉至 64.71%）；且 12K tokens 時呈線性膨脹（1.08 s vs RelayCaching 0.42 s）`[RelayCaching, §5.2–5.3, Table 1, Fig. 8, Appendix B.3, p.7, 14]`。
- **差異根因**：Independent KV 的 Value Norm 偏移劇烈（0.588），但 Decoding KV 的 Value Norm 高達 0.926、真正偏移的是 **Value Cosine（0.800）**；且固定比例重算不如均值相對門檻＋注意力影響力＋尾端 10 token 具備次線性擴展性 `[RelayCaching, §3.1, §5.3–5.4, Fig. 2, Table 3, p.3, 7–8]`。

## 張力 2：跨模型 KV 共享的路線之爭——同架構局部重算（DroidSpeak）vs. 跨尺寸閉式線性映射（NVIDIA）
- **涉及頁面**：[DroidSpeak](../papers/droidspeak.md)、[Cross-Model KV Transfer](../papers/cross-model-kv-transfer.md)
- **雙方證據並陳**：
  - **[DroidSpeak](../papers/droidspeak.md)**：鎖定「同底模、同架構微調變體」，透過重算單一連續關鍵層區間＋傳輸 E-cache 實現 1.7–2.6× Prefill 加速與幾乎無損 F1，但無法跨模型尺寸使用 `[DroidSpeak, §3.1, §4.2, §5.2, p.4, 7, 10]`。
  - **[Cross-Model KV Transfer](../papers/cross-model-kv-transfer.md)**：在「同家族、不同尺寸（matched-KV）」間以閉式逐頭 Ridge 映射完全跳過接收端 Prefill，在 4 組 Tier 1 配對保留 **73–98%** 準確率與 **2.7–25×** 加速；但在 Ministral 3→14B／8B→14B 兩組 Tier 2 配對上線性映射驟降至 **41.6–44.2%**（floor-normalized 11–15%），必須改採需梯度訓練的 MLP 才救回 92–96% `[Cross-Model KV, §4.2, §4.4, Table 1, Table 3, Table 6, p.6–7, 13]`。
- **差異根因與適用邊界**：DroidSpeak 的優勢是零線性假設、支援同架構下任意微調差異與動態 SLO 調整；Cross-Model KV Transfer 則突破尺寸限制並帶來更高長上下文加速（最高 25×），但受限於 matched-KV 條件、每方向需儲存 4–12 GB Mapper、且遇到非線性跨尺寸配對時閉式解會失效。

## 張力 3：KV 品質該看重建誤差（$R^2$ / 範數差）還是注意力子空間保真度？
- **涉及頁面**：[Cross-Model KV Transfer](../papers/cross-model-kv-transfer.md)、[RelayCaching](../papers/relaycaching.md)、[KV 偏差衡量指標](../concepts/kv-deviation-metrics.md)
- **雙方證據並陳**：
  - 單配對內挑選源層或靜態區塊篩選時，$R^2$ 與數值偏差十分有效 `[CacheBlend, §4.3, p.6; Cross-Model KV, §3.2, §4.5, p.5, 8]`。
  - 跨模型配對評估時，[Cross-Model KV Transfer](../papers/cross-model-kv-transfer.md) 證明校準集 $R_K^2$ 與下游 HellaSwag 保留率毫無正相關（**$r = -0.20$**）；真正決定表現的是誤差是否落在目標 Query 敏感子空間（**Attention-Output Cosine $r = +0.57$** 與 **K-concentration**）`[Cross-Model KV, §4.5, Table 4, p.7–8]`。
- **差異根因**：$R^2$ 對 KV 所有維度等權計分，但 Transformer 注意力只讀取與目標 Query 高度對齊的子空間，且僅有高注意力權重的 token／方向會主導下游輸出。

## 張力 4：系統層遠端卸載的頻寬交叉點與 Context Truncation 陷阱
- **涉及頁面**：[LMCache](../papers/lmcache.md)
- **雙方證據並陳**：
  - **遠端載入快慢交叉點**：Company C 使用高速物件儲存（如 S3 Express ~1 GB/s）可比完整 Prefill 降 **22–32% TTFT** `[LMCache, §9, p.15]`；但 B200 敏感度分析指出在 **32 Gbps** 頻寬下，唯有超過 **256K tokens** 載入才快於重算，須達 **64–128 Gbps** 才全序列勝出 `[LMCache, §8.7, Fig. 15, p.14–15]`。
  - **截斷反噬快取**：滑動視窗截斷輸入開頭雖可節省記憶體，卻使 Company F 前綴命中率從 **~85% 腰斬至 ~45%** `[LMCache, §9, p.15]`。
- **工程啟示**：系統層必須採「自適應載入決策」與「append-only 上下文管理」，否則卸載或截斷皆可能造成負優化。

## 相關頁面
- [跨論文方法全景對照](./kv-reuse-landscape.md)
- [KV Cache Reuse 領域總覽](../overview.md)
