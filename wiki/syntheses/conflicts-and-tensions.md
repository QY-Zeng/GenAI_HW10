---
title: "KV Cache Reuse 跨文獻張力、前提差異與爭議彙整"
type: "synthesis"
sources:
  - "raw/03-lmcache-2510.09665v2.md"
updated: "2026-11-23"
---

# 跨文獻張力、前提差異與爭議彙整

本頁遵循 [AGENTS.md](../../AGENTS.md) 的矛盾處理原則：**不強行選邊站，並陳各方數據、實驗條件與適用前提**，協助讀者與下游簡報準確掌握每項結論的成立邊界。

## 張力 1：遠端儲存載入 KV 究竟比重新 Prefill 快還是慢？
- **來源頁面**：[LMCache 論文筆記](../papers/lmcache.md)
- **表面張力**：
  - **正向生產證據**：[LMCache](../papers/lmcache.md) §9 指出，受惠於 S3 Express 等高速遠端物件儲存（吞吐從 ~100 MB/s 提升至 ~1 GB/s），企業客戶 Company C 直接從遠端物件儲存載入 KV，比完整 Prefill 降低 **22–32% TTFT** `[LMCache, §9, p.15]`。
  - **負向條件限制**：同文 §8.4 與 §8.7 在 B200 上測試發現，當網路頻寬偏低（**32 Gbps**）且輸入短於 **256K tokens**（或模型較小）時，遠端載入延遲會反超重新 Prefill；唯有在 **64–128 Gbps** 下才在全序列長度勝出 `[LMCache, §8.4, §8.7, Fig. 15, p.12–15]`。
- **差異根因與工程啟示**：取決於「GPU 算力速度 vs. 網路／儲存頻寬 vs. 序列長度（Prefill 二次成長 vs. I/O 線性成長）」的交叉點；實務上必須採用**自適應載入決策（adaptive load-vs-prefill）**而非一律載入。

## 張力 2：長上下文截斷（Context Truncation）與 Prefix Caching 的內在衝突
- **來源頁面**：[LMCache 論文筆記](../papers/lmcache.md)
- **差異現象**：工業界常以滑動視窗截斷早期 token 以控制 GPU 記憶體與 context window，但 LMCache 在 Company F 真實流量上測得此舉會使前綴快取命中率從 **~85% 暴跌至 ~45%**，因為移除開頭 token 直接破壞了前綴哈希匹配 `[LMCache, §9, p.15]`。
- **工程啟示**：在長對話與代理系統中應避免動態改動或截斷前綴（append-only 原則），否則會抵銷系統層 KV 快取的大半效益。

*(後續將隨 RelayCaching 與 Cross-Model KV Transfer 的 Ingest 持續增補跨論文張力。)*

## 相關頁面
- [LMCache 論文筆記](../papers/lmcache.md)
- [跨論文方法全景對照](./kv-reuse-landscape.md)
- [KV Cache Reuse 領域總覽](../overview.md)
