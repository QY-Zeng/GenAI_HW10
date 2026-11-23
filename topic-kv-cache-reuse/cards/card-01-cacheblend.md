# 證據卡 01：CacheBlend

- **唯一來源頁**：`wiki/papers/cacheblend.md`（嚴禁混入其他來源）
- **核心問題**：RAG 多區塊輸入中，Prefix Caching 僅能重用第 1 個 chunk；Full KV Reuse（PromptCache）雖補回位置編碼但完全忽略跨區塊 cross-attention（如 Messi 13 球 vs Ronaldo 8 球案例），導致生成品質崩潰 `[CacheBlend, §3.2–3.3, Fig. 1, 3–4, p.2–5]`。
- **核心機制**：
  - **Token 級選擇性重算（HKVD）**：利用注意力稀疏性，僅重算每層約 **10–15%**（系統保底 15%，實測 **5%–18%**）高 KV 偏差 tokens；以首層全算＋逐層 **Gradual Filtering** 動態篩選 `[CacheBlend, §4.3, §5.1, §7.3, Fig. 6–9, 16, p.6–8, 12]`。
  - **RoPE 單次旋轉校正**：利用 RoPE 相對距離不變性，一次性乘上旋轉矩陣恢復位置 `[CacheBlend, Footnote 3, p.6; Appendix A, p.16]`。
  - **計算–載入逐層管線化**：雙執行緒重疊第 $i$ 層 `prefill_layer` 與第 $i+1$ 層 `fetch_kv`；Loading Controller 依 $T_{\text{recompute}}$ 與 $T_{\text{load}}$ 挑選重算比例或最便宜儲存裝置 `[CacheBlend, §5.1, §6, Fig. 10–11, p.8–9]`。
- **關鍵數據**：
  - 4K tokens Prefill 在單張 A40 需 3–6 秒（Llama-34B／70B）`[CacheBlend, §2, p.3]`。
  - TTFT 降低 **2.2–3.3×**、吞吐提升 **2.8–5×**（較 Prefix Caching 高 **3.3×**）`[CacheBlend, §7, §7.2, Fig. 12, 14, p.10–12]`。
  - F1／Rouge-L 損失 **≤ 0.02**（Yi-34B 5%–18% 時 **≤ 0.002**，對應 4.1–6.6× TTFT 縮減）；較 Full KV Reuse 提升 0.1–0.2 F1 與 0.03–0.25 Rouge-L `[CacheBlend, §7.2–7.3, Fig. 16, p.12]`。
- **邊界與限制**：限 Transformer 架構；聚焦靜態預計算文字區塊 `[CacheBlend, §9, p.13]`。
