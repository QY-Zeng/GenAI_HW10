# Node 1 產出：Wiki 檢索清單 (`sources.md`)

- **簡報主題**：KV Cache Reuse：從單模型前綴快取到多代理與跨模型重用
- **知識邊界**：100% 僅限本專案 `wiki/` 目錄內已驗證頁面（共檢索 16 頁，涵蓋全部 5 篇論文）。

## 1. 領域總覽與跨文獻綜合（3 頁）
- [KV Cache Reuse 領域全景總覽](../wiki/overview.md) (`wiki/overview.md`)
- [跨論文方法全景對照](../wiki/syntheses/kv-reuse-landscape.md) (`wiki/syntheses/kv-reuse-landscape.md`)
- [跨文獻張力與差異彙整](../wiki/syntheses/conflicts-and-tensions.md) (`wiki/syntheses/conflicts-and-tensions.md`)

## 2. 五篇核心論文筆記（5 頁）
- [CacheBlend](../wiki/papers/cacheblend.md) (`wiki/papers/cacheblend.md`)
- [DroidSpeak](../wiki/papers/droidspeak.md) (`wiki/papers/droidspeak.md`)
- [LMCache](../wiki/papers/lmcache.md) (`wiki/papers/lmcache.md`)
- [RelayCaching](../wiki/papers/relaycaching.md) (`wiki/papers/relaycaching.md`)
- [Cross-Model KV Cache Transfer](../wiki/papers/cross-model-kv-transfer.md) (`wiki/papers/cross-model-kv-transfer.md`)

## 3. 核心技術概念（5 頁）
- [Selective KV Recomputation](../wiki/concepts/selective-kv-recomputation.md) (`wiki/concepts/selective-kv-recomputation.md`)
- [KV Deviation Metrics](../wiki/concepts/kv-deviation-metrics.md) (`wiki/concepts/kv-deviation-metrics.md`)
- [E-Cache Transition Overhead](../wiki/concepts/e-cache-transition-overhead.md) (`wiki/concepts/e-cache-transition-overhead.md`)
- [RoPE Position Alignment](../wiki/concepts/rope-position-alignment.md) (`wiki/concepts/rope-position-alignment.md`)
- [Compute-I/O Pipelining](../wiki/concepts/compute-io-pipelining.md) (`wiki/concepts/compute-io-pipelining.md`)

## 4. 系統與效能指標實體（3 頁）
- [LLM 推理系統效能指標](../wiki/entities/llm-serving-metrics.md) (`wiki/entities/llm-serving-metrics.md`)
- [vLLM 與 SGLang](../wiki/entities/vllm-and-sglang.md) (`wiki/entities/vllm-and-sglang.md`)
- [LMCache 系統架構](../wiki/entities/lmcache-system.md) (`wiki/entities/lmcache-system.md`)
