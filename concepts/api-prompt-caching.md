---
name: api-prompt-caching
description: 商用 API 的 prompt caching（以 Anthropic 官方文件為例）：怎麼命中、壽命、價格倍率、最小長度、什麼會讓快取失效
sources: [S5]
---

# API 的 prompt caching（Anthropic 文件，2026-11-15 取得）

> 這是 API 的「功能」，不是某篇論文的系統。價格與限制會變，一律以官方文件為準。

## 怎麼運作
- [C19] 快取到 `cache_control` 指定 block 為止的完整 prefix，順序為 tools → system → messages。 [S5]
- [C20] 預設壽命 5 分鐘，每次命中免費刷新；可選 1 小時。 [S5]
- [C24] 快取不影響輸出，回應與不使用時相同。 [S5]

## 錢怎麼算
- [C21] 5 分鐘寫入 1.25×、1 小時寫入 2×、讀取一般 0.1×（部分模型更低，文件列出 0.05×、0.025× 的例外）。 [S5]

## 什麼時候不會命中
- [C22] prompt 短於該模型的最小長度（512 到 4,096 tokens，依模型而異）就不快取，也不會報錯；用 `cache_creation_input_tokens` 與 `cache_read_input_tokens` 判斷是否命中。 [S5]
- [C23] 需要 prefix 100% 相同；改 tool 定義讓整個快取失效；`tool_choice` 或圖片增減讓 messages 部分失效；breakpoint 要放在最後一個穩定的 block，放在含時間戳的 block 上永遠不會命中；最多 4 個明確 breakpoint。 [S5]

## 實務檢查清單（解說，整理自上列 claim）
1. 把不會變的內容（tool 定義、系統指示、長文件）放在 prompt 最前面。
2. 把會變的內容（時間戳、使用者問題）放在最後，並把 breakpoint 放在變動內容之前。
3. 看 usage 欄位確認有沒有命中，不要假設。
4. 請求間隔可能超過 5 分鐘時，評估 1 小時壽命。
