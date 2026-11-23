# [學校] [學號] [系級] [姓名] 用 LLM Wiki 與 Graph Workflow 打造 KV Cache Reuse 教學簡報

> *(繳交前請將上方標題方括號處改為你的「學校 學號 系級 姓名」)*

---

## 一、LLM Wiki 主題與簡短介紹

- **主題**：**KV Cache Reuse（大型語言模型 KV 快取重用技術）**
- **簡短介紹**：
  在長上下文 RAG、多輪對話、多代理協作（MAS）與多模型路由場景中，Prefill 階段的重複計算是延遲（TTFT／ITL）與算力成本的核心瓶頸。本專案以「**先討論、後生成**」模式，先請 AI 進行 9 題需求訪談並確認需求摘要後，才建立規則檔 `AGENTS.md`（3,231 字元，遠低於 12,000 字元上限，並附 `CLAUDE.md` 僅寫 `@AGENTS.md`、不建衝突的 `GEMINI.md`）與知識庫骨架，再依技術演進順序**一次一篇**增量 Ingest 以下 5 篇代表性論文（每篇獨立 `git commit`）：
  1. **CacheBlend**（`arXiv:2405.16444v3`，EuroSys '25）— RAG 多區塊非前綴融合與 HKVD 選擇性重算
  2. **DroidSpeak**（`arXiv:2411.02820v3`，2024／NSDI '26）— 同底模微調模型間的連續層選擇性重算共享
  3. **LMCache**（`arXiv:2510.09665v2`，2025）— 企業級分散式 KV Cache 層、卸載與 PD 分離
  4. **RelayCaching**（`arXiv:2603.13289v1`，2026）— 多代理系統 Decode-to-Prefill U 型中層與稀疏修正
  5. **Cross-Model KV Cache Transfer**（`arXiv:2608.03893v1`，NVIDIA，2026）— 同家族跨尺寸模型的閉式線性 Ridge 映射與 MLP 救援
- **建 Wiki 時特別考量的設計**：
  - **讀者雙軌定位**：`wiki/` 偏向研究深度（公式、架構與實驗數據），下游 HTML 簡報偏向直覺導讀（先講痛點與案例類比，再呈現核心機制與選型指南）。
  - **嚴格唯讀邊界與章節級出處**：`raw/` 搭配 `MANIFEST.sha256` 鎖定唯讀；所有 `wiki/` 頁面強制具備 YAML Frontmatter 與章節／圖表／頁碼級引用（例：`[CacheBlend, §7.2, Fig. 12, p.12]`）。
  - **跨文獻張力並陳**：當不同論文結論或前提出現落差（例如 CacheBlend 在靜態 RAG 近乎無損，但在 RelayCaching 動態多代理場景明顯掉點），統一以 `⚠️ 跨文獻張力／差異` 並陳雙方實驗條件，並集中彙整於 `wiki/syntheses/conflicts-and-tensions.md`。

---

## 二、成果連結

