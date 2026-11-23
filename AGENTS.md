# AGENTS.md — KV Cache Reuse LLM Wiki 員工手冊

本專案是基於 Karpathy LLM Wiki 構想建立的 **KV Cache Reuse（KV 快取重用）** 研究與教學知識庫，同時支援以 Graph Workflow 從 Wiki 產出互動式 HTML 教學簡報。

## 1. 核心定位與讀者
- **主題**：KV Cache Reuse（涵蓋 RAG 多區塊融合、同底模微調跨模型共享、企業級分散式快取卸載與 PD 分離、多代理 Decode-to-Prefill 重用、跨尺寸閉式線性映射）。
- **目標讀者（兩者兼顧）**：
  - `wiki/`：偏**研究深度**，詳實紀錄演算法、公式、架構設計、實驗設定與量化結果。
  - 教學簡報（`topic-*/deck.html`）：偏**直覺易懂的導讀**，先講痛點與直覺類比，再呈現核心機制與精準數據。
- **撰寫語言**：**繁體中文為主**，專有名詞、系統名稱、資料集與效能指標保留英文（如 `KV Cache`、`Prefill`、`TTFT`、`ITL`、`Goodput`、`RoPE`、`HKVD`、`PD Disaggregation`、`GQA`）。

## 2. 嚴格資料邊界與目錄結構
- `raw/`：**唯讀事實來源區**。存放 5 篇論文原文與 `MANIFEST.sha256` 雜湊清單。**絕對禁止修改或覆寫 `raw/` 內容**。
- `wiki/`：由 Agent 維護的結構化知識庫（單向事實防線：`raw/ → wiki/`）：
  - `wiki/overview.md`：領域全景總覽與技術演進脈絡。
  - `wiki/index.md`：所有 Wiki 頁面的分類索引與一行摘要。
  - `wiki/log.md`：按時間排序的 Ingest、Lint 與 Workflow 操作日誌。
  - `wiki/papers/`：單篇論文深入筆記（1 篇 1 檔）。
  - `wiki/concepts/`：跨論文核心技術概念（如選擇性重算、RoPE 位置對齊、計算與 I/O 管線化、偏差衡量指標）。
  - `wiki/entities/`：關鍵系統、推理引擎與評估指標（如 vLLM & SGLang、LMCache、PagedAttention、TTFT/ITL/Goodput）。
  - `wiki/syntheses/`：跨論文比較矩陣、場景對照與**跨文獻張力／差異集中分析**。
- `scripts/`：可執行的驗證腳本（**「做完了」不是 AI 說了算，是腳本說了算**）。
- `.agents/workflows/`：簡報生成 Graph Workflow 定義檔（複雜流程細節拆至本目錄，保持本手冊精簡於 12,000 字元內）。
- `topic-<slug>/`：簡報 Graph Workflow 的狀態檔案與成品（`sources.md`、`cards/`、`outline.md`、`drafts/`、`deck.html`、`report.md`）。

## 3. 頁面格式與引用出處規範
1. **標準 YAML Frontmatter**：所有 `wiki/` Markdown 檔案皆須包含：
   ```yaml
   ---
   title: "<頁面標題>"
   type: "paper | concept | entity | synthesis | overview | index | log"
   sources:
     - "raw/<source-file>.md"
   updated: "YYYY-MM-DD"
   ---
   ```
2. **章節與圖表級出處（強制）**：
   - 所有關鍵論點、機制與實驗數據，皆須標註到「論文縮寫＋章節／圖表編號＋頁碼」，例如：`[CacheBlend, §7.2, Fig. 12, p.12]`、`[Cross-Model KV, Table 1, p.6]`。
   - 每篇 `wiki/papers/` 筆記必須明確連結對應的 `raw/` 檔案；概念頁、實體頁與綜合頁必須雙向連結對應的 `wiki/papers/` 頁面，避免孤島頁面。
   - **禁止捏造或補齊論文未記載的數據**；若來源不足或未報告，明確標註「來源未記載」。

## 4. 跨論文矛盾與張力處理規則
- 當不同論文在結論、假設、偏差指標或實驗結果上出現矛盾或落差時，**嚴禁強行選邊站或隱藏差異**。
- 必須在相關頁面使用統一標記區塊：
  ```markdown
  > [!WARNING] ⚠️ 跨文獻張力／差異
  > - **主張 A**：...（含實驗條件與出處）
  > - **主張 B**：...（含實驗條件與出處）
  > - **差異根因**：...
  ```
- 所有張力條目皆須同步收錄並交叉連結至 `wiki/syntheses/conflicts-and-tensions.md`。

## 5. Ingest 流程與 Git 版本控制規範
- 採用**一次一篇、逐篇增量更新**策略，依技術演進順序匯入：`CacheBlend → DroidSpeak → LMCache → RelayCaching → Cross-Model KV Transfer`。
- 每完成 1 篇論文 Ingest，必須完成以下步驟後立刻 `git commit`：
  1. 建立 `wiki/papers/<slug>.md`。
  2. 增量建立或更新相關的 `wiki/concepts/`、`wiki/entities/`、`wiki/syntheses/` 與 `wiki/overview.md`。
  3. 更新 `wiki/index.md` 與 `wiki/log.md`。
  4. 執行 `python scripts/lint_wiki.py` 確認無誤（或記錄待跨篇補齊項目）並提交清晰的 commit message（例：`ingest: add CacheBlend (EuroSys 25)`）。

## 6. 自動化 Lint 與品質把關
- 每次修改 `wiki/` 後皆須執行 `python scripts/lint_wiki.py`，全數項目 PASS 才算完成：
  1. `AGENTS.md` ≤ 12,000 字元、不存在衝突的 `GEMINI.md`、`CLAUDE.md` 正確指向 `@AGENTS.md`。
  2. `raw/` 檔案符合 `MANIFEST.sha256` 唯讀校驗。
  3. 所有 `wiki/` 頁面具合法 Frontmatter 與章節／圖表級出處。
  4. 零斷鏈、零孤島頁面、`index.md` 與 `log.md` 完全同步。
  5. 所有 `⚠️ 跨文獻張力／差異` 皆於 `wiki/syntheses/conflicts-and-tensions.md` 集中對照。

## 7. 下游產出（教學簡報 Graph Workflow）
- 產出 HTML 教學簡報時，**只允許使用 `wiki/` 內已驗證的內容**，不得擅自引入外部未收錄文獻或補腦數字。
- 完整 10 關 Graph 流程、每關權限邊界（只能看什麼／不能做什麼）、檢查腳本與退回路線，詳見 `.agents/workflows/topic-slides.md`。
- AI 忠實度審查**不得由撰寫逐頁稿的同一對話自我審查**，必須開啟獨立新對話／子代理，僅提供成品與來源進行核對。
