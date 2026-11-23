# Slide 07：RelayCaching：化解多代理系統 $O(M^2)$ 級聯冗餘

- **頁碼**：07 / 12
- **來源卡片**：`cards/card-04-relaycaching.md`
- **Wiki 出處**：`wiki/papers/relaycaching.md`

## 核心內容
- **多代理痛點**：Architect → Developer → Reviewer 接力時，上游動態輸出嵌入下游不同角色提示（prefix variation），使傳統系統每輪從頭 Prefill，成本隨輪數呈 $O(M^2)$ 暴增 `[RelayCaching, §1, Fig. 1, p.1–2]`。
- **三大跨模型實證規律（0.6B–32B 六模型驗證）**：
  1. 解碼 KV 與完整 Prefill 的 Key/Value Norm 皆 >0.92，唯獨 **Value Cosine（0.800）** 是主要偏差指標 `[RelayCaching, §3.1, Fig. 2, p.3]`。
  2. 層間 Value Cosine 呈 **U 型曲線**：淺層與深層穩定，僅**中層**偏差最大 `[RelayCaching, §3.2, Fig. 3, 9, p.3–4, 12]`。
  3. Token 偏差稀疏且相鄰層 Spearman 排名相關性迅速穩定 **> 0.9** `[RelayCaching, §3.3, Fig. 4, 10, p.4, 13]`。
- **層×Token 雙維稀疏修正**：
  - 離線鎖定中層 $[L_{\text{start}}, L_{\text{end}}]$ 與偵測層 $L_{\text{det}}$（跳過淺／深層），搭配 **偏差（1.5×均值）∪ 注意力影響力（1.45×均值）∪ 尾端 10 tokens** 三合一選擇 `[RelayCaching, §4.2–4.3, Fig. 5, p.5–6]`。
- **核心成效與邊界**：GSM8K／MMLU／HumanEval 重用率 **>80%** 且齊平 Full Prefill（GSM8K 消融：僅偏差掉至 79.68%，三合一拉回 **84.84%**）；5 代理 TTFT 快 **4.71×**、12K 長文達 **0.42 s**（較 Full 快 **9.2×**、次線性擴展）；目前限**同質多代理**（同架構同權重）`[RelayCaching, §5.2–5.4, Table 1–3, Fig. 8, Appendix C, p.6–8, 18]`。
- **頁尾出處**：`wiki/papers/relaycaching.md`｜`[RelayCaching, §3–5, Table 1–3, Fig. 2–5, 8, p.3–8]`
