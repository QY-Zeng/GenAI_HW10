# Node 10 交件總報告：KV Cache Reuse 教學簡報 (`report.md`)

- **成品位置**：`topic-kv-cache-reuse/deck.html`（獨立單檔互動式 HTML，支援 `←`/`→`/`Space` 翻頁、`G` 鍵網格總覽、進度條與列印輸出 PDF）
- **簡報主題**：KV Cache Reuse：從單模型前綴快取到多代理與跨模型重用
- **總頁數**：12 頁（符合 8–15 頁規範）
- **知識邊界**：100% 僅使用 `wiki/` 內 16 個已驗證頁面（涵蓋全部 5 篇論文與 4 大跨文獻張力）

---

## 一、全流程 10 關 Graph Workflow 驗收紀錄

| 關卡 | 類型 | 執行命令／工具 | 結果 | 退回與修正紀錄 |
| --- | --- | --- | --- | --- |
| Wiki 品質前置 | 腳本 | `python scripts/lint_wiki.py` | **PASS (9/9, 0 錯)** | 5 篇論文逐篇 Ingest＋5 次獨立 commit，`raw/` SHA-256 唯讀校驗全過 |
| Node 1 檢索 Wiki | AI 節點 | 產出 `sources.md` | **PASS** | 檢索 16 頁（5 論文 + 5 概念 + 3 實體 + 2 綜合 + overview） |
| Node 2 覆蓋率關卡 | 腳本 | `python scripts/gate1_check_coverage.py topic-kv-cache-reuse` | **PASS** | 16 頁有效 `wiki/` 頁面、5/5 論文全覆蓋、零外部邊界違規 |
| Node 3 證據卡（平行） | AI 節點 | 平行產出 `cards/card-01`～`card-10` | **PASS** | 嚴格單一來源隔離（每卡僅讀對應 1 份 `wiki/` 頁面） |
| Node 4 大綱 | AI 節點 | 產出 `outline.md`（12 頁） | **PASS** | 每頁明確綁定對應證據卡 |
| Node 5 **人工確認** | **人工關卡** | 使用者審閱 `outline.md` | **APPROVED** | 使用者確認 12 頁大綱無誤後進入後半段 |
| Node 6 逐頁稿 | AI 節點 | 產出 `drafts/slide-01.md`～`slide-12.md` | **PASS** | 每頁僅看大綱＋綁定卡片，密度皆低於 950 字上限 |
| Node 7 忠實度檢查 | 腳本＋**獨立子代理** | `gate2_check_drafts.py` + `Independent Fidelity Reviewer`（唯讀新對話） | **Round 1 FAIL → Round 2 PASS (12/12)** | **真實退回案例 1**：獨立子代理抓出 `slide-04` 引入卡片外字詞「世界盃」、`slide-09` 過度概括充分條件且 `278 ms / 25×` 未標明屬 `Qwen3 14B→32B` → 依退回路線只修受影響頁，其餘 5 頁 `PASS` 頁不動 → Round 2 全部 12/12 `PASS` |
| Node 8 渲染 HTML | AI 節點 | 產出 `deck.html`（含內嵌 SVG 圖表與鍵盤導覽） | **PASS** | 忠實呈現已通過之逐頁稿 |
| Node 9 渲染與溢出檢查 | 腳本＋無頭 Chrome | `gate3_check_html.py` + `check_overflow_headless.py` (`1280×720`) | **Round 1 FAIL → Round 2 PASS (12/12)** | **真實退回案例 2**：`gate3_check_html.py` 抓出 Slide 1 眉標多寫了逐頁稿未出現的 `100%` → 立刻修正為文字敘述 → 重跑 Gate 3 0 錯誤，且真實 Chrome 渲染全部 12 頁皆 **`hOverflow=0px, wOverflow=0px, footerOverlap=0px`** |
| Node 10 交件 | 彙整＋版控 | 產出 `report.md` 並更新 `wiki/log.md` 與 `git commit` | **DONE** | 完整狀態檔案與腳本皆納入 Git 追蹤 |

---

## 二、無頭 Chrome（1280×720）版面溢出實測結果
```text
Slide 01: hOverflow=0px, wOverflow=0px, footerOverlap=0px [PASS]
Slide 02: hOverflow=0px, wOverflow=0px, footerOverlap=0px [PASS]
Slide 03: hOverflow=0px, wOverflow=0px, footerOverlap=0px [PASS]
Slide 04: hOverflow=0px, wOverflow=0px, footerOverlap=0px [PASS]
Slide 05: hOverflow=0px, wOverflow=0px, footerOverlap=0px [PASS]
Slide 06: hOverflow=0px, wOverflow=0px, footerOverlap=0px [PASS]
Slide 07: hOverflow=0px, wOverflow=0px, footerOverlap=0px [PASS]
Slide 08: hOverflow=0px, wOverflow=0px, footerOverlap=0px [PASS]
Slide 09: hOverflow=0px, wOverflow=0px, footerOverlap=0px [PASS]
Slide 10: hOverflow=0px, wOverflow=0px, footerOverlap=0px [PASS]
Slide 11: hOverflow=0px, wOverflow=0px, footerOverlap=0px [PASS]
Slide 12: hOverflow=0px, wOverflow=0px, footerOverlap=0px [PASS]
[PASS] All 12 slides verified with 0px overflow and 0px footer overlap at 1280x720.
```

---

## 三、課堂作業反思參考素材（對應課程簡報第 52 頁）
1. **建 Wiki 時特別考量的事情**：
   - 先做 9 題需求訪談並確認摘要後才建檔，將規則濃縮在 `AGENTS.md`（3,231 字元，遠低於 12,000 字元上限），並以 `CLAUDE.md`（`@AGENTS.md`）兼顧跨工具共用、不建衝突的 `GEMINI.md`。
   - 用 `raw/MANIFEST.sha256` 程式化鎖死唯讀邊界，並強制「章節／圖表級出處」與「跨文獻張力並陳（`conflicts-and-tensions.md`）」，避免綜合多篇論文時把不同前提的實驗結論混為一談。
   - 依技術演進順序「一次一篇」增量 Ingest 並獨立 `git commit`，每步皆以 `lint_wiki.py` 把關。
2. **Graph Workflow 設計心得**：
   - 將狀態全部檔案化（`sources.md` → `cards/` → `outline.md` → `drafts/` → `fidelity_review.md` → `deck.html` → `report.md`），每一道檢查關卡對應一支可執行腳本（`gate1`～`gate3` + `check_overflow_headless.py`），把「說檢查一下不算驗證」落實為可重跑的客觀門檻。
   - 嚴格實踐「**不自審自稿**」與「**錯在哪關退回哪關**」：本次實測中，獨立唯讀子代理確實抓出一般自審極易漏掉的卡片邊界溢漏（Slide 4「世界盃」）與模型歸屬歧義（Slide 9），而 `gate3_check_html.py` 也在渲染階段抓出未經授權新增的數字（Slide 1「100%」），真實證明了 Graph＋腳本關卡的實戰價值。
