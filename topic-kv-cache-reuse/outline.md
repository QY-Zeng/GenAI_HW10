# Node 4 產出：教學簡報大綱 (`outline.md`)

- **簡報標題**：KV Cache Reuse：從單模型前綴快取到多代理與跨模型重用
- **目標讀者**：修課同學與研究入門者（直覺導讀為主，輔以精準實驗數據與跨文獻張力對照）
- **總頁數**：12 頁（符合 8–15 頁規範）
- **知識邊界**：100% 源自 `cards/card-01` 至 `card-10`（對應 `wiki/` 已驗證頁面）

| 頁碼 | 投影片標題 | 教學重點與直覺切入 | 視覺／排版建議 | 綁定證據卡（Node 6 唯一輸入） |
| --- | --- | --- | --- | --- |
| 01 | **KV Cache Reuse：打破 LLM 重複閱讀的算力枷鎖** | 封面頁：點出長上下文 RAG、多代理與多模型路由中「反覆重算 Prefill」的核心痛點，預告 5 篇里程碑論文的演進路線。 | 深藍漸層封面＋五大里程碑時間軸徽章 | `cards/card-10-overview.md` |
| 02 | **為什麼 Prefill 是推理系統的頭號瓶頸？** | 白話拆解 Prefill（二次方計算）vs Decode（線性記憶頻寬），說明 TTFT、ITL/TBT、Goodput 與「Prefill 干擾」，以及傳統 Prefix Caching 的三重限制（同模型、同 GPU、嚴格前綴）。 | 左右對照卡（Prefill vs Decode）＋三重枷鎖圖示 | `cards/card-06-metrics-and-prefill.md`, `cards/card-10-overview.md` |
| 03 | **五篇論文如何突圍？三軸演進全景圖** | 用三個直覺問題串起 5 篇論文：(1) 存不下／怎麼搬（LMCache）、(2) 前綴變了怎麼辦（CacheBlend → RelayCaching）、(3) 換了模型還能用嗎（DroidSpeak → Cross-Model KV）。 | 三軸架構圖＋五篇定位卡片 | `cards/card-07-landscape.md`, `cards/card-10-overview.md` |
| 04 | **CacheBlend：RAG 多區塊非前綴融合與 HKVD 選擇性重算** | 以「Messi 13 球 vs Ronaldo 8 球」直覺案例說明為何直接拼接會漏掉 cross-attention；介紹 Token 級 5–18%（預設 15%）HKVD 漸進過濾與逐層 I/O 管線化（TTFT 降 2.2–3.3×、吞吐升 2.8–5×）。 | 案例對比圖＋3 步驟流程卡＋關鍵 KPI 數字 | `cards/card-01-cacheblend.md` |
| 05 | **LMCache：讓 KV Cache 走出單張 GPU 的企業級基礎設施** | 揭露 16–64 KB 分頁小檔拖垮頻寬的真相（64 KB 僅 4 GB/s vs 16 MB 49 GB/s）；介紹 256-token Chunk 批次搬運（400 vs 88 Gbps）、雙層重疊與標準化 KV Connector / Controller API（吞吐最高 15×）。 | 頻寬長條圖對比＋分層架構示意 | `cards/card-03-lmcache.md` |
| 06 | **企業生產現場的兩個反直覺真相（LMCache 實戰教訓）** | (1) 高速遠端物件儲存載入比 Prefill 還快（降 22–32% TTFT），但 32 Gbps 低頻寬下有 256K tokens 交叉點；(2) 滑動視窗截斷（Context Truncation）讓前綴命中率從 ~85% 腰斬至 ~45%。 | 雙警報對照卡片＋交叉點摘要 | `cards/card-03-lmcache.md`, `cards/card-08-tensions.md` |
| 07 | **RelayCaching：化解多代理系統 $O(M^2)$ 級聯重複計算** | 說明 Architect→Developer→Reviewer 接力時的 prefix variation 問題；展示跨模型通用的 Value Cosine **U 型中層曲線**＋三合一雙準則 Token 選擇（偏差＋注意力影響＋尾端 10 tok），達成 >80% 重用、12K 長文 0.42 s（快 9.2×、次線性）。 | U 型曲線示意＋雙準則流程＋消融數字 | `cards/card-04-relaycaching.md` |
| 08 | **DroidSpeak：同底模微調模型間的連續層選擇性重算** | 直接全盤重用微調模型 KV 會掉 >50% F1，但其實平均僅 **11%** 為關鍵層；解釋 **E-Cache（2–4× KV 大小）**多次切換造成傳輸與誤差爆炸，因此設計單一切換點連續層重算與線上 SLO 動態調度（Prefill 降 1.7–2.6×、吞吐升 2–3×）。 | 散落切換 vs 單一連續區塊視覺對比 | `cards/card-02-droidspeak.md` |
| 09 | **Cross-Model KV Transfer：跨尺寸模型的閉式線性映射** | 連層數與參數量都不同還能重用？介紹同家族 Matched-KV 線性結構、無梯度閉式逐頭 Ridge（top-$k$ 源層＋500 條序列 47–87 分鐘擬合），4 組 Tier 1 保留 73–98%、32K 快 25×；2 組 Tier 2 失敗則由 MLP 救回 +24.3 至 +36.8 pp。 | 管線流程＋Tier 1 vs Tier 2/MLP 柱狀對比 | `cards/card-05-cross-model-kv.md` |
| 10 | **貫穿五篇的兩條隱藏主線：RoPE 對齊與偏差指標進化** | 左欄串聯 RoPE 三部曲（單次旋轉 → Pre-RoPE 接力 → 剝源／內容空間映射／重施目標 RoPE）；右欄揭示「誤差落點 > 誤差大小」：校準 $R_K^2$ 跨配對 $r = -0.20$ 失靈，Attention-Output Cosine 達 $r = +0.57$。 | 左右雙主線演進圖 | `cards/card-09-rope.md`, `cards/card-08-tensions.md`, `cards/card-05-cross-model-kv.md` |
| 11 | **別只看單篇結論！四大跨文獻張力與前提邊界** | 忠實並陳四組跨篇張力：(1) CacheBlend 在靜態 RAG 無損 vs 動態 MAS 掉點；(2) DroidSpeak 同架構重算 vs NVIDIA 跨尺寸映射；(3) 重建 $R^2$ vs 子空間保真度；(4) 遠端卸載頻寬交叉點與截斷反噬。 | 2×2 張力矩陣卡片 | `cards/card-08-tensions.md` |
| 12 | **實務選型指南與課程總結** | 依「單模型多區塊 / 企業卸載與 PD 分離 / 同質多代理 / 同底模微調 / 同家族跨尺寸」五種場景提供選型決策表，並以一句話總結 KV Cache 成為 AI-native 基礎設施的趨勢。 | 精簡五列決策表＋總結金句 | `cards/card-07-landscape.md`, `cards/card-10-overview.md` |
