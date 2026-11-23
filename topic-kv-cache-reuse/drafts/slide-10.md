# Slide 10：貫穿五篇的兩條隱藏主線：RoPE 對齊與誤差落點

- **頁碼**：10 / 12
- **來源卡片**：`cards/card-09-rope.md`, `cards/card-08-tensions.md`, `cards/card-05-cross-model-kv.md`
- **Wiki 出處**：`wiki/concepts/rope-position-alignment.md`, `wiki/syntheses/conflicts-and-tensions.md`, `wiki/papers/cross-model-kv-transfer.md`

## 核心內容
- **隱藏主線 A｜RoPE 旋轉位置編碼對齊三部曲**：
  1. **CacheBlend**：預存 K 向量乘上一次相對旋轉矩陣，近零開銷恢復位置 `[CacheBlend, Footnote 3, p.6; Appendix A, p.16]`。
  2. **RelayCaching**：上游直接存 **Pre-RoPE KV**，下游接力時再重施目標位置 RoPE `[RelayCaching, §4.2, Fig. 5, p.5]`。
  3. **Cross-Model KV**：$\hat{\mathbf{K}}_t = (\mathbf{K}_s \mathbf{R}_{\Theta_s}^{-1}(t)\mathbf{W}_K + \mathbf{b}_K)\mathbf{R}_{\Theta_t}(t)$ 徹底解耦位置與語意；若漏推論重施，MMLU 崩至 **25.79%**、GSM8K 崩至 **4.17%** `[Cross-Model KV, §3.3, §4.3, Table 2, p.5–7]`。
- **隱藏主線 B｜偏差指標進化：誤差「落點」遠比誤差「大小」重要**：
  - 跨 12 組 matched-KV 配對評估，校準集重建指標 $R_K^2$ 與 HellaSwag 保留率毫無正相關（Pearson **$r = -0.20$**），而 **Attention-Output Cosine** 達 **$r = +0.57$** `[Cross-Model KV, §4.5, p.7–8]`。
  - MLP 之所以救回 +37 pp，是因它大幅降低 **K-concentration（$\Delta \approx -2.5$）**，把殘差推離目標 Query 敏感子空間 `[Cross-Model KV, §4.5, Table 4, p.8]`。
- **頁尾出處**：`wiki/concepts/rope-position-alignment.md`、`wiki/syntheses/conflicts-and-tensions.md`｜`[CacheBlend, App. A; RelayCaching, §4.2; Cross-Model KV, §3.3, §4.3, §4.5, Table 2, 4]`
