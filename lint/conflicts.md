---
name: conflicts
description: 來源之間、或來源與二手說法之間的衝突紀錄與處理決定（不覆蓋、不抹平，寫明採用哪個以及為什麼）
sources: [S1, S2, S3, S4, S5, S6]
---

# 衝突紀錄

| ID | 衝突 | 處理 |
|---|---|---|
| L1 | 搜尋結果裡的部落格與轉載頁，對 SGLang 寫出 10×、5× 的加速，以及「vLLM hit rate 為 0」之類的表格；這些數字在 S2 全文中找不到。 | 不採用。數字一律取 S2 全文：**最高 6.4× 吞吐、最高 3.7× 延遲降低** [C15]。 |
| L2 | S3 自己的摘要/結論寫「GPU 最高 8×、CPU 最高 60×」，§5.2 的詳細範圍寫 GPU 1.5×–10×、CPU 20×–70×。同一篇論文內部不一致。 | 兩組都留在帳本 [C27]，簡報只用「GPU 約 1.5–10×、CPU 約 20–70×（論文摘要寫 8× 與 60×）」，並指明脈絡。 |
| L3 | Prompt Cache 的準確度：S3 說沒有明顯損失；S2 轉述「最高可能掉 43%」；S4 說 full KV reuse 忽略 cross-attention 會降低品質。 | 三個都記 [C28][C39][C29]。結論寫成「不同設定下的結果不同，沒有通則」，簡報不給單一數字當結論。 |
| L4 | S4 的引言寫「相較 prefix caching 降 TTFT 2.2–3.3×、三個資料集」；摘要與 §7 寫「相較 full KV recompute、四個資料集」，並另外說同樣 TTFT 下吞吐最多比 prefix caching 高 3.3×。 | 以 §7 的拆分為準 [C31][C32]：2.2–3.3× 的基線是 full KV recompute；3.3× 的吞吐優勢才是對 prefix caching。 |
| L5 | Anthropic 文件：官方現行頁面與舊版鏡像/第三方轉載不同（舊模型清單、讀取價固定 0.1×、最小長度 1,024/2,048）。 | 以官方現行頁面為準 [C21][C22]，簡報價格頁加註「以官方文件為準，取得日 2026-11-15」。 |
| L6 | S2 論文寫 radix tree 的 page 大小為 1 token；第三方文件顯示 SGLang 現行實作的 page 大小可調；S6 的 vLLM 以 block 為單位。 | 簡報只說「論文中 page=1 token [C37]」與「vLLM 以 block 為單位 [C10]」，不聲稱現行程式碼細節。 |
| L7 | S1 的 20.4%–38.2% 與「block 預設 16、copy-on-write」只出現在 WebFetch 擷取摘要，我的搜尋沒能在原文片段中重現。 | 標 `extract-only` [C38][C42]，簡報不使用。 |
| L8 | S6 的 WebFetch 回傳的是工具擷取，不是原文。其中 free queue 順序、`cache_salt`、sha256 為 `extract-only`。 | [C11][C12] 標 `extract-only`；簡報只講 hash 鏈的概念 [C10]，不講 sha256 或淘汰順序。 |
