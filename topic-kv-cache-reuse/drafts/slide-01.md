# Slide 01：KV Cache Reuse：打破 LLM 重複閱讀的算力枷鎖

- **頁碼**：01 / 12（封面頁）
- **來源卡片**：`cards/card-10-overview.md`
- **Wiki 出處**：`wiki/overview.md`

## 核心內容
- **主標**：KV Cache Reuse：從單模型前綴快取到多代理與跨模型重用
- **副標**：五篇代表性論文的技術演進、系統實戰與跨文獻張力導讀
- **問題鉤子**：在 RAG、多代理協作與多模型路由中，同一段長上下文為何每換一次位置或模型，就得重算一次昂貴的 Prefill？
- **五大里程碑預告**：
  1. **CacheBlend（EuroSys '25）**：打破「嚴格前綴」限制
  2. **LMCache（2025）**：打破「單張 GPU 記憶體」限制
  3. **RelayCaching（2026）**：打破「靜態預計算」限制
  4. **DroidSpeak（2024／NSDI '26）**：打破「單一權重」限制
  5. **Cross-Model KV Transfer（2026）**：打破「相同模型尺寸」限制
- **頁尾出處**：`wiki/overview.md`｜`[CacheBlend, §4–7; DroidSpeak, §3–5; LMCache, §5–8; RelayCaching, §3–5; Cross-Model KV, §2–4]`
