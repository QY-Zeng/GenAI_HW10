# 證據卡 02：DroidSpeak

- **唯一來源頁**：`wiki/papers/droidspeak.md`（嚴禁混入其他來源）
- **核心問題**：多代理與多微調模型系統中，衍生自**同一基礎模型**的多個微調變體共享相同長上下文卻各自重複 Prefill；直接全盤重用 baseline KV 會讓 HotpotQA 損失 **>50%** F1 `[DroidSpeak, §1, §3.2.1, Fig. 6, p.1, 4–5]`。
- **核心洞察**：
  - 平均僅 **11%** 的網路層屬於對微調敏感的 **critical layers**（單層重用即掉 >10% F1），且輸入變異幾乎只集中在關鍵層 `[DroidSpeak, §3.2.2–3.2.3, Fig. 7–8, p.5–6]`。
  - 若零散重算關鍵層，每次 `reuse → recompute` 切換都須傳輸 baseline **E cache**（Mistral-7B／Llama-3-8B 上達 KV 的 **2×**、GQA Llama-3.1-70B 達 **4×**），且每次載入都會放大累積誤差 `[DroidSpeak, §4.1, Fig. 9–11, p.6–7]`。
- **核心機制**：
  - **單一切換點連續層重算**：採用 `recompute → reuse → recompute → reuse`，將 E-cache 切換次數限縮至**最多 1 次** `[DroidSpeak, §4.2, p.7]`。
  - **兩階段系統**：離線用 50 筆 HotpotQA 剖析準確度–效率帕累托前緣（跨資料集泛化誤差平均僅 **2 分** F1）；線上依延遲 SLO 動態調整重算區間 `[DroidSpeak, §4.3–4.4, §5.1, §5.5, Fig. 12–13, 17, p.7–11]`。
- **關鍵數據**：
  - 跨 8 組模型配對 × 3 個 LongBench 資料集：Prefill 延遲降低 **1.7–2.6×**，品質無明顯損失 `[DroidSpeak, §5.2, Fig. 14, p.9–10]`。
  - 線上服務於掉點 ≤ 1% 條件下提升 **2–3×**（最高 **3×**）吞吐量；共享儲存記憶體省 **1.5×** `[DroidSpeak, §1, §5.3, Fig. 1, 15, p.1, 10–11]`。
  - InfiniBand 傳輸 KV + E cache 僅佔總 Prefill 延遲最多 **11%** `[DroidSpeak, §5.4, Fig. 16, p.10–11]`。
- **邊界與限制**：嚴格要求**同底模且架構完全相同**（層數、隱藏維度、KV 頭數皆須一致）`[DroidSpeak, §3.1, §6, p.4, 12]`。
