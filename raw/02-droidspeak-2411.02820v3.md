# [RAW SOURCE] DroidSpeak: KV Cache Sharing for Cross-LLM Communication and Multi-LLM Serving

- **Source ID**: `arXiv:2411.02820v3 [cs.MA]` (19 Dec 2024; subsequently published at USENIX NSDI '26 as cited by Cross-Model KV Transfer)
- **Authors**: Yuhan Liu (UChicago / Microsoft intern), Yuyang Huang, Jiayi Yao, Zhuohan Gu, Kuntai Du, Hanchen Li, Yihua Cheng, Junchen Jiang (University of Chicago); Shan Lu, Madan Musuvathi, Esha Choukse (Microsoft)
- **Read-Only Notice**: Extracted verbatim from user-supplied PDF (17 pages). Do not modify.

## Abstract & Core Claims (p.1–2)
- Problem: Multi-agent workflows and multi-LLM serving increasingly run multiple fine-tuned LLMs (e.g., LoRA or domain-specialized variants) derived from the **same foundational model** on the **same shared context**, causing repeated prefill computation and duplicated KV cache storage.
- Naively reusing the entire KV cache across fine-tuned variants causes huge accuracy degradation (HotpotQA loses >50% F1 points across all pairs, §3.2.1, Fig. 6, p.5).
- Approach (**DroidSpeak**): Exploits the insight that fine-tuning alters only a small subset of **critical layers** (average **11%** of layers, §3.2.2, Fig. 7, p.5–6). Selectively recomputes a **contiguous chunk** of critical layers while reusing non-critical layers, minimizing transition points (`reuse → recompute`) to at most one.
- Headline results (p.1–2, §5 p.8–11):
  - Reduces prefill latency by **1.7–2.6×** across 3 datasets and 8 model pairs without compromising accuracy.
  - Improves online serving throughput by up to **3×** (2–3× under SLO, §5.3, Fig. 15, p.10–11).
  - Reduces memory footprint by up to **1.5×** in shared KV storage scenarios (Fig. 1, p.1–2).

## §2 Background & Motivation (p.2–4)
- Transformer concepts (§2.1, Fig. 2, p.2): Distinguishes **KV cache** (K and V tensors) and **E cache** (input embedding / hidden-state E vector fed into each layer).
- Performance metrics (§2.1, p.3): TTFT, TBT (Time Between Tokens), E2E latency, Goodput (throughput meeting SLOs).
- Prefill interference (§2.3, Fig. 5, p.3–4): Long prefill phases create scheduling delays that ripple into decode TBT and reduce overall goodput.
- Interconnects (§2.4, p.4): GPU clusters (A100/H100/GB200) use high-bandwidth InfiniBand (25–50 GB/s per GPU pair).

## §3 Empirical Insights on Cross-LLM KV Cache Sharing (p.4–6)
- Benchmark setup (§3.1, Table 1, p.4): 8 model pairs sharing the same foundational model (baseline = context generator; specialized = context user on a separate node):
  1. `glue_sst2` ← `conllpp`
  2. `gsm8k` ← `glue_stsb`
  3. `phi-3.5-mini-instr-adapter` ← `phi-3.5-mini-instr-task15`
  4. `phi-3.5-mini-instr-adapter-v2` ← `phi-3.5-mini-instr-task15`
  5. `llama-3-8b-sft-lora-ultrachat` ← `fingpt-llama-3-8b`
  6. `llama-3-8b-chat-lora` ← `fingpt-llama-3-8b`
  7. `mistrallite` ← `mistral-7b`
  8. `llama-3.1-70b-instruct` ← `llama-3.1-70b`
  Across 3 LongBench datasets: HotpotQA (300 contexts, med 10,933 tokens, P95 18,650), 2wikimQA (200, med 7,466, P95 10,705), multifieldQA_en (150, med 8,084, P95 14,680) (Table 2, p.10).
- **Insight 1 (§3.2.1, Fig. 6, p.4–5)**: Reusing the whole KV cache between models leads to a huge loss in accuracy (>50% F1 loss on HotpotQA).
- **Insight 2 (§3.2.2, Fig. 7, p.5–6)**: Only a small subset of layers are sensitive to KV reuse (on average **11%** of layers have >10% F1 drop when reused alone = *critical layers*), scattered across different depths of the model.
- **Insight 3 (§3.2.3, Fig. 8, p.6)**: Variation in KV cache error sensitivity across different inputs is only notable for critical layers (e.g., Layer 23 in `llama-3-8b-sft-lora-ultrachat` shows >50% F1 swings, while non-critical layers have near-zero variance across inputs).

## §4 DroidSpeak Design & Implementation (p.6–8)
- **Two Challenges of Non-Contiguous Selective Reuse (§4.1, Fig. 9–11, p.6–7)**:
  1. **Efficiency challenge**: Switching from KV reuse to recompute at a *transition layer* requires loading the baseline model's **E cache** as a proxy starting point. E cache is huge: up to **2×** KV cache size on Mistral-7B / Llama-3-8B and up to **4×** KV cache size on Llama-3.1-70B (because KV cache is shrunk by GQA).
  2. **Accuracy challenge**: Each loaded baseline E cache introduces deviation that propagates through subsequent layers (Fig. 10, p.7). Recomputing scattered critical layers requires multiple transitions (multiple E-cache injections), consistently underperforming recomputing a single contiguous block (Fig. 11, p.7).
- **Reuse Patterns (§4.2, p.7)**: Restrict to at most **one** `reuse → recompute` transition (one E-cache load): general pattern `recompute → reuse → recompute → reuse` (stored as 3 integers), with special cases `recompute → reuse → recompute` and `reuse → recompute → reuse`.
- **Offline Profiling (§4.3, Fig. 12, p.7–8)**: Profile each model pair on 50 HotpotQA training contexts (§5.1, p.9) to generate an accuracy heatmap and accuracy-efficiency Pareto frontier (e.g., `glue_sst2` ← `conllpp` recomputes layers 13–23).
- **Two-Stage System (§4.4, Fig. 13, p.8)**:
  - Offline stage: Profile model pair → Pareto-optimal reuse patterns.
  - Online stage: Dynamic policy selects a point on the Pareto frontier based on latency SLO and system load (more reuse under high load for throughput; more recompute under low load for higher accuracy).
- **Implementation (§4.5, p.8)**: ~2K LoC Python on PyTorch v2.0, CUDA 12.0, HuggingFace, and **LMCache 0.1.3** with interfaces `store_kv`/`store_e`, `fetch_kv`/`fetch_e` (via `torch.distributed`), and `partial_prefill(recompute_config, context)`.

## §5 Evaluation (p.8–12)
- Hardware (§5.1, p.9): Two Azure `Standard_ND96amsr_A100_v4` VMs (8× 80 GB A100 each) connected via InfiniBand.
- **Latency & Quality (§5.2, Fig. 14, p.9–10)**: **1.7–2.6×** prefill delay reduction vs. full prefill (vLLM) without sacrificing accuracy; far higher F1 than full KV reuse.
- **Online Serving (§5.3, Fig. 15, p.10–11)**: At ≤1% accuracy drop, supports **2–3×** higher throughput (QPS) under SLOs, also reducing TBT and E2E latency via reduced prefill interference.
- **Latency Breakdown (§5.4, Fig. 16, p.10–11)**: Across 0–32K input tokens, prefill latency cut roughly in half; InfiniBand transfer overhead for KV + E cache is at most **11%** of DroidSpeak's total prefill delay.
- **Cross-Dataset Robustness (§5.5, Fig. 17, p.10–11)**: Profiling on one dataset (50 HotpotQA contexts) generalizes to unseen datasets (`2wikimQA`, `multifieldQA_en`) with max 4 F1 points difference (average **2 points**).
- **Other Tasks (§5.6, Fig. 18, p.11–12)**: Validated on GSM8K math reasoning with MAmmoTH2.
- **vs. Smaller Model (§5.7, Fig. 19, p.11–12)**: Llama-3.1-8B-Instruct gives ~4× lower prefill delay than Llama-3.1-70B-Instruct but loses ~50% F1; DroidSpeak on 70B preserves accuracy while scaling latency smoothly without model-swapping GPU reload overhead.

## §6 Discussion & Limitations (p.12)
- Currently requires **same foundational model / identical architecture**; extending to different foundational models (structurally different architectures) is left as future work.
- Future directions: token-subset recomputation, power/energy reduction (prefill is compute/power heavy), combining with KV compression, security/privacy risks of sharing intermediate states across agents.
