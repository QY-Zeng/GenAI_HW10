---
name: s5-anthropic-prompt-caching
description: Anthropic 官方 prompt caching 文件（取得日 2026-11-15）：prefix 順序、TTL、價格倍率、最小長度、失效條件與用量欄位
sources: [S5]
---

# S5 — Anthropic Claude Platform Docs: Prompt caching

- 位置：`platform.claude.com/docs/en/build-with-claude/prompt-caching`
- 取得方式：WebFetch 全文（2026-11-15）
- 驗證狀態：**一手（廠商官方）、全文已讀；內容會隨時間改變**，引用價格與限制時必須註明「以官方文件為準」

## 重點（claim）
- [C19] API 的 prompt caching 讓請求從「prompt 的某個 prefix」繼續處理；快取的是到 `cache_control` 指定 block 為止的**完整 prefix**，順序為 tools → system → messages。 [S5 How prompt caching works]
- [C20] 預設快取壽命 5 分鐘，每次命中免費刷新；可選 1 小時壽命。壽命從寫入或讀取該快取的請求「開始」時起算。 [S5]
- [C21] 價格倍率：5 分鐘寫入為基本輸入價的 1.25×、1 小時寫入 2×、讀取一般為 0.1×；部分模型的讀取倍率更低（文件列出 0.05×、0.025× 的例外）。 [S5 Pricing]
- [C22] 最小可快取長度依模型而異，文件列出 512 到 4,096 tokens；prompt 太短會「不快取、也不報錯」；可用回應 usage 中的 `cache_creation_input_tokens` 與 `cache_read_input_tokens` 判斷是否命中。 [S5 Cache limitations、Tracking cache performance]
- [C23] 命中需要 prefix 100% 相同；改動 tool 定義會讓整個快取失效；`tool_choice` 或圖片的增減會讓 messages 部分失效；最多 4 個明確 breakpoint；breakpoint 應放在「各請求之間最後一個不變的 block」，若放在含時間戳或使用者輸入的 block，每次都會寫入新項目而從不命中。 [S5 What invalidates the cache、Structuring your prompt]
- [C24] 快取不影響輸出：回應與不使用快取時相同。 [S5 Cache storage and sharing]
- 隔離與資料處理：快取以 workspace（部分平台為 organization）隔離；KV cache 表示與雜湊只存在記憶體中，不寫入磁碟。 [S5 Data retention]（此條未進帳本，簡報未使用）

## 使用時要小心
- 搜尋結果中的舊版文件鏡像與第三方轉載頁，顯示的是舊模型清單、固定 0.1× 讀取價與 1,024/2,048 tokens 最小長度；與官方現行頁面不同。見 `lint/conflicts.md` L5。
- 文件描述的是 API 行為，**並未揭露底層如何實作**；不可據此推論 Anthropic 內部使用 RadixAttention 或 PagedAttention。
