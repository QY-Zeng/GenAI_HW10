# 證據卡 04：RelayCaching

- **唯一來源頁**：`wiki/papers/relaycaching.md`（嚴禁混入其他來源）
- **核心問題**：多代理系統（MAS）中上游輸出成為下游輸入，因角色提示不同產生 **prefix variation**，導致傳統系統反覆重新 Prefill，累積成本隨互動輪數 $M$ 呈二次方 $O(M^2)$ 成長；Prefix Caching 失效、靜態 Pre-computed Caching 不適用動態輸出、KVCOMM 隨代理增加重用率由 **88% 滑落至 70%** `[RelayCaching, §1, §2.2–2.3, §5.2, Fig. 1, p.1–3, 7]`。
- **三大實證發現（橫跨 0.6B–32B 六模型驗證）**：
  1. Decoding KV 與 Full-Prefill KV 高度對齊（Key Norm 0.947、Value Norm 0.926、Key Cosine 0.935），唯獨 **Value Cosine（0.800）** 為主要偏差訊號 `[RelayCaching, §3.1, Fig. 2, p.3]`。
  2. 層間 Value Cosine 呈 **U 型曲線**：淺層與深層穩定，**中層**偏差最大且主導輸出品質 `[RelayCaching, §3.2, Fig. 3, 9, p.3–4, 12]`。
  3. Token 偏差高度稀疏且相鄰層 Spearman 排名相關性迅速穩定於 **> 0.9** `[RelayCaching, §3.3, Fig. 4, 10, p.4, 13]`。
- **核心機制**：
  - 上游解碼保存 **Pre-RoPE KV**、$h^{(L_{\text{start}})}$ 與累計注意力影響分數 $s_{\text{inf}}(j)$；交棒時重新施加 RoPE `[RelayCaching, §4.2–4.3, Fig. 5, p.5–6]`。
  - **Layer-Range Profiler**（離線剖析）：僅修正中層 $[L_{\text{start}}, L_{\text{end}}]$，跳過淺層與深層，於穩定層 $L_{\text{det}}$ 偵測 `[RelayCaching, §4.2, Table 5, p.5, 14]`。
  - **Dual-Criterion Token Selector**：取偏差（$d_{j,L_{\text{det}}} \ge 1.5 \mu_{\text{dev}}$）∪ 注意力影響力（$s_{\text{inf}}(j) \ge 1.45 \mu_{\text{inf}}$）∪ 尾端 **10 tokens**（$I_{\text{inf-suffix}}$），缺一不可（GSM8K 消融：僅偏差掉至 79.68%，三者合一回升至 **84.84%** 且維持 **85.35%** 重用率）`[RelayCaching, §4.3, §5.4, Table 3, p.6, 8]`。
- **關鍵數據**：
  - GSM8K、MMLU、HumanEval 上重用率穩定 **>80%** 且齊平 Full Prefill（GSM8K 4-agent：85.17% vs Full 84.69%，反超 CacheBlend 74.73%）`[RelayCaching, §5.2, Table 1, p.6–7]`。
  - AIME24（Qwen3-0.6B）5 代理 TTFT 加速 **4.71×**（104.8 ms vs 493.9 ms）；12,288 tokens 時達 **0.42 s**（較 Full 3.89 s 快 **9.2×**、較 CacheBlend 1.08 s 快 **2.5×**，呈次線性擴展）`[RelayCaching, §5.3, Table 2, Fig. 8, p.7–8]`。
- **邊界與限制**：限於**同質多代理（同模型架構與權重）** `[RelayCaching, Appendix C, p.18]`。
