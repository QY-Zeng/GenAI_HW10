# 證據卡 07：五篇論文三軸演進與全景對照

- **唯一來源頁**：`wiki/syntheses/kv-reuse-landscape.md`（嚴禁混入其他來源）
- **三軸演進框架**：
  1. **空間與系統軸（怎麼存、怎麼搬？）**：vLLM／SGLang 單機 GPU 前綴快取 → LMCache 256-token Chunk 批次搬運（400 Gbps）、雙層管線化與標準化 API，打通 CPU／SSD／遠端儲存與 PD 分離 `[LMCache, Abstract, §5–8, Table 5, p.1, 6–14]`。
  2. **語境與位置軸（前綴變了怎麼辦？）**：嚴格前綴 → CacheBlend 靜態 RAG 非前綴（Token 級 HKVD 5–18%，TTFT 降 2.2–3.3×）→ RelayCaching 多代理動態接力（U 型中層＋Value Cosine＋影響力＋尾端 10 tok，重用 >80%、12K 快 9.2×）`[CacheBlend, §4.3, §7.2–7.3, p.6–7, 12; RelayCaching, §4–5, Table 1–2, Fig. 8, p.4–8]`。
  3. **模型邊界軸（換了模型還能重用嗎？）**：單模型 → DroidSpeak 同底模同架構（連續層重算＋單次 E-cache，Prefill 降 1.7–2.6×）→ Cross-Model KV Transfer 同家族跨尺寸 matched-KV（無梯度閉式 Ridge＋RoPE 解耦，保留 73–98%、快 2.7–25×）`[DroidSpeak, §4.1–4.2, §5.2–5.3, p.6–7, 10; Cross-Model KV, §3–5, Table 1, 5, p.4–9]`。
