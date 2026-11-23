---
title: "Cross-Model KV Cache Transfer：同家族跨尺寸模型的閉式線性映射"
type: "paper"
sources:
  - "raw/05-cross-model-kv-transfer-2608.03893v1.md"
updated: "2026-11-23"
---

# Cross-Model KV Cache Transfer in LLM Families: A Closed-Form Linear Mapping for Prefill Reuse

- **原始來源**：[05-cross-model-kv-transfer-2608.03893v1.md](../../raw/05-cross-model-kv-transfer-2608.03893v1.md)（`arXiv:2608.03893v1`，2026 年 8 月）
- **作者與單位**：Taekyung Heo、Rasoul Shafipour、Ritchie Zhao、Maximilian Golub、Mohammad Mahdi Kamani、Ritika Borkar、Makesh Tarun Chandran、Pantea Zardoshti、Bita Darvish Rouhani（NVIDIA）

## 1. 核心痛點與差異定位
- **多模型編排的重複 Prefill 代價**：生產級 LLM 服務大量採用成本–品質級聯（cascading）、對話中途切換（mid-conversation switching）與路由器（routing），在同一模型家族不同尺寸模型間雙向切換（小→大升品質、大→小省成本）；每次切換接收端都必須對累積長上下文重新 Prefill `[Cross-Model KV, §1, Fig. 1, p.1–2]`。
- **與既有跨模型方法的根本差別**：如 Table 6 所示，C2C 與 LatentAlign 需反向傳播梯度訓練、IAM 只轉移注意力模式而非 KV 值、[DroidSpeak](./droidspeak.md) 雖無須梯度訓練但限定於**架構完全相同**的模型；本文是唯一同時滿足「**無梯度（gradient-free）、跨尺寸（cross-scale）、直接轉移 KV 值、且具閉式解（closed-form）**」的方法 `[Cross-Model KV, §2.2, Table 6, p.3, 13]`。
- **關鍵前提（Matched-KV Pairs）**：源模型 $\mathcal{S}$ 與目標模型 $\mathcal{T}$ 雖層數 $L_s \ne L_t$ 且參數量不同，但共享同一 tokenizer、KV 頭數（$n_{\text{kv}}^s = n_{\text{kv}}^t = 8$）與單頭維度（$d_h^s = d_h^t = 128$）`[Cross-Model KV, §2.1, Table 10, p.2, 16]`。

## 2. 跨模型線性結構與三步驟閉式 Ridge Mapper
- **線性結構實證**：在 Qwen3 14B→32B 上，單一源層線性回歸即可解釋目標 K 的 **56%** 變異（$R^2 = 0.5572$）與 V 的 **32%**（$R^2 = 0.3249$）；聚合 $k=8$ 個源層後分別躍升至 **79%**（$0.7914$）與 **65%**（$0.6541$）`[Cross-Model KV, Abstract, §2.3, Fig. 2, Table 7, p.1, 3–4, 14]`。
- **三大核心元件（Fig. 3）**：
  1. **Per-Head Ridge Regression（逐頭嶺回歸）**：對每個目標 `(layer l, head h)` 的 K、V 分別求閉式解 $\mathbf{W}^* = (\mathbf{X}^\top \mathbf{X} + \lambda \mathbf{I})^{-1}\mathbf{X}^\top \mathbf{Y}$（$\lambda = 0.01$）。僅需 **500 條 FineWeb-Edu 序列（每條 1,024 tokens，stride 4 取樣 $N \approx 128\text{K}$ tokens）**，在單台 8×H100 上約 **47–87 分鐘**即可擬合完成，完全無需反向傳播；Mapper 體積為 **1.01–3.36 B 參數（4–12 GB）**，可常駐主機 DRAM／磁碟按需載入（PCIe Gen4/5 約 80–480 ms）`[Cross-Model KV, §3.1, Eq. 3–4, Table 12, Appendix E, p.4–5, 17]`。
  2. **Cross-Layer Source Selection（跨層 top-$k$ 源層選擇）**：為每個目標層依 head-averaged $R^2$ 挑選最具預測力的前 $k$ 個源層串接其所有 KV 頭；此元件在消融中貢獻最大（$k$ 從 8 降至 1 使 $K\ R^2$ 從 0.79 掉至 0.56，GSM8K 由 90.98% 崩跌至 0.38%）`[Cross-Model KV, §3.2, §4.3, Table 2, Table 7, p.5–7, 14]`。
  3. **Content-Space Mapping / RoPE Factoring（詳見 [RoPE 位置對齊](../concepts/rope-position-alignment.md)）**：先剝除源 RoPE、在無位置內容空間套用 $\mathbf{W}_K$，再重新編碼目標 RoPE：$\hat{\mathbf{K}}_t = (\mathbf{K}_s \mathbf{R}_{\Theta_s}^{-1}(t)\mathbf{W}_K + \mathbf{b}_K)\mathbf{R}_{\Theta_t}(t)$，使 1,024-token 擬合結果可泛化至不同 RoPE 設定與長達 32K 上下文 `[Cross-Model KV, §3.3, p.5]`。

