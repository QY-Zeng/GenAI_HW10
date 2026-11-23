---
title: "KV Cache Reuse 領域全景總覽"
type: "overview"
sources:
  - "raw/01-cacheblend-2405.16444v3.md"
  - "raw/02-droidspeak-2411.02820v3.md"
  - "raw/03-lmcache-2510.09665v2.md"
  - "raw/04-relaycaching-2603.13289v1.md"
  - "raw/05-cross-model-kv-transfer-2608.03893v1.md"
updated: "2026-11-23"
---

# KV Cache Reuse（KV 快取重用）領域全景總覽

在長上下文 RAG、多輪對話、多代理協作（MAS）與多模型路由／級聯部署中，**Prefill 階段的重複計算**（複雜度隨上下文二次成長）與 [Prefill 干擾](./entities/llm-serving-metrics.md) 已成為推論延遲（TTFT／ITL）、算力與能源成本的頭號瓶頸 `[CacheBlend, §2, p.3; DroidSpeak, §2.3, p.4; LMCache, §2.2, p.3; RelayCaching, §1, p.1; Cross-Model KV, §1, p.1]`。

傳統 [vLLM 與 SGLang](./entities/vllm-and-sglang.md) 的 **Prefix Caching** 只能在「同一模型、同一 GPU 記憶體、且前綴完全一致」的狹窄條件下運作。本知識庫收錄的 5 篇核心論文，分別沿著**「非前綴融合 → 同底模跨模型 → 企業級系統卸載 → 動態多代理接力 → 跨尺寸閉式轉移」**五條關鍵里程碑，系統性打破了這些邊界：

## 五大里程碑脈絡
1. **打破「嚴格前綴」限制 — [CacheBlend](./papers/cacheblend.md)（EuroSys '25）**：針對 RAG 多區塊非前綴輸入，結合 Token 級[選擇性 KV 重算](./concepts/selective-kv-recomputation.md)（HKVD 5–18%）、單次 [RoPE 位置對齊](./concepts/rope-position-alignment.md) 與 [Compute-I/O 管線化](./concepts/compute-io-pipelining.md)，降 **2.2–3.3× TTFT**、升 **2.8–5× 吞吐** `[CacheBlend, §4–7, p.5–12]`。
2. **打破「單一權重」限制 — [DroidSpeak](./papers/droidspeak.md)（2024／NSDI '26）**：面向同底模微調變體共享上下文，發現平均僅 11% 為關鍵層，並為規避 [E-Cache 切換開銷](./concepts/e-cache-transition-overhead.md) 設計單一切換點連續層重算與帕累托動態調度，降 **1.7–2.6×** Prefill 延遲、升 **2–3×** 吞吐 `[DroidSpeak, §3–5, p.4–11]`。
3. **打破「單張 GPU 記憶體」限制 — [LMCache](./papers/lmcache.md)（2025）**：建構企業級分散式 [LMCache 系統架構](./entities/lmcache-system.md)，以 256-token Chunk 批次搬運（**400 Gbps** vs 原生 88 Gbps）、雙層管線化、Zero-Copy 與標準化 KV Connector / Controller API 統一支撐跨查詢卸載與 PD 分離，最高提升 **15× 吞吐量** `[LMCache, Abstract, §5–8, Table 5, p.1, 6–14]`。
4. **打破「靜態預計算」限制 — [RelayCaching](./papers/relaycaching.md)（2026）**：解決多代理系統動態輸出的 $O(M^2)$ 級聯冗餘，揭示 Value Cosine 為主導偏差（[KV 偏差衡量指標](./concepts/kv-deviation-metrics.md)）與 U 型中層結構，以層×Token 雙維稀疏修正達成 **>80%** 重用率、**4.71×**（5 代理）至 **9.2×**（12K 長文）TTFT 加速 `[RelayCaching, §3–5, Table 1–2, Fig. 8, p.3–8]`。
5. **打破「相同模型尺寸」限制 — [Cross-Model KV Cache Transfer](./papers/cross-model-kv-transfer.md)（NVIDIA, 2026）**：證明同家族跨尺寸（matched-KV）模型間具顯著線性結構，以無梯度閉式逐頭 Ridge 回歸＋top-$k$ 源層選擇＋無位置 RoPE 解耦，在 4 組 Tier 1 配對保留 **73–98%** 準確率、跑出 **2.7–25×** 加速，並揭示誤差落點（Attention-Output Cosine $r=+0.57$ vs $R^2$ $r=-0.20$）才是品質關鍵 `[Cross-Model KV, §2–4, Table 1, 3–5, p.2–9]`。

## 延伸導覽
- [跨論文方法全景對照](./syntheses/kv-reuse-landscape.md)
- [跨文獻張力與差異彙整](./syntheses/conflicts-and-tensions.md)
- [Wiki 目錄索引](./index.md)
