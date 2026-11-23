# [RAW SOURCE] LMCache: An Efficient KV Cache Layer for Enterprise-Scale LLM Inference

- **Source ID**: `arXiv:2510.09665v2 [cs.LG]` (5 Dec 2025)
- **Authors**: Yuhan Liu*, Jiayi Yao*, Yihua Cheng* (equal contribution), Yuwei An, Xiaokun Chen, Shaoting Feng, Yuyang Huang, Samuel Shen, Rui Zhang, Kuntai Du, Junchen Jiang (Tensormesh Inc. & University of Chicago)
- **Code**: `https://github.com/LMCache/LMCache`
- **Read-Only Notice**: Extracted verbatim from user-supplied PDF (19 pages). Do not modify.

## Abstract & Core Claims (p.1–2)
- Problem: Stored KV caches in enterprise deployments increasingly exceed GPU HBM capacity, while two trends require moving KV caches outside GPUs: (1) **Cross-query context caching (cache offloading)** and (2) **Prefill–Decode (PD) disaggregation** (cross-engine/GPU cache transfer).
- Approach (**LMCache**): First and most widely adopted open-source enterprise-grade KV caching layer sitting between LLM inference engines (vLLM, SGLang) and heterogeneous storage/network tiers (CPU DRAM, local disk, remote disk, Redis, S3, Mooncake, InfiniStore, etc.; over Ethernet, RDMA, NVLink).
- Three core contributions (p.1–2):
  1. **Highly optimized KV data movement**: Batched chunk-level operations (default 256 tokens/chunk), compute-I/O pipelining (layer-wise + async prefetch), zero-copy reference counting & dynamic offloading.
  2. **Standardized modular KV cache connector**: Decouples LMCache from fast-evolving inference engines (15–20 new open-weight models/week in 2025; one prominent LLM every 4 days).
  3. **First-class Controller API**: `lookup`, `move`, `clear`, `pin/unpin`, `compress/decompress` enabling KV-cache-aware routing, migration, and P2P sharing.
- Headline results (p.1–2, §8 p.10–15):
  - Up to **15×** higher throughput (2.3–14× in single-node CPU offloading vs. strongest baseline, Fig. 8, p.11) and **1.9–8.1×** lower TTFT (at least 2× lower latency across diverse settings).
  - Real-trace evaluation (Company F & G): **3.7–6.8×** smaller TTFT and **19–58%** smaller ITL at high QPS (§8.3, Fig. 9–10, p.12).
  - Centralized remote storage (15 Gbps): **1.3–3×** higher throughput (§8.4, Fig. 11, p.12–13).
  - PD disaggregation vs. vLLM native PD: **1.53–1.84×** lower mean TTFT and **1.12–1.66×** lower mean ITL (§8.5, Fig. 12, p.13–14).

## §2 Real-World Usage Statistics (p.2–3)
- Voluntary telemetry over 5 weeks (Fig. 1, 3, 4, p.1, 3):
  - Normalized users grew **23.21×**; stored KV cache size grew **5.57×**; the non-GPU portion far exceeds GPU HBM capacity (Fig. 3).
  - Average reuse per token beyond GPU memory grew rapidly; **>19%** of users reuse stored tokens more than **1.5×** (Fig. 4).

## §3 Three Systems Challenges (p.4–5)
1. **I/O inefficiency under paged memory (§3.1.1, Table 1, p.4)**:
   - Legacy `torch.save`/`torch.load` achieves sub-1 GB/s.
   - vLLM / SGLang use paged attention with tiny fixed pages (16–64 KB; e.g., 62.5 KB = 16 tokens × 1 layer in Llama-3.1-8B-Instruct, Footnote 2 p.6).
   - Small non-contiguous transfers severely underutilize bandwidth: Table 1 (RCCL/UCCL) shows **64 KB → 4 GB/s**, **256 KB → 13 GB/s**, **1 MB → 30 GB/s**, **10 MB → 46 GB/s**, **16 MB → 49 GB/s**, **100 MB → 49 GB/s** (needs ≥16 MB to saturate 8×400 Gbps NICs; 1–2 MB for 75–80% PCIe 5.0).
2. **Compatibility with fast-evolving engines (§3.1.2, p.4)**: Frequent attention kernel & memory layout changes (SWA, MLA, new models).
3. **Lack of management APIs (§3.1.3, p.4–5)**: Routers need global KV locations; enterprises request explicit pinning (financial firm) or compress+transfer APIs (agent company).

