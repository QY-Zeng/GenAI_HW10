---
title: "LLM 推理系統效能指標（TTFT、ITL/TBT、E2E、Goodput）"
type: "entity"
sources:
  - "raw/01-cacheblend-2405.16444v3.md"
  - "raw/02-droidspeak-2411.02820v3.md"
updated: "2026-11-23"
---

# LLM 推理系統效能指標

在 KV Cache Reuse 相關研究中，系統效能評估圍繞 Prefill（計算密集、複雜度隨輸入長度呈二次成長）與 Decode（記憶體頻寬受限、複雜度呈線性成長）兩階段展開 `[CacheBlend, §2, p.3; DroidSpeak, §2.1, Fig. 3, p.2–3]`：

- **TTFT（Time to First Token）**：從查詢送出到產生第 1 個輸出 token 的總時間，包含排隊延遲與 Prefill 時間，是 KV Cache Reuse 最直接優化的指標（如 [CacheBlend](../papers/cacheblend.md) 降 2.2–3.3×、[DroidSpeak](../papers/droidspeak.md) 降 1.7–2.6×）`[CacheBlend, §7.2, p.12; DroidSpeak, §2.1, §5.2, p.3, 10]`。
- **TBT / ITL（Time Between Tokens / Inter-Token Latency）**：相鄰兩個輸出 token 之間的平均生成間隔 `[DroidSpeak, §2.1, p.3]`。
- **E2E Latency（End-to-End 延遲）**：從查詢送出到最後一個 token 生成完畢的總耗時 `[DroidSpeak, §2.1, p.3]`。
- **Goodput（有效吞吐量）**：在**滿足 SLO（Service-Level Objectives）延遲門檻**的前提下系統可承受的最大查詢率（QPS）`[DroidSpeak, §2.1, §5.3, p.3, 10]`。
- **Prefill Interference（預填充干擾）**：長上下文 Prefill 會長時間佔用 GPU 排程，不僅使 TTFT 隨輸入超線性上升，還會波及正在 Decode 的請求、推高 TBT 與 E2E 延遲；因此透過 KV Reuse 縮短 Prefill，會產生連帶降低 TBT／E2E 並提升 2–3× Goodput 的二階效益 `[DroidSpeak, §2.3, §5.3, Fig. 5, Fig. 15, p.3–4, 10–11]`。

## 相關頁面
- [CacheBlend 論文筆記](../papers/cacheblend.md)
- [DroidSpeak 論文筆記](../papers/droidspeak.md)
- [Compute-I/O Pipelining](../concepts/compute-io-pipelining.md)
- [KV Cache Reuse 領域總覽](../overview.md)
