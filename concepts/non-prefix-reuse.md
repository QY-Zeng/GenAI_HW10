---
name: non-prefix-reuse
description: 當可重用的內容不在輸入開頭時怎麼辦：Prompt Cache（模組化）與 CacheBlend（選擇性重算），以及品質與位置編碼的取捨
sources: [S3, S4, S2]
---

# 非 prefix 的 KV 重用

## 問題
- [C29] Prefix caching 只能重用開頭；RAG 把多個檢索 chunk 放進輸入，只有第一個 chunk 是 prefix。直接重用其他 chunk 的 KV（full KV reuse）又會忽略 chunk 之間的 cross-attention，可能答錯。 [S4]
- [C25] 另一個難點是位置編碼讓 attention states 與位置有關。 [S3]

## 做法 A：Prompt Cache（模組化）
- [C25] 用 schema（PML）把可重用文字段定義成 prompt modules，預先算好存起來；論文觀察 LLM 能處理不連續的 position IDs。 [S3]
- [C28] 各 module 獨立編碼，跨 module 的 attention 被遮蔽：module 語意獨立時可能無害甚至降低雜訊，相依時品質可能變差。 [S3]
- [C27] TTFT 改善：摘要與結論為 GPU 最高 8×、CPU 最高 60×；§5.2 的範圍為 GPU 1.5×–10×、CPU 20×–70×。 [S3]
- [C26] 只降 TTFT，每個 token 的生成時間不變（TTFT 900 ms → 90 ms；約 32 ms／token）。 [S3]
- [C07] 記憶體成本：Llama 70B 快取 1K tokens 的 module 要 2.5 GB。 [S3]

## 做法 B：CacheBlend（選擇性重算）
- [C30] 重用預先算好的 KV，再選擇性重算少量 KV deviation 高的 token（HKVD tokens）；預設約 15%，10–20% 通常足夠；重算與載入以 pipeline 重疊。 [S4]
- [C31] 相較 full KV recompute：TTFT 降 2.2–3.3×、吞吐升 2.8–5×、品質下降不超過 0.01–0.03；吞吐最多比 prefix caching 高 3.3×。 [S4]
- [C32] 三個模型、四個資料集，實作於 vLLM。 [S4]
- [C34] 限制：未驗證於 Mamba 等非 transformer 架構。 [S4]

## 來源之間的分歧（必讀）
- [C39] S2 說 Prompt Cache 準確度最高可能掉 43%；S3 說沒有明顯損失；S4 說忽略 cross-attention 會讓品質下降。三者在不同設定下測量，**不要把任何一個數字當成通則**。見 `lint/conflicts.md` L3。 [S2][S3][S4]
