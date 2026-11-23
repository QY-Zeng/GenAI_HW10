---
description: "Graph 版教學簡報 Workflow Prototype（10 關節點、嚴格權限隔離、可執行腳本關卡與精準退回路線）"
---

# `/topic-slides` — Graph 版教學簡報 Workflow Prototype

本 Workflow 依據課程第 10 單元《把你的工作拆成 AI 能做的流程》第 43–47 頁設計：**Graph 決定大流程與退回路線，Loop 負責單一節點內的反覆修正，每一關狀態皆落地成檔案，每一道檢查關卡皆由腳本或獨立審查者把關**。

## 狀態檔案結構 (`topic-<slug>/`)
```text
topic-<slug>/
├── sources.md          # Node 1: 從 wiki/ 檢索出的主題相關頁面清單
├── cards/              # Node 3: 平行產出之單一來源證據卡（嚴禁混入外部來源）
├── outline.md          # Node 4: 8–15 頁教學簡報大綱（Node 5 人工確認對象）
├── drafts/             # Node 6: 逐頁稿（slide-01.md ~ slide-NN.md）
├── fidelity_review.md  # Node 7: 獨立新對話／子代理之忠實度與覆蓋率審查報告
├── deck.html           # Node 8: 最終互動式 HTML 教學簡報
└── report.md           # Node 10: 交件總報告（附全部關卡腳本輸出與審查結果）
```

## 10 關節點、權限隔離與退回路線

| 關卡 | 類型 | 只能看（輸入邊界） | 不能做（禁止行為） | 產出／驗證方式 | 不通過時退回目標 |
| --- | --- | --- | --- | --- | --- |
| 1. 檢索 Wiki | AI 節點 | `wiki/index.md`、`wiki/**/*.md` | 禁止讀取外部網路或未收錄文獻 | `sources.md` | — |
| 2. 覆蓋率關卡 | 檢查腳本 | `sources.md`、`wiki/` | 不可自行修改檔案 | `python scripts/gate1_check_coverage.py <topic_dir>`（相關頁 ≥ 3 且覆蓋核心面向） | **不足 → 立刻停下**並告知缺少哪些資料 |
| 3. 證據卡（平行） | AI 節點（平行） | **單一**指定 `wiki/` 來源頁 | **嚴禁混入其他論文或來源** | `cards/<source>.md` | 卡片錯誤 → 僅重抽該篇證據卡 |
| 4. 大綱 | AI 節點 | `sources.md` + `cards/*.md` | 不可編造卡片以外的論點或數據 | `outline.md`（8–15 頁） | — |
| 5. **人工確認** | **人工關卡** | `outline.md` | AI 必須暫停等待使用者審閱 | 使用者核准大綱 | 缺子題 → 退回 **Node 1 補檢索**；結構需調整 → 退回 **Node 4 修大綱** |
| 6. 逐頁稿 | AI 節點（內含小 Loop ≤ 2 輪） | `outline.md` + **該頁對應證據卡** | **嚴禁引用卡片以外內容**；單頁字數不超標 | `drafts/slide-01.md`..`NN.md` | 內迴圈自檢出處與字數（最多 2 輪） |
| 7. 忠實度檢查 | 腳本 + **獨立子代理** | `drafts/` + `cards/` + `wiki/` | **不可自己改稿**；AI 審查必須開啟獨立新對話／子代理，不自審自稿 | `python scripts/gate2_check_drafts.py <topic_dir>` + 獨立子代理產出 `fidelity_review.md` | **只退回重修出錯的那一頁**（其餘頁不動）；若卡片錯則退回 **Node 3** |
| 8. 渲染 HTML | AI 節點 | 已通過之 `drafts/` | **嚴禁私自更動逐頁稿事實文字與數字** | `deck.html`（16:9 教學投影片＋鍵盤導覽＋視覺圖表） | — |
| 9. 渲染與溢出檢查 | 腳本 + 渲染驗證 | `deck.html` + `drafts/` | 不可自己改文字硬塞版面 | `python scripts/gate3_check_html.py <topic_dir>` + 實際瀏覽器溢出檢查 | 版面溢出／字太多 → **退回 Node 6 縮短逐頁稿**（非硬縮小字體）；CSS 排版問題 → 退回 **Node 8**（最多 2 輪） |
| 10. 交件 | AI 節點 | 所有關卡輸出與 `deck.html` | 不可隱瞞未通過的警告 | `report.md` + `git commit` | — |
