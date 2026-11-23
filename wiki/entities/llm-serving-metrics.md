---
title: "LLM 推理系統效能指標（TTFT、ITL/TBT、E2E、Goodput）"
type: "entity"
sources:
  - "raw/01-cacheblend-2405.16444v3.md"
updated: "2026-11-23"
---

# LLM 推理系統效能指標

在 KV Cache Reuse 相關研究中，系統效能評估聚焦於 Prefill 與 Decode 兩階段的延遲及整體吞吐量：

- **Prefill Phase（預填充階段）**：一次平行處理完整輸入提示並產生所有層的 KV Cache，計算複雜度隨輸入長度呈超線性／二次成長；4K tokens 在單張 A40 上即需 3–6 秒（Llama-34B／70B）`[CacheBlend, §1–2, p.2–3]`。
- **TTFT（Time to First Token）**：從請求送出到產生第 1 個輸出 token 的延遲，主要由排隊時間與 Prefill 延遲決定，是所有 KV Cache Reuse 技術最直接優化的核心指標（如 [CacheBlend](../papers/cacheblend.md) 降低 2.2–3.3× TTFT）`[CacheBlend, §1, §7.2, p.1, 12]`。
- **Throughput（吞吐量，QPS）**：在維持相同 TTFT／品質條件下系統每秒可服務的請求數；消除重複 Prefill 瓶頸可大幅拉升系統吞吐量（CacheBlend 提升 2.8–5×）`[CacheBlend, §2, §7.2, p.3, 12]`。

## 相關頁面
- [CacheBlend 論文筆記](../papers/cacheblend.md)
- [Compute-I/O Pipelining](../concepts/compute-io-pipelining.md)
- [KV Cache Reuse 領域總覽](../overview.md)
