# Slide 09：Cross-Model KV Transfer：跨尺寸模型的閉式線性映射

- **頁碼**：09 / 12
- **來源卡片**：`cards/card-05-cross-model-kv.md`
- **Wiki 出處**：`wiki/papers/cross-model-kv-transfer.md`

## 核心內容
- **突破同架構限制**：在級聯、路由與對話切換中，源與目標模型尺寸與層數不同；NVIDIA 發現針對同家族、dense full-attention 且 **Matched-KV**（KV 頭數 8、單頭維度 128 相同）配對，跨模型 KV 常具顯著線性結構（Qwen3 14B→32B 單層解釋 K **56%**、$k=8$ 層達 **79%**）`[Cross-Model KV, §2.1, §2.3, §5, Table 7, p.2–4, 9, 14]`。
- **三步驟無梯度閉式 Ridge Mapper**：
  1. **跨層 top-$k$ 源層選擇**（消融貢獻最大：$k=8 \to 1$ 使 GSM8K 從 90.98% 崩至 0.38%）`[Cross-Model KV, §3.2, §4.3, Table 2, p.5–7]`。
  2. **無位置內容空間映射**：剝除源 RoPE → 映射 → 重施目標 RoPE，泛化至 32K 長文 `[Cross-Model KV, §3.3, p.5]`。
  3. **逐頭嶺回歸閉式解**：500 條 FineWeb-Edu 序列於 8×H100 約 **47–87 分鐘**擬合，免反向傳播；Mapper 佔 **4–12 GB** `[Cross-Model KV, §3.1, Table 12, Appendix E, p.4–5, 17]`。
- **分層表現與 MLP 救援**：
  - **Tier 1（4 組高保真）**：平均保留 **73–98%**（Qwen3 14B→32B **97.6%**、Llama 3.1 8B→70B **72.8%**）；S→L 加速 **2.7–25.1×**（Qwen3 14B→32B 於 32K 為 **278 ms vs 6,975 ms = 25×**），CoQA 10 輪穩定 `[Cross-Model KV, §4.2, §4.6–4.7, Table 1, 5, 16, p.6, 8–9, 19]`。
  - **Tier 2（2 組失敗）**：Ministral 3B→14B（44.2%）與 8B→14B（41.6%）線性失效；換用 2 層 MLP 救回 **+24.3 至 +36.8 pp**（HellaSwag 全破 90%）`[Cross-Model KV, §4.2, §4.4, Table 1, 3, p.6–7]`。
- **頁尾出處**：`wiki/papers/cross-model-kv-transfer.md`｜`[Cross-Model KV, §2.3–4.7, Table 1–3, 5, 7, 12, 16, p.3–9, 14–19]`