- **LLM Wiki 連結（GitHub Repository）**：https://github.com/QY-Zeng/GenAI_HW10
  - 規則檔與目錄入口：[AGENTS.md](https://github.com/QY-Zeng/GenAI_HW10/blob/main/AGENTS.md) ｜ [wiki/index.md](https://github.com/QY-Zeng/GenAI_HW10/blob/main/wiki/index.md) ｜ [wiki/overview.md](https://github.com/QY-Zeng/GenAI_HW10/blob/main/wiki/overview.md)
  - 跨文獻綜合：[kv-reuse-landscape.md](https://github.com/QY-Zeng/GenAI_HW10/blob/main/wiki/syntheses/kv-reuse-landscape.md) ｜ [conflicts-and-tensions.md](https://github.com/QY-Zeng/GenAI_HW10/blob/main/wiki/syntheses/conflicts-and-tensions.md)
  - 成果規模：共 **18 個 Markdown 頁面**（5 篇論文筆記 + 5 個核心概念 + 3 個系統／指標實體 + 2 篇跨文獻綜合 + `overview`/`index`/`log`），並保留完整漸進式 Git commit 紀錄。
- **教學型 HTML 簡報連結（GitHub Pages 線上瀏覽）**：https://qy-zeng.github.io/GenAI_HW10/topic-kv-cache-reuse/deck.html
  - （GitHub 原始碼位置：https://github.com/QY-Zeng/GenAI_HW10/blob/main/topic-kv-cache-reuse/deck.html ）
  - 共 **12 頁**，採「痛點直覺（Prefill vs Decode）→ 三軸演進全景 → 五大里程碑逐篇導讀 → RoPE 與誤差落點隱藏主線 → 四大跨文獻張力 → 五大場景實務選型」的教學結構；支援 `←`/`→`/`Space` 翻頁、`G` 鍵網格總覽、進度條與列印 PDF，每頁皆附對應 `wiki/` 與章節出處頁尾。

---

## 三、Graph（內含局部 Loop）Workflow 設計說明

本專案採用 **Graph 決定大流程與退回路線、Loop 負責單一節點內反覆修正** 的設計（完整規格見 [.agents/workflows/topic-slides.md](https://github.com/QY-Zeng/GenAI_HW10/blob/main/.agents/workflows/topic-slides.md)），所有中介狀態皆落地成檔案（`topic-kv-cache-reuse/`），每一道檢查關卡皆由可執行 Python 腳本或獨立唯讀子代理把關。

### 流程圖（純文字版，適用所有課程平台）
```text
[Node 1: 檢索 wiki -> sources.md]
          │
          ▼
[Node 2: 覆蓋率關卡 (gate1_check_coverage.py)] ──(不足 <3 頁或漏論文)──► 停下補資料
          │ PASS
          ▼
[Node 3: 平行產出證據卡 -> cards/ (嚴格單一來源隔離)]
          │
          ▼
[Node 4: 產出教學大綱 -> outline.md (8–15 頁)]
          │
          ▼
[Node 5: 人工確認關卡] ──(缺子題 -> 退回 Node 1) / (調架構 -> 退回 Node 4)
          │ 確認大綱
          ▼
[Node 6: 逐頁稿 -> drafts/ (僅看大綱+綁定卡片，內含小 Loop ≤2 輪)]
          │
          ▼
[Node 7: 忠實度檢查 (gate2_check_drafts.py + 獨立唯讀子代理)]
          ├──(卡片本身錯)──────────────► 退回 Node 3 重抽該張卡片
          ├──(單頁錯／越界)────────────► 退回 Node 6 只修出錯那一頁
          │ 12/12 PASS
          ▼
[Node 8: 渲染互動式 HTML -> deck.html (嚴禁改動事實與數字)]
          │
          ▼
[Node 9: 渲染與溢出檢查 (gate3_check_html.py + 無頭 Chrome 1280×720)]
          ├──(字太多導致溢出)──────────► 退回 Node 6 縮短逐頁稿
          ├──(HTML/CSS 或越權字詞)─────► 退回 Node 8 修正 (≤2 輪)
          │ 0px 溢出 PASS
          ▼
[Node 10: 交件報告 -> report.md + git commit]
```

### 1. 哪些步驟會重複執行？
- **Wiki 建置階段**：每匯入 1 篇新論文就重複執行「單篇 Ingest → 增量更新概念／實體／綜合頁 → 執行 `scripts/lint_wiki.py` → 獨立 `git commit`」。
- **簡報生成階段（局部小 Loop）**：Node 6（撰寫逐頁稿 → `gate2_check_drafts.py` 檢核出處、數字與字數 → 修正，最多 2 輪）、Node 7（獨立子代理退回單頁 → 只修該頁再複審）、Node 8–9（渲染 HTML → `gate3_check_html.py`＋無頭 Chrome 測溢出 → 修正再測，最多 2 輪）。

### 2. 哪些地方需要檢查或重新生成？
- **Node 2（`gate1_check_coverage.py`）**：驗證 `sources.md` 至少含 3 個有效 `wiki/` 頁、100% 不超出 `wiki/` 邊界、且涵蓋全部 5 篇論文；不足直接停下。
- **Node 5（人工確認關卡）**：在寫逐頁稿前先由人確認 `outline.md`，缺子題或順序不佳時立即退回 Node 1／Node 4，避免寫完全部頁面才大改。
- **Node 7（`gate2_check_drafts.py` ＋ 獨立唯讀子代理）**：腳本先檢查出處存在、數據皆可回溯至引用卡片、且每頁字數 ≤ 950 字；接著開啟**全新獨立唯讀子代理**（絕不自審自稿、不可修改檔案），只給 `drafts/` 與來源做忠實度與覆蓋率審查，不通過僅退回重修該頁。
- **Node 9（`gate3_check_html.py` ＋ `check_overflow_headless.py`）**：腳本核對頁數一致、頁尾出處完整、且 HTML 無越權新增逐頁稿未出現的數字；再以真實無頭 Chrome（`1280×720`）量測每頁水平／垂直溢出與頁尾重疊像素。

### 3. 為什麼這樣設計？
- **權限隔離防幻覺**：證據卡限看單篇、逐頁稿限看綁定卡片、HTML 渲染禁改事實文字、檢查關卡禁改檔案，讓每個節點責任單一且可驗證。
- **腳本說了算＋小圈快修、大圈少轉**：用可重跑腳本取代口頭「檢查一下」，並讓錯誤在離源頭最近的地方被抓到，減少整份重來的成本。

---

## 四、一次實際執行的結果與檢查紀錄

完整檢查報告見 [topic-kv-cache-reuse/report.md](https://github.com/QY-Zeng/GenAI_HW10/blob/main/topic-kv-cache-reuse/report.md) 與 [fidelity_review.md](https://github.com/QY-Zeng/GenAI_HW10/blob/main/topic-kv-cache-reuse/fidelity_review.md)：

1. **Wiki Lint（`python scripts/lint_wiki.py`）**：**9/9 PASS（0 錯誤、0 警告）** — `AGENTS.md` 3,231／12,000 字元、`raw/` 5 份來源 SHA-256 唯讀校驗通過、18 頁零斷鏈零孤島、5 處跨文獻張力全數集中對照。
2. **Gate 1 覆蓋率檢查（`gate1_check_coverage.py`）**：**PASS**（有效 `wiki/` 頁面 16 頁、5/5 論文全覆蓋）。
3. **Node 5 人工確認**：審閱 12 頁大綱與證據卡綁定後核准放行。
4. **Gate 2 ＋ 獨立唯讀子代理忠實度審查（真實攔截案例 1）**：
   - `gate2_check_drafts.py`：**PASS**（12 頁、0 錯誤、0 警告）。
   - **獨立子代理 Round 1 裁決：`FAIL`（精準抓出 2 頁退件 + 5 頁微調）**：
     - `slide-04.md`：寫入「Messi **世界盃**進 13 球」，但卡片與 Wiki 僅寫「Messi 進 13 球」，抓出外部常識溢漏。
     - `slide-09.md`：「**只要**屬同家族且 Matched-KV…竟具高度線性結構」過度概括充分條件（遺漏 `dense full-attention` 且與 Tier 2 失敗衝突），且 `278 ms vs 6,975 ms = 25×` 緊接在 Llama 3.1 後方未標明係屬 `Qwen3 14B→32B`。
   - **精準退回修訂**：保持其餘 5 頁 `PASS` 頁完全不動，只修受影響頁面 → 重跑 `gate2` 0 錯誤 → 獨立子代理 **Round 2 複審：`12/12 PASS`，零殘留缺陷**。
5. **Gate 3 ＋ 無頭 Chrome 版面實測（真實攔截案例 2）**：
   - **`gate3_check_html.py` Round 1 裁決：`FAIL`**：抓出 Slide 1 封面眉標美化時順手多寫了逐頁稿未出現的 `100%`（`Slide 1: Metric '100%' in HTML is NOT present in approved draft slide-01.md`）。修正眉標後 Round 2 **0 錯誤 PASS**。
   - **無頭 Chrome `1280×720` 實測（`check_overflow_headless.py`）**：全部 12 頁實測皆為 **`hOverflow=0px, wOverflow=0px, footerOverlap=0px [PASS]`**。

---

## 五、反思

### 1. 哪一個節點最常出錯？
實測發現，**Node 6「逐頁稿撰寫」與 Node 8「HTML 渲染」的邊界最容易出錯**，且多屬「表面看來很合理、實則隱性越界」的錯誤：
- 在 Node 6 將研究筆記改寫成白話教學稿時，AI 容易不自覺帶入訓練記憶中的額外字詞（如 `slide-04` 多寫了卡片沒寫的「世界盃」），或在精簡字數時省掉模型前提與數據歸屬（如 `slide-09` 的 `dense full-attention` 與 `Qwen3 14B→32B`）。
- 在 Node 8 進行視覺排版時，AI 為了美化封面眉標而順手加入逐頁稿沒有的 `100%`，違反「排版節點不可更動事實與數字」的邊界。

### 2. 發現問題後，把檢查往前移到了哪一個步驟？
- **把「防版面溢出」從 Node 9 往前移到 Node 6/7**：在 `gate2_check_drafts.py` 就先加入單頁字數密度上限（≤ 950 字），結果最後進到 Node 9 無頭 Chrome 實測時 12 頁一次就達成全部 `0px` 溢出，完全避免了「做到最後一關才整份大修」的大圈退回。
- **把「適用前提與數據歸屬」從 Node 7 往前移到 Node 3（證據卡）**：原本要靠 Node 7 獨立子代理事後抓出 `slide-09` 的過度概括與模型混淆；檢討後把該檢核前置到 Node 3 證據卡規範——在抽卡階段就強制把「適用前提／限制」與「每項數字綁定的模型與基準」分開寫清，從源頭堵住下游寫歪的機會。

### 3. 有沒有因此修改 workflow / graph？為什麼？
**有，做了兩項具體修改並以 Git 紀錄留存（commit `89ffdab`）**：
1. **更新 `.agents/workflows/topic-slides.md` 的 Node 3 證據卡規則**：新增強制欄位要求（「每張卡須明列適用前提／限制與每項數據綁定之模型／基準」），把品質把關再往前移一關。
2. **將 Node 9 的瀏覽器溢出檢查正式腳本化**：新增可重複執行的 `scripts/check_overflow_headless.py` 與 `deck.html?audit=1` 檢測鉤子，搭配 `gate3_check_html.py` 的禁止新增未授權數字規則，真正落實「說檢查一下不算驗證，腳本說了算」。
