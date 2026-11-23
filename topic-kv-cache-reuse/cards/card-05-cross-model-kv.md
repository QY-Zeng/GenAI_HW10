# 證據卡 05：Cross-Model KV Cache Transfer

- **唯一來源頁**：`wiki/papers/cross-model-kv-transfer.md`（嚴禁混入其他來源）
- **核心問題**：多模型編排（級聯、對話中途切換、路由）在同一家族不同尺寸模型間切換時，接收端每次都必須重頭 Prefill；既有方法或需梯度訓練（C2C、LatentAlign）、或僅轉移注意力模式（IAM）、或限同架構（DroidSpeak）`[Cross-Model KV, §1, §2.2, Table 6, p.1–3, 13]`。
- **核心發現（Matched-KV Pairs）**：在共享 KV 頭數（8）與單頭維度（128）的同家族跨尺寸模型間，跨模型 KV 具顯著線性結構——Qwen3 14B→32B 單源層解釋 K **56%**、V **32%** 變異，取 $k=8$ 源層升至 **79%** 與 **65%** `[Cross-Model KV, §2.1, §2.3, Table 7, p.2–4, 14]`。
- **三步驟閉式 Ridge Mapper（無梯度訓練）**：
  1. **逐頭嶺回歸**：$\mathbf{W}^* = (\mathbf{X}^\top \mathbf{X} + \lambda \mathbf{I})^{-1}\mathbf{X}^\top \mathbf{Y}$（$\lambda = 0.01$），僅需 **500 條 FineWeb-Edu 序列（1,024 tokens）**、單台 8×H100 約 **47–87 分鐘**擬合；Mapper 體積 **4–12 GB**（1.01–3.36 B 參數）`[Cross-Model KV, §3.1, Table 12, Appendix E, p.4–5, 17]`。
  2. **跨層 top-$k$ 源層選擇**：消融中貢獻最大（$k=8 \to 1$ 使 GSM8K 由 90.98% 崩跌至 0.38%）`[Cross-Model KV, §3.2, §4.3, Table 2, p.5–7]`。
  3. **無位置內容空間映射（RoPE Factoring）**：剝除源 RoPE → 線性映射 → 重施目標 RoPE，泛化至 32K 上下文（若漏推論重施 RoPE，MMLU 崩至 25.79%、GSM8K 崩至 4.17%）`[Cross-Model KV, §3.3, §4.3, Table 2, p.5–7]`。
- **關鍵數據與機制突破**：
  - **Tier 1（4 組高保真）**：平均保留 **73–98%** 準確率（Qwen3 14B→32B **97.6%**、8B→32B **87.5%**、Ministral 3B→8B **76.2%**、Llama 3.1 8B→70B **72.8%**）；3 項留出基準全破 **96%** `[Cross-Model KV, §4.2, Table 1, Table 18, p.6, 21]`。
  - **Tier 2（2 組失敗）與 MLP 救援**：Ministral 3B→14B（44.2%）與 8B→14B（41.6%）線性失敗；換用 2 層 ReLU MLP 救回 **+24.3 至 +36.8 pp**（HellaSwag 全破 90%）`[Cross-Model KV, §4.2, §4.4, Table 1, 3, p.6–7]`。
  - **誤差落點 > 誤差大小**：跨 12 組評估，校準集 $R_K^2$ 與保留率幾乎無關（Pearson **$r = -0.20$**），而 **Attention-Output Cosine** 達 **$r = +0.57$**；MLP 透過降低 K-concentration（$\Delta \approx -2.5$）將誤差移出注意力敏感子空間 `[Cross-Model KV, §4.5, Table 4, p.7–8]`。
  - **延遲與多輪**：S→L 加速 **2.7–25.1×**（Qwen3 14B→32B 於 32K 為 **278 ms vs 6,975 ms = 25×**）；CoQA 10 輪交棒穩定 `[Cross-Model KV, §4.6–4.7, Table 5, 16, p.8–9, 19]`。
- **邊界與限制**：限同家族、dense full-attention、matched-KV 配對 `[Cross-Model KV, §5, p.9]`。