## 3. 關鍵實驗結果與深度機制分析
- **三大家族六組 Matched-KV 配對（5 項主基準，Table 1 & Table 13）**：
  - **Tier 1（4 組高保真，平均保留 73–98%）**：Qwen3 14B→32B（$k=8$）**97.6%**（ARC-C 101.0%、GSM8K 95.6%）、Qwen3 8B→32B（$k=12$）**87.5%**、Ministral 3 3B→8B（$k=\text{all}$）**76.2%**、Llama 3.1 8B→70B（$k=20$，8.8× 參數量落差）**72.8%** `[Cross-Model KV, §4.2, Table 1, p.6]`。
  - **Tier 2（2 組急劇退化）**：Ministral 3 3B→14B **44.2%**（floor-normalized 14.7%）、Ministral 3 8B→14B **41.6%**（floor-normalized 11.1%）`[Cross-Model KV, §4.2, Table 1, Table 15, p.6, 18]`。
  - **三項未參與選 $k$ 的留出基準（PIQA/BoolQ/ARC-Easy, Table 18）**：Tier 1 四組全數超過 **96%**，Tier 2 皆低於 64% `[Cross-Model KV, Appendix H, Table 18, p.21]`。
- **非線性 MLP 救援（§4.4, Table 3）**：在失敗的 Tier 2 配對上改用 2 層 1,024-unit ReLU MLP（同 MSE 損失），HellaSwag 保留率大幅拉回 **+24.3 pp**（Ministral 3B→14B：68.0%→92.3%）與 **+36.8 pp**（8B→14B：58.7%→95.5%），使四組測試配對全破 90%；但在線性已成功的 Tier 1 上 MLP 反而微幅低於 Ridge（−0.3 至 −1.5 pp）`[Cross-Model KV, §4.4, Table 3, p.7]`。
- **轉移品質真正決定因素（詳見 [KV 偏差衡量指標](../concepts/kv-deviation-metrics.md)）**：
  - 跨 12 組配對評估（6 組 S→L + 6 組 L→S），校準集 $R_K^2$ 與 HellaSwag 保留率幾乎無關（Pearson **$r = -0.20$**），而 **Attention-Output Cosine** 相關性達 **$r = +0.57$** `[Cross-Model KV, §4.5, p.7–8]`。
  - 關鍵不在誤差「大小」，而在誤差「落點（**K-concentration**）」：MLP 之所以在 Tier 2 救回 +37 pp，是因它把殘差從目標 Query 敏感子空間重新分配到注意力忽略的方向（$\Delta \text{K-conc} \approx -2.5$、$\Delta \text{cosine} \approx +0.45$）`[Cross-Model KV, §4.5, Table 4, p.8]`。
- **多輪交棒與 Prefill 延遲（§4.6–4.7）**：
  - CoQA 10 輪交替交棒（Qwen3 14B↔32B）：S→L 落差 10 輪僅擴大 1.7 pp；L→S 呈 0.33 pp／輪線性微漂移，未發生級聯崩潰 `[Cross-Model KV, §4.6, Fig. 4, p.8–9]`。
  - 延遲加速（8×H100 NVLink, 64–32K tokens）：S→L 快 **2.7–25.1×**（Qwen3 14B→32B 於 32K 為 **278 ms vs 6,975 ms = 25×**；Llama 3.1 8B→70B 為 **777 ms vs 11,562 ms = 14.9×**）；L→S 快 **2.8–7.6×** `[Cross-Model KV, §4.7, Table 5, Table 16, p.8–9, 19]`。

> [!WARNING] ⚠️ 跨文獻張力／差異
> - **同架構選擇性重算（DroidSpeak）vs. 跨尺寸閉式映射（Cross-Model KV Transfer）**：[DroidSpeak](./droidspeak.md) 假設跨模型共享必須具備相同架構（同層數與維度），且靠重算連續關鍵層與傳輸 E-cache 修正誤差 `[DroidSpeak, §3.1, §4.1, p.4, 6]`；本論文則證明在同家族不同尺寸（matched-KV）模型間可直接透過閉式線性映射完全跳過重算，但仍無法保證所有 matched-KV 配對皆呈線性（如 Ministral 3→14B 須改用非線性 MLP）`[Cross-Model KV, §4.2, §4.4, Table 6, p.6–7, 13]`。
> - **重建誤差 $R^2$ 無法預測跨配對下游品質**：本論文反駁「高 $R^2$ 等於高轉移品質」的直覺（$r = -0.20$），強調必須改看 Attention-Output Cosine（$r = +0.57$）與注意力敏感子空間誤差落點 `[Cross-Model KV, §4.5, Table 4, p.7–8]`。詳見 [跨文獻張力與差異彙整](../syntheses/conflicts-and-tensions.md)。

## 4. 限制與後續連結
- 限於同家族、dense full-attention 且 matched-KV 配對；跨家族（如 Qwen3→Llama 3.1）、mismatched-KV 與混合注意力／SSM（如 Nemotron 3）尚待研究；校準域僅用 FineWeb-Edu（換 CodeAlpaca 會在 HellaSwag 掉 5.24 pp，Table 8–9）`[Cross-Model KV, §5, Appendix C, p.9, 15–16]`。
- 延伸閱讀：[KV 偏差衡量指標](../concepts/kv-deviation-metrics.md)、[RoPE 位置對齊](../concepts/rope-position-alignment.md)、[跨論文方法全景對照](../syntheses/kv-reuse-landscape.md)。
