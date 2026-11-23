# Slide 12：實務選型指南與課程總結

- **頁碼**：12 / 12
- **來源卡片**：`cards/card-07-landscape.md`, `cards/card-10-overview.md`
- **Wiki 出處**：`wiki/syntheses/kv-reuse-landscape.md`, `wiki/overview.md`

## 核心內容
- **五大應用場景選型決策表**：
  - **RAG 靜態多區塊拼接** → **CacheBlend**：Token 級 HKVD 重算（5–18%）＋管線化，TTFT 降 **2.2–3.3×** `[CacheBlend, §4.3, §7.2–7.3, p.6–7, 12]`。
  - **企業跨查詢卸載／PD 分離** → **LMCache**：256-token Chunk 搬運（400 Gbps）＋標準化 API，最高升 **15×** 吞吐 `[LMCache, Abstract, §5–8, Table 5, p.1, 6–14]`。
  - **同質多代理動態接力** → **RelayCaching**：U 型中層＋三合一稀疏修正，重用 **>80%**、12K 快 **9.2×** `[RelayCaching, §4–5, Table 1–2, Fig. 8, p.4–8]`。
  - **同底模微調模型共享** → **DroidSpeak**：單一切換點連續層重算＋帕累托動態調度，Prefill 降 **1.7–2.6×** `[DroidSpeak, §4.1–4.2, §5.2, p.6–7, 10]`。
  - **同家族跨尺寸路由／級聯** → **Cross-Model KV Transfer**：閉式 Ridge（Tier 2 換 MLP）＋RoPE 解耦，Tier 1 保留 **73–98%**、快 **2.7–25×** `[Cross-Model KV, §3–5, Table 1, 5, p.4–9]`。
- **一句話帶走**：KV Cache 正從「單次推論的 GPU 副產品」，演進為**跨查詢、跨節點、跨代理與跨模型的 AI-native 計算與儲存核心原語**。
- **頁尾出處**：`wiki/syntheses/kv-reuse-landscape.md`、`wiki/overview.md`｜`[5 篇綜合選型總結]`
