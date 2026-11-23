---
title: "LMCache 系統架構與標準化介面"
type: "entity"
sources:
  - "raw/03-lmcache-2510.09665v2.md"
  - "raw/01-cacheblend-2405.16444v3.md"
  - "raw/02-droidspeak-2411.02820v3.md"
updated: "2026-11-23"
---

# LMCache（企業級分散式 KV Cache 層）

**LMCache** 是由 University of Chicago 與 Tensormesh Inc. 團隊開發的開源分散式 KV Cache 層，定位於「LLM 推理引擎（[vLLM 與 SGLang](./vllm-and-sglang.md)）」與「異質儲存／網路裝置（CPU DRAM、本地 SSD、遠端磁碟、Redis、S3、Mooncake、InfiniStore、NFS、WEKA、Valkey 等）」之間的標準化高效能中介層 `[LMCache, §1, §4, §9, Fig. 5, p.1–2, 5, 16]`。

## 1. 與既有研究的承繼關係
- [CacheBlend](../papers/cacheblend.md) 的非前綴 RAG 融合實作已開源整合至 `LMCache/LMCache` 倉庫 `[CacheBlend, Abstract, p.1]`。
- [DroidSpeak](../papers/droidspeak.md) 直接基於 LMCache 0.1.3 實作跨模型 `store_kv`/`fetch_kv` 介面 `[DroidSpeak, §4.5, p.8]`。
- [LMCache 論文](../papers/lmcache.md) 進一步將其演進為支援企業級萬億 token 規模、可跨節點與多引擎運作的生產系統 `[LMCache, §10, p.16]`。

## 2. 兩大標準化介面
1. **KV Connector API（引擎解耦介面）**：依 vLLM 的 Scheduler / Model Runner 分離哲學分為兩組函式 `[LMCache, §6, Table 2, p.8–9]`：
   - **Scheduler 側**：`get_num_new_matched_tokens`（可回傳 `None` 延後排程以重疊 I/O 與其他請求計算）、`update_state_after_alloc`、`build_connector_meta`。
   - **Model Runner 側**：`start_load_kv`、`wait_load_kv`、`start_store_kv`、`wait_store_kv`（同時支援整批搬運與逐層管線化）。
2. **Cache Controller API（全域調度介面）**：由集中式 Controller Manager 與各節點 Worker 構成 `[LMCache, §7, Table 3, p.9–10]`：
   - 內部回報：`batched_admit` / `batched_evict`、`batched_p2p_lookup`。
   - 外部控制：`lookup(tokens)`（支援 KV-aware 路由）、`move(...)`（縮容／負載平衡遷移）、`clear(...)`、`pin/unpin(...)`（固定高頻文件）、`compress/decompress(...)`。

## 3. 生態系採用與產業－學界取捨
- KV Connector API 已於 vLLM 上線超過 6 個月，獲 NVIDIA Dynamo、RedHat llm-d、ByteDance AIBrix、vLLM Production Stack 與 KServe 採用 `[LMCache, §3.2, §6, p.5, 9]`。
- 團隊亦坦承「產業重視穩定卸載與相容性、學界重視修改注意力機制（如 token dropping）」之間存在介面設計優先序張力，後續將擴充對研究原型更友善的 API `[LMCache, §9, p.16]`。

## 相關頁面
- [LMCache 論文筆記](../papers/lmcache.md)
- [vLLM 與 SGLang](./vllm-and-sglang.md)
- [Compute-I/O Pipelining](../concepts/compute-io-pipelining.md)
- [KV Cache Reuse 領域總覽](../overview.md)
