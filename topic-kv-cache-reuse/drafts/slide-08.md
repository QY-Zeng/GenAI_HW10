# Slide 08：DroidSpeak：同底模微調模型間的連續層選擇性重算

- **頁碼**：08 / 12
- **來源卡片**：`cards/card-02-droidspeak.md`
- **Wiki 出處**：`wiki/papers/droidspeak.md`

## 核心內容
- **跨微調模型痛點**：源自同一基礎模型的不同微調版本（如 LoRA／領域特化模型）共享長上下文時，直接全盤重用 baseline KV 會導致 HotpotQA 損失 **>50%** F1 `[DroidSpeak, §1, §3.2.1, Fig. 6, p.1, 4–5]`。
- **關鍵洞察與 E-Cache 切換陷阱**：
  - 平均僅 **11%** 的網路層屬於對微調敏感的關鍵層（單層重用即掉 >10% F1）`[DroidSpeak, §3.2.2, Fig. 7, p.5–6]`。
  - **為何不能只重算散落的關鍵層？** 每次從「重用」切回「重算」都必須傳輸 baseline 的 **E cache**（體積達 KV Cache 的 **2×** 至 GQA 70B 的 **4×**），且多次注入帶偏差 E cache 會放大累積誤差 `[DroidSpeak, §4.1, Fig. 9–11, p.6–7]`。
- **單一切換點設計＋SLO 動態調度**：
  - 採 `recompute → reuse → recompute → reuse` 連續重算區間，限制至多 **1 次** E-cache 切換；離線用 50 筆 HotpotQA 剖析帕累托前緣（跨資料集平均誤差僅 **2 分** F1），線上依延遲 SLO 動態調整 `[DroidSpeak, §4.2–4.4, §5.1, §5.5, Fig. 12–13, 17, p.7–11]`。
- **核心成效（8 組模型配對 × 3 資料集）**：Prefill 延遲降 **1.7–2.6×**、線上吞吐升 **2–3×**（掉點 ≤ 1%）、共享記憶體省 **1.5×**，InfiniBand 傳輸僅佔最多 **11%** `[DroidSpeak, §5.2–5.4, Fig. 1, 14–16, p.1, 9–11]`。
- **頁尾出處**：`wiki/papers/droidspeak.md`｜`[DroidSpeak, §3.2–5.5, Fig. 6–17, p.4–11]`