## §4–7 Architecture, Optimizations & APIs (p.5–10)
- **End-to-end architecture (§4, Fig. 5–6, p.5–7)**: KV Connector → Token Processor → Cache Engine / Storage Manager (Local, PD, P2P, Remote backends) + Event Manager + Memory Allocator + Transfer Channel (NVLink, RDMA, TCP) + Centralized Cache Controller.
- **Performance Optimizations (§5, p.6–8)**:
  - **§5.1 Batched Operations**:
    - *Configurable Chunk Size* (default **256 tokens/chunk** across multiple layers) via intermediate contiguous GPU streaming buffer + custom CUDA gather/scatter kernels + DMA.
    - *Parallel Store/Load* across full-duplex heterogeneous tiers simultaneously.
    - *Delayed Decode KV Cache Storing*: Buffers decode tokens until a full chunk is ready before offloading.
  - **§5.2 Compute-I/O Overlapping**:
    - *Layer-wise pipelining*: Separate CUDA streams per layer; fixed single-layer GPU buffer overlaps layer $i$ compute with layer $i+1$ KV load.
    - *Asynchronous compute & prefetch*: Uses scheduler queue wait time to prefetch KV from remote/disk into CPU/GPU.
  - **§5.3 Minimum Data Copy**:
    - *Zero-Copy Operations*: Reference counting (like OS PCB counter) when writing KV to multiple tiers concurrently.
    - *Dynamic Offloading* (Fig. 7, p.7–8): Three pointers (`Start`, `Current`, `End`) over vLLM's GPU free-page pool duplicate only a configurable window of free pages to CPU (trading duplication ratio vs. allocation stall risk).
- **Standardized KV Connector API (§6, Table 2, p.8–9)**:
  - Scheduler side: `get_num_new_matched_tokens` (may return `None` to defer request & overlap I/O with other requests' compute), `update_state_after_alloc`, `build_connector_meta`.
  - Model runner side: `start_load_kv`, `wait_load_kv`, `start_store_kv`, `wait_store_kv`.
  - Adopted by NVIDIA Dynamo, RedHat llm-d, ByteDance AIBrix, vLLM Production Stack, KServe, and proprietary connectors.
- **Controller APIs (§7, Table 3, p.9–10)**:
  - Two layers: centralized controller manager + per-instance workers.
  - Internal: `batched_admit`/`batched_evict`, `batched_p2p_lookup`.
  - External: `lookup(tokens)`, `move(...)`, `clear(...)`, `pin/unpin(...)`, `compress/decompress(...)`.

## §8 Evaluation Details (p.10–15)
- Models: Llama-3.1-8B-Instruct, Sao10K-L3-8B, Llama-3.1-70B-Instruct, Qwen2.5-Coder-32B-Instruct, Qwen2.5-72B-Instruct, Qwen3-Coder-480B-A35B-Instruct-FP8, Qwen3-32B (SGLang).
- Hardware: 8×H100 (GMI Cloud); sensitivity on B200 (Fig. 15, p.14–15).
- **Single-node CPU offloading (§8.2, Fig. 8, p.11)**: 10K-token inputs (20K for 8B), 500 GB CPU DRAM limit, 40 initial users. At QPS=1: **1.9–8.1×** smaller TTFT, **7–92%** smaller ITL; **2.3–14×** higher throughput at same TTFT vs. Basic vLLM, vLLM native CPU offloading (fails on Qwen3-Coder-480B), and 2 commercial APIs.
- **Component-wise (§8.6, Table 5, Fig. 13–14, p.13–14)**:
  - CPU loading bandwidth (Table 5): LMCache achieves **400 Gbps** vs. vLLM native CPU offloading **88 Gbps** (**4.5×** higher).
  - Async compute overlapping (Fig. 13): Reduces end-to-end delay by **1.46×**.
  - PD transmission (Fig. 14): 3.68 s vs. naive vLLM 4.47 s because vLLM native NIXL transfers page-by-page.
- **Sensitivity (§8.7, Fig. 15, p.14–15)**: On B200, at **32 Gbps** network bandwidth, LMCache KV loading beats prefill **only when context length > 256K tokens**; at **64 or 128 Gbps**, loading beats prefill across all context lengths → motivates **adaptive load-vs-prefill decisions**.
- **SGLang (§8.8, Fig. 16, p.15)**: On Qwen3-32B (2×H100, TP=2), matches SGLang native CPU offloading while adding hierarchical/distributed storage support.

## §9 Real-World Lessons & Experience (p.15–16)
1. **Remote storage is faster than prefill**: Modern object stores (e.g., S3 Express jumped from ~100 MB/s to ~1 GB/s) let Company C achieve **22–32% lower TTFT** from remote object store vs. full prefill.
2. **Context truncation halves prefix cache hit rates**: Sliding-window truncation keeping only recent tokens drops Company F's prefix cache hit rate from **~85% to ~45%** (aligning with Manus context engineering lessons [Ji, 2025]).
3. **Unexpectedly high hit rates in production**: Company G saw **50%** hit rate from dynamically reusable contexts (coding assistants, chat histories, RAG).
4. **Containerized Docker/K8s deployment** is industry standard; **Python + careful CUDA/C++ optimizations** beats rewriting in Rust for velocity & community contributions (now supports 8+ extra backends: NFS, WEKA, GDS, Mooncake, NIXL, S3, InfiniStore, Valkey; 4 accelerators: NVIDIA, AMD, Ascend, TPU).
5. **Industry vs. academia tension**: Prioritizing enterprise stability/offloading delayed flexible attention-customization APIs (like token dropping) needed by researchers.
