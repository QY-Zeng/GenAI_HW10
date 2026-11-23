# [RAW SOURCE] CacheBlend: Fast Large Language Model Serving for RAG with Cached Knowledge Fusion

- **Source ID**: `arXiv:2405.16444v3 [cs.LG]` (3 Apr 2025)
- **Venue**: Twentieth European Conference on Computer Systems (EuroSys '25), March 30–April 3, 2025, Rotterdam, Netherlands. DOI: `10.1145/3689031.3696098`
- **Authors**: Jiayi Yao (University of Chicago / CUHK Shenzhen), Hanchen Li, Yuhan Liu, Siddhant Ray, Yihua Cheng, Qizheng Zhang (Stanford), Kuntai Du, Shan Lu (Microsoft Research / UChicago), Junchen Jiang (University of Chicago)
- **Code**: `https://github.com/LMCache/LMCache`
- **Read-Only Notice**: Extracted verbatim from user-supplied PDF (16 pages). Do not modify.

## Abstract & Core Claims (p.1–2)
- Problem: LLM inputs in RAG incorporate multiple retrieved text chunks. Prefix caching only reuses the first chunk (prefix). Full KV reuse (e.g., PromptCache) reuses non-prefix chunks by adjusting positional encoding, but **ignores cross-attention** between chunks, causing severe quality drop (e.g., Messi vs. Ronaldo FIFA World Cup goals example, Fig. 3, p.4).
- Approach (**CacheBlend**): Fuses multiple pre-computed KV caches regardless of prefix position by **selective KV recompute**—recomputing KV values of a small subset of tokens (<15%, empirically 5–18% / 10–20%) on each layer while reusing other tokens' KV.
- Pipelining: Parallelizes partial KV update on layer $i$ with fetching pre-computed KV cache of layer $i+1$ into GPU memory, allowing storage in slower non-volatile devices (CPU RAM / NVMe SSD / slower disks) without increasing TTFT.
- Headline results (p.1, §7 p.10, §7.2 p.12):
  - Reduces TTFT by **2.2–3.3×** compared to full KV recompute / prefix caching across 3 open-source LLMs (Mistral-7B, Yi-34B [8-bit], Llama-70B [8-bit]) and 4 datasets (2WikiMQA, Musique, SAMSum, MultiNews).
  - Increases inference throughput by **2.8–5×** vs. full KV recompute (and up to **3.3×** vs. prefix caching, §7 p.10).
  - Quality drop ≤ **0.01–0.03** (within 0.02 in Fig. 12, §7.2 p.12) vs. full KV recompute; improves quality by **0.1–0.2** absolute F1 on QA and **0.03–0.25** absolute Rouge-L on summarization (0.15–0.35 overall, p.10) vs. full KV reuse.

## §2–3 Background & Motivation (p.2–4)
- Prefill on 4,000 tokens takes 3 s (Llama-34B) or 6 s (Llama-70B) on one A40 GPU (§2, p.3).
- Prefix caching (vLLM, SGLang, RAGCache) only saves prefill of chunk 1; marginal saving for multi-chunk RAG (§3.2, p.3–4).
- Full KV reuse (PromptCache [24]) concatenates independently precomputed caches using dummy prefix buffers, preserving positions but completely missing cross-attention between chunks, causing large discrepancies in the forward attention matrix (Fig. 4, p.5). Disparity widens with more chunks (Fig. 2, p.4).

## §4 Fast KV Cache Fusing (p.5–7)
- Terminology (Table 1, p.5):
  - **KV deviation**: $\Delta_{\text{kv}}(KV_i, KV_i^{\text{full}})[j] = |KV_i[j] - KV_i^{\text{full}}[j]|$ on layer $i$, token $j$.
  - **Attention deviation**: $\Delta_{\text{attn}}(A_i, A_i^{\text{full}}) = \|A_i - A_i^{\text{full}}\|_2$ on layer $i$.
- **Selective KV recompute (§4.2, Fig. 5, p.5–6)**: Mask layer $i$ input to selected tokens → compute $Q_i, K_i, V_i$ only for selected tokens → expand $K_i, V_i$ by reusing precomputed KV of unselected tokens → run attention module. Recomputing $r\%$ tokens incurs $r\%$ of full prefill compute.
- **RoPE correction (Footnote 3 p.6, Appendix A p.16)**: Precomputed K vectors are adjusted with correct positional encoding by multiplying by a rotation matrix $R_{\Theta, m}^d$; Proposition A.1 proves RoPE attention score depends only on relative distance $l$. Overhead is negligible (done once).
- **Insight 1 (§4.3, Fig. 6, p.6)**: Recomputing tokens with highest KV deviation (**HKVD tokens**) produces the biggest drop in attention deviation. Due to attention sparsity (Fig. 7, p.7), ~10–15% (10–20%) tokens have much higher KV deviation.
- **Insight 2 (§4.3, Fig. 8, p.7)**: HKVD tokens exhibit high Spearman rank correlation across consecutive layers (slow embedding change across layers).
- **Gradual filtering (§4.3, Fig. 9, p.7)**: Recompute all tokens on Layer 1 (or check layer) → pick top $r_1\%$ HKVD tokens (slightly > $r\%$) for Layer 2 → recompute those on Layer 2 and filter down to $r_2\%$ for Layer 3, etc. Extra precomputed KV for layer $i$ is discarded once moving to layer $i+1$, so memory overhead is negligible.

## §5–6 System Design & Implementation (p.7–9)
- **Basic insight (§5, p.7)**: If selective recompute delay $\le$ KV loading delay into GPU memory, layer-wise pipelining hides recompute delay completely.
  - Example (p.8): Llama-7B with 4K context: recomputing 15% takes 3 ms/layer vs. loading from NVMe SSD takes 16 ms/layer (completely hidden). Llama-70B: recomputing 15% takes 7 ms vs. loading 4 ms (not completely hidden).
- **Three Components (§5.1, Fig. 11, p.8–9)**:
  1. **Loading Controller**: Uses $T_{\text{recompute}}(r\%, LLM, L) = r\% \times \text{Prefill}(LLM, L)$ and $T_{\text{load}}(LLM, L, \text{device}) = \frac{\text{PerTokenKVSize}(LLM) \times L}{\text{Throughput}(\text{device})}$. Picks $\max(r\%, r^*\%)$ where $r^*\% = 15\%$ (minimal ratio for negligible quality drop), or given fixed 15%, picks cheapest storage device satisfying $T_{\text{recompute}} \ge T_{\text{load}}$ via storage cost estimator $C_{\text{store}}$.
  2. **KV Cache Store**: Splits input into chunks (e.g., 512 tokens with LangChain in §7.1), hashes each chunk (similar to vLLM block hashing), LRU eviction; hash tables take 16 MB for 1M chunks in CPU (§6, p.9).
  3. **Fusor**: Performs layer-wise selective recompute on GPU queue.
- **Implementation (§6, p.9)**: ~3K LoC Python on vLLM & PyTorch v2.0 with 3 interfaces: `fetch_kv(text, layer_id)`, `prefill_layer(input_dict, KVCache)` (tracks `input_org`, `check_flag`, `HKVD_indices`), `synchronize()`. Uses two threads to pipeline `prefill_layer` of layer $i$ with `fetch_kv` of layer $i+1$.

## §7 Evaluation (p.10–13)
- Hardware (§7.1, p.10): Runpod with 128 GB RAM, 2× NVIDIA A40 GPUs, 1 TB NVMe SSD (4.8 GB/s). 1 GPU for Mistral-7B & Yi-34B (8-bit); 2 GPUs for Llama-70B (8-bit).
- Datasets (§7.1, p.10–11): 2WikiMQA (200 cases, F1), Musique (150 cases, F1), SAMSum (200 cases, Rouge-L), MultiNews (60 cases, Rouge-L); plus synthetic `Musique extended` and `2WikiMQA extended` (6,000 queries: 1,500 original + 4,500 GPT-4 simulated, top-6 chunks of 512 tokens in random order).
- Baselines: Full KV recompute, Prefix caching (SGLang style, idealized zero load delay), Full KV reuse (PromptCache), MapReduce (CacheBlend 2–5× lower TTFT & higher F1, Fig. 13, p.12), MapRerank (slightly lower TTFT than CacheBlend but much worse quality).
- Sensitivity (§7.3, p.12–13):
  - Varying recompute ratio on Yi-34B (Fig. 16, p.12): **5%–18%** recompute ratio yields ≤ **0.002** loss in F1/Rouge-L, translating to **4.1–6.6×** TTFT reduction vs. full KV recompute and **3.4–6.1×** vs. prefix caching.
  - Consistent reduction across varying chunk numbers (3–12), chunk lengths (300–900), and batch sizes (2–10; prefill dominates more at larger batch sizes, Fig. 15).
  - Storage devices (Fig. 17, p.12–13): Works on both CPU RAM and slower SSD (4 Gbps); gap between CacheBlend and Full KV reuse narrows on slower storage because loading dominates.

## §9 Limitations & Future Work (p.13)
- Applies only to Transformer architectures (not Mamba/Griffin).
- Not yet tested with newer serving engines like DistServe or cross-node KV sharing, nor varied quantization settings.
