# 證據卡 09：RoPE 旋轉位置編碼對齊三部曲

- **唯一來源頁**：`wiki/concepts/rope-position-alignment.md`（嚴禁混入其他來源）
- **為何關鍵**：RoPE 將絕對位置 $m$ 以正交矩陣 $\mathbf{R}_{\Theta, m}^d$ 編碼進 Q 與 K（V 不含位置）；KV 移位或跨模型時若未對齊將破壞相對距離注意力。
- **三階段解法演進**：
  1. **CacheBlend（單次相對旋轉校正）**：利用 Proposition A.1 相對距離不變性，對預存 K 乘上一次相對旋轉矩陣，開銷可忽略 `[CacheBlend, Footnote 3, p.6; Appendix A, p.16]`。
  2. **RelayCaching（Pre-RoPE 儲存＋接力重施）**：上游直接存未旋轉的 Pre-RoPE KV，下游接力 Prefill 時再依新位置重施 RoPE `[RelayCaching, §4.2, Fig. 5, p.5]`。
  3. **Cross-Model KV Transfer（內容空間完全解耦）**：$\hat{\mathbf{K}}_t = (\mathbf{K}_s \mathbf{R}_{\Theta_s}^{-1}(t)\mathbf{W}_K + \mathbf{b}_K)\mathbf{R}_{\Theta_t}(t)$；若漏推論重施 RoPE，Qwen3 14B→32B 的 MMLU 崩至 **25.79%**、GSM8K 崩至 **4.17%**；解耦後可推廣至 **32K** 上下文 `[Cross-Model KV, §3.3, §4.3, Table 2, p.5–7]`。
