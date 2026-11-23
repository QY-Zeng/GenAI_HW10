# 證據卡 06：LLM 推理效能指標與 Prefill 瓶頸

- **唯一來源頁**：`wiki/entities/llm-serving-metrics.md`（嚴禁混入其他來源）
- **Prefill vs. Decode 特性**：Prefill 一次處理完整上下文、計算密集且複雜度隨長度二次成長（4K tokens 在單張 A40 需 3–6 秒）；Decode 逐 token 生成、屬記憶體頻寬受限且複雜度線性 `[CacheBlend, §2, p.3; DroidSpeak, §2.1, Fig. 3, p.2–3]`。
- **四大核心指標**：
  - **TTFT（Time to First Token）**：查詢送出到第 1 個 token 產出時間（排隊＋Prefill），是 KV Reuse 最直接優化指標 `[CacheBlend, §7.2, p.12; DroidSpeak, §2.1, p.3]`。
  - **TBT / ITL**：相鄰輸出 token 間的平均生成間隔 `[DroidSpeak, §2.1, p.3]`。
  - **E2E Latency**：送出至最後一個 token 完成的總延遲 `[DroidSpeak, §2.1, p.3]`。
  - **Goodput**：滿足延遲 SLO 前提下系統可承載的有效吞吐量（QPS）`[DroidSpeak, §2.1, §5.3, p.3, 10]`。
- **Prefill 干擾（Prefill Interference）**：長 Prefill 阻塞排程，不只推高 TTFT，還會波及正在 Decode 的請求、惡化 TBT 與 E2E；縮短 Prefill 能帶來提升 2–3× Goodput 的二階連鎖效益 `[DroidSpeak, §2.3, §5.3, Fig. 5, 15, p.3–4, 10–11]`。
