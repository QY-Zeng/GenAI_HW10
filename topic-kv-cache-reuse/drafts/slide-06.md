# Slide 06：企業生產現場的兩個反直覺真相（LMCache 實戰教訓）

- **頁碼**：06 / 12
- **來源卡片**：`cards/card-03-lmcache.md`, `cards/card-08-tensions.md`
- **Wiki 出處**：`wiki/papers/lmcache.md`, `wiki/syntheses/conflicts-and-tensions.md`

## 核心內容
- **真相一：高速遠端物件儲存竟然比重新 Prefill 快——但存在頻寬交叉點！**
  - 現代物件儲存（如 S3 Express）讓 Company C 直接從遠端載入 KV 反而比完整 Prefill 降低 **22–32% TTFT** `[LMCache, §9, p.15]`。
  - **前提邊界**：B200 敏感度實驗顯示，若網路頻寬僅 **32 Gbps**，唯有輸入超過 **256K tokens** 載入才勝過重算；達 **64–128 Gbps** 才全序列長度皆勝出 → 系統必須做**自適應載入決策** `[LMCache, §8.7, Fig. 15, p.14–15]`。
- **真相二：為了省記憶體截斷對話開頭，反讓快取命中率直接腰斬！**
  - 工業界常見滑動視窗 **Context Truncation**（僅保留最新 tokens）會破壞前綴雜湊匹配。
  - Company F 真實流量顯示：截斷後前綴快取命中率從 **~85%** 暴跌至 **~45%**；實務上應盡量採 append-only 上下文管理 `[LMCache, §9, p.15]`。
- **企業真實流量回放效益（Company F & G）**：導入 LMCache 後高 QPS 下 TTFT 降 **3.7–6.8×**、ITL 降 **19%–58%** `[LMCache, §8.3, Fig. 9–10, p.12]`。
- **頁尾出處**：`wiki/papers/lmcache.md`、`wiki/syntheses/conflicts-and-tensions.md`｜`[LMCache, §8.3, §8.7, §9, Fig. 9–10, 15, p.12, 14–15]`
