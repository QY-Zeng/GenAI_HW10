# Slide 03：五篇論文如何突圍？三軸演進全景圖

- **頁碼**：03 / 12
- **來源卡片**：`cards/card-07-landscape.md`, `cards/card-10-overview.md`
- **Wiki 出處**：`wiki/syntheses/kv-reuse-landscape.md`, `wiki/overview.md`

## 核心內容
- **軸一｜空間與系統軸（GPU 存不下、跨機怎麼搬？）**：
  - **LMCache（2025）**：Chunk 批次搬運（**400 Gbps**）、計算–I/O 管線化與標準化 API，打通 CPU／SSD／遠端儲存與 PD 分離，最高提升 **15×** 吞吐 `[LMCache, Abstract, §5–8, Table 5, p.1, 6–14]`。
- **軸二｜語境與位置軸（前綴變了怎麼辦？）**：
  - **CacheBlend（EuroSys '25）**：RAG 靜態多區塊非前綴融合，重算 **5–18%** HKVD tokens，TTFT 降 **2.2–3.3×** `[CacheBlend, §4.3, §7.2–7.3, p.6–7, 12]`。
  - **RelayCaching（2026）**：多代理動態 Decode-to-Prefill 接力，U 型中層＋稀疏修正，重用 **>80%**、12K 長文快 **9.2×** `[RelayCaching, §4–5, Table 1–2, Fig. 8, p.4–8]`。
- **軸三｜模型邊界軸（換了模型還能重用嗎？）**：
  - **DroidSpeak（2024／NSDI '26）**：同底模同架構微調變體，單一切換點連續層重算，Prefill 降 **1.7–2.6×** `[DroidSpeak, §4.1–4.2, §5.2, p.6–7, 10]`。
  - **Cross-Model KV Transfer（2026）**：同家族跨尺寸 matched-KV 閉式線性映射，Tier 1 保留 **73–98%** 精度、快 **2.7–25×** `[Cross-Model KV, §3–4, Table 1, 5, p.4–9]`。
- **頁尾出處**：`wiki/syntheses/kv-reuse-landscape.md`、`wiki/overview.md`｜`[5 篇綜合對照]`
