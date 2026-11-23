# 證據卡 10：領域總覽與五大里程碑

- **唯一來源頁**：`wiki/overview.md`（嚴禁混入其他來源）
- **核心敘事**：傳統 vLLM／SGLang 的 Prefix Caching 困於「同一模型、同一 GPU 記憶體、完全相同前綴」三重枷鎖；5 篇代表性論文依序打破五大邊界：
  1. **CacheBlend（EuroSys '25）**：打破「嚴格前綴」— RAG 多區塊非前綴融合（TTFT 降 2.2–3.3×、吞吐升 2.8–5×）`[CacheBlend, §4–7, p.5–12]`。
  2. **DroidSpeak（2024／NSDI '26）**：打破「單一權重」— 同底模微調跨模型共享（Prefill 降 1.7–2.6×、吞吐升 2–3×）`[DroidSpeak, §3–5, p.4–11]`。
  3. **LMCache（2025）**：打破「單張 GPU 記憶體」— 企業級分層卸載與 PD 分離（400 Gbps、最高升 15× 吞吐）`[LMCache, Abstract, §5–8, Table 5, p.1, 6–14]`。
  4. **RelayCaching（2026）**：打破「靜態預計算」— 多代理 Decode-to-Prefill 接力（重用 >80%、TTFT 快 4.71–9.2×）`[RelayCaching, §3–5, Table 1–2, Fig. 8, p.3–8]`。
  5. **Cross-Model KV Transfer（NVIDIA, 2026）**：打破「相同模型尺寸」— 同家族跨尺寸閉式線性映射（保留 73–98%、快 2.7–25×）`[Cross-Model KV, §2–4, Table 1, 3–5, p.2–9]`。
