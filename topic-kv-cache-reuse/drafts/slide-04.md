# Slide 04：CacheBlend：RAG 多區塊融合與 HKVD 選擇性重算

- **頁碼**：04 / 12
- **來源卡片**：`cards/card-01-cacheblend.md`
- **Wiki 出處**：`wiki/papers/cacheblend.md`

## 核心內容
- **直覺案例（為何 Full KV Reuse 會答錯？）**：
  - 獨立預計算 Chunk 1「Messi 進 13 球」與 Chunk 2「Ronaldo 進 8 球」並直接拼接，即便修好位置編碼，仍完全缺失跨區塊 **cross-attention**，導致模型胡言亂語 `[CacheBlend, §3.3, Fig. 3–4, p.4–5]`。
- **三大關鍵設計**：
  1. **HKVD 選擇性重算＋漸進過濾**：受惠於注意力稀疏性，僅需重算每層約 **10–15%**（實測 **5%–18%**，保底 **15%**）高偏差 tokens，首層全算後逐層過濾 `[CacheBlend, §4.3, §5.1, §7.3, Fig. 6–9, p.6–8, 12]`。
  2. **RoPE 單次旋轉校正**：利用相對距離不變性，一次性乘法對齊非前綴位置 `[CacheBlend, Footnote 3, p.6; Appendix A, p.16]`。
  3. **計算–載入逐層管線化**：重疊第 $i$ 層重算與第 $i+1$ 層 SSD／RAM 載入，讓重算延遲被載入時間隱藏 `[CacheBlend, §5.1, §6, Fig. 10–11, p.8–9]`。
- **核心成效**：TTFT 降 **2.2–3.3×**、吞吐升 **2.8–5×**（較 Prefix Caching 高 **3.3×**）、F1／Rouge-L 損失 **≤ 0.02**（Yi-34B 僅 **≤ 0.002**）`[CacheBlend, §7, §7.2–7.3, Fig. 12, 14, 16, p.10–12]`。
- **頁尾出處**：`wiki/papers/cacheblend.md`｜`[CacheBlend, §3.3–7.3, Fig. 3, 6–12, 16, p.4–12]`
