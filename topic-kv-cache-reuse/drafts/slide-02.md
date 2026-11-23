# Slide 02：為什麼 Prefill 是推理系統的頭號瓶頸？

- **頁碼**：02 / 12
- **來源卡片**：`cards/card-06-metrics-and-prefill.md`, `cards/card-01-cacheblend.md`, `cards/card-03-lmcache.md`, `cards/card-10-overview.md`
- **Wiki 出處**：`wiki/entities/llm-serving-metrics.md`, `wiki/papers/cacheblend.md`, `wiki/papers/lmcache.md`, `wiki/entities/vllm-and-sglang.md`, `wiki/overview.md`

## 核心內容
- **Prefill vs. Decode 兩階段本質差異**：
  - **Prefill（預填充）**：一次處理完整輸入，屬**計算密集**且複雜度隨長度呈二次成長；4K tokens 在單張 A40 上即需 **3–6 秒**（Llama-34B／70B）`[CacheBlend, §2, p.3]`。
  - **Decode（解碼）**：逐 token 生成，屬**記憶體頻寬受限**且複雜度線性 `[DroidSpeak, §2.1, Fig. 3, p.2–3]`。
- **連鎖殺傷力 — Prefill 干擾（Prefill Interference）**：
  - 長 Prefill 不只直接拉高 **TTFT**，還會搶佔排程波及正在 Decode 的請求，拖累 **TBT／ITL** 與 **E2E**，大幅壓低滿足 SLO 的有效吞吐 **Goodput** `[DroidSpeak, §2.1, §2.3, Fig. 5, p.3–4]`。
- **傳統 Prefix Caching（vLLM／SGLang）的三重枷鎖**：
  - 只能在「**同一模型** ＋ **同一 GPU 記憶體** ＋ **嚴格相同前綴**」下生效，無法應付多區塊拼接、跨機卸載、多代理與多模型切換 `[CacheBlend, §3.2, p.3; LMCache, §1, p.1]`。
- **頁尾出處**：`wiki/entities/llm-serving-metrics.md`、`wiki/overview.md`｜`[CacheBlend, §2, p.3; DroidSpeak, §2.1–2.3, Fig. 3, 5, p.2–4]`
