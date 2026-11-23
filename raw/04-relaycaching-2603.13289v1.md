# [RAW SOURCE] RelayCaching: Accelerating LLM Collaboration via Decoding KV Cache Reuse

- **Source ID**: `arXiv:2603.13289v1 [cs.LG]` (28 Feb 2026; preprint dated March 17, 2026)
- **Authors**: Yingsheng Geng (BUPT), Yuchong Gao (Tsinghua), Weihong Wu (UESTC), Guyue Liu (Peking University), Jiang Liu (BUPT)
- **Read-Only Notice**: Extracted verbatim from user-supplied PDF (18 pages). Do not modify.

## Abstract & Core Claims (p.1–2)
- Problem: In Multi-Agent Systems (MAS), upstream agent outputs (specs, reasoning chains, code) are embedded into downstream agent prompts under **different prefixes** (*prefix variation*), causing **cascading context redundancy** whose cumulative prefill cost scales quadratically with interaction turns $O(M^2)$.
- Why prior work fails (§1, §2.2, Fig. 1, p.1–3):
  - **Prefix caching** (vLLM, SGLang) requires strict positional/prefix alignment → fails on prefix mismatch.
  - **Pre-computed caching** (PromptCache, CacheBlend, EPIC) assumes static, offline-encodable content → fails on dynamically generated runtime outputs; and CacheBlend's value-norm detection does not capture directional (cosine) decode-to-prefill deviations while scaling linearly ($K = 20\% \times N$) with length.
  - **KVCOMM** relies on similarity-based retrieval from external anchor pools → reuse rate degrades (88% → 70% on GSM8K) as agent count/diversity grows.
- Approach (**RelayCaching**): Training-free **decode-to-prefill KV reuse** method directly reusing upstream decoding KV caches in downstream prefill with targeted rectification via: (1) **Layer-Range Profiler** (`[L_start, L_end]` + detection layer `L_det`) and (2) **Dual-Criterion Token Selector** (deviation-based + attention-influence-based + suffix-aware).
- Headline results (p.1–2, §5 p.6–8):
  - Achieves **>80% KV cache reuse** across GSM8K, MMLU, HumanEval while matching Full-Prefill accuracy.
  - Reduces per-agent TTFT by up to **4.71×** (at Agent 5 on AIME24, Qwen3-0.6B, Table 2, p.7) and up to **9.2×** vs. Full Prefill (**2.5×** vs. CacheBlend) at 12K tokens (0.42 s vs. 3.89 s full / 1.08 s CacheBlend, §5.3, Fig. 8, p.7–8).

## §3 Empirical Observations (p.3–4; generalized to 5 more models in Appendix A, p.11–13)
Probe setup: 2WikiMQA summarize-then-answer (200 samples), primary model Mistral-7B-Instruct-v0.3; verified across Llama-3.1-8B-Instruct, Qwen2.5-Coder-7B-Instruct, DeepSeek-R1-Distill-Qwen-32B, Qwen3-30B-A3B, Qwen3-0.6B.
1. **High macro-level alignment (§3.1, Fig. 2, p.3)**: Decoding KV vs. Full-Prefill KV maintains Key Norm 0.947, Value Norm 0.926, Key Cosine 0.935, **Value Cosine 0.800** (lowest metric → primary deviation indicator). In contrast, Independent KV shows large Value Norm drop (0.588) and Key/Value Cosine (0.682/0.701), proving pre-computation assumptions differ from decode-to-prefill reuse.
2. **U-shaped layer-wise similarity profile (§3.2, Fig. 3, p.3–4; Fig. 9, p.12)**: Value cosine similarity is high in shallow layers, drops sharply in **middle layers** (where reasoning/context integration occurs), and partially recovers in deep layers. Oracle substitution (Fig. 3b) confirms middle layers dominate downstream recovery; shallow & deep layers yield diminishing returns.
3. **Sparse & inter-layer-correlated token-wise deviations (§3.3, Fig. 4, p.4; Fig. 10, p.13)**: Only a small subset of tokens (position-dependent boundary tokens + content-dependent tokens) show large deviations. Adjacent-layer Spearman rank correlation starts low in earliest layers, then rapidly rises and plateaus (>0.9), meaning high-deviation tokens persist once emerged.

## §4 RelayCaching Methodology (p.4–6, Fig. 5, p.5)
- **Stage $i-1$ Decoding**: Collect pre-RoPE decoding KV cache, save hidden states $h^{(L_{\text{start}})}$, and accumulate attention weights $s_{\text{inf}}(j) = \sum_{t,\ell,h} \alpha_{t,\ell,h,j}$ (Eq. 6).
- **Relay Handoff**: Re-apply RoPE to align reused KV caches to new positions.
- **4.2 Layer-Range Profiler (Offline on auxiliary dataset, e.g., 2WikiMQA)**:
  - Token-wise deviation (Eq. 1): $d_{j,\ell} = 1 - \frac{1}{H}\sum_{h=1}^H \cos(\mathbf{v}_{h,j,\ell}^{\text{reuse}}, \mathbf{v}_{h,j,\ell}^{\text{full}})$; layer similarity $s_\ell = \frac{1}{|I_{\text{reuse}}|}\sum (1 - d_{j,\ell})$ (Eq. 2).
  - `L_start`: Deepest shallow layer with $s_\ell \ge \tau_{\text{st}}$ (default $\tau_{\text{low}}=0.99$, Table 4, p.14). Layers $[0, L_{\text{start}})$ are skipped; load $h^{(L_{\text{start}})}$.
  - `L_end`: Scan forward from $\ell_{\min}$ until first layer followed by $C=2$ consecutive layers where $s_\ell \ge \mu_{\text{last}} - \sigma_{\text{last}}$ and $|s_\ell - s_{\ell-1}| < \lambda \sigma_{\text{last}}$ ($T=5, \lambda=2.0$, Eq. 3, Table 4). Layers $(L_{\text{end}}, L_{\text{full}}]$ are skipped.
  - `L_det`: Second-order difference of adjacent Spearman correlation $\alpha_\ell = \rho_\ell - 2\rho_{\ell-1} + \rho_{\ell-2}$ (Eq. 4); $\ell^*$ is first positive-to-negative transition, $L_{\text{det}} = \ell^* + 1$. Layers $[L_{\text{start}}, L_{\text{det}})$ are fully recomputed; $[L_{\text{det}}, L_{\text{end}}]$ apply sparse token rectification.
  - Profiled configs (Table 5, p.14): Llama-3.1-8B-Instruct `(1, 3, 18)`; Qwen2.5-Coder-7B-Instruct `(3, 4, 22)`; Qwen3-0.6B `(2, 3, 19)`.
- **4.3 Dual-Criterion Token Selector**:
  - **Deviation-based** (Eq. 5): $I_{\text{dev}} = \{j \mid d_{j, L_{\text{det}}} \ge \tau_{\text{dev}} \cdot \mu_{\text{dev}}\}$ (default $\tau_{\text{diff}}=1.5$).
  - **Influence-based** (Eq. 7): $I_{\text{inf-score}} = \{j \mid s_{\text{inf}}(j) \ge \tau_{\text{inf}} \cdot \mu_{\text{inf}}\}$ (default $\tau_{\text{down}}=1.45$).
  - **Suffix-aware correction** (Eq. 8): Always include trailing $K_{\text{suf}}=10$ tokens ($I_{\text{inf-suffix}}$) because attention accumulation biases early tokens while suffix boundary tokens strongly influence newly appended prompts.
  - Final set: $I_{\text{final}} = I_{\text{dev}} \cup I_{\text{inf-score}} \cup I_{\text{inf-suffix}}$ (Eq. 9).

## §5 Evaluation (p.6–8, Appendix B p.14–18)
- Hardware: Single NVIDIA H20 (96 GB), BF16, PyTorch 2.1.0, Transformers 4.50.2.
- **Main Accuracy Results (Table 1, p.7)**:
  - GSM8K (Llama-3.1-8B, 2/3/4 agents): Full Prefill `85.97 / 84.69 / 84.69`, Zero Reuse `40.33 / 40.03 / 53.68`, CacheBlend `76.72 / 77.56 / 74.73`, EPIC `58.73 / 66.46 / 58.42`, KVComm `84.23 / 82.34 / 84.91`, **RelayCaching `84.84 / 85.50 / 85.17`**.
  - MMLU (Llama-3.1-8B, 2/3/4 agents): Full `71.24 / 73.20 / 66.67`, Zero `67.97 / 41.18 / 35.29`, CacheBlend `69.28 / 64.71 / 66.67`, EPIC `69.28 / 45.10 / 43.79`, KVComm `68.63 / 69.28 / 66.01`, **RelayCaching `69.28 / 71.90 / 67.97`**.
  - HumanEval (Qwen2.5-Coder-7B, Pass@1, 2/3/4 agents): Full `82.61 / 85.71 / 87.58`, **RelayCaching `82.61 / 85.09 / 87.58`**.
- **TTFT Breakdown (Table 2, AIME24, Qwen3-0.6B, p.7)**:
  - Agent 2 → Agent 5: Full Prefill `85.2 → 493.9 ms` (5.8× growth); CacheBlend `44.9 → 159.3 ms` (3.10× speedup at Agent 5); **RelayCaching `40.6 → 104.8 ms` (2.6× growth, 4.71× speedup at Agent 5)**; overhead: full recompute 1.6–7.9 ms, index selection 0.5–0.8 ms.
- **Context Length Scaling (Fig. 8, p.7–8)**: At 12,288 cumulative tokens: Full Prefill 3.89 s, CacheBlend 1.08 s (linear scaling due to fixed 20%), RelayCaching **0.42 s** (sub-linear, **9.2×** over Full, **2.5×** over CacheBlend).
- **Ablation on GSM8K 2-agent (Table 3, p.8)**:
  - Full Prefill: 0% reuse, 85.97% Acc
  - `+ Layer Range Profiler`: 46.88% reuse, 85.90% Acc
  - `+ I_dev`: 90.37% reuse, 79.68% Acc (deviation alone misses generation-critical tokens)
  - `+ I_inf-score`: 85.84% reuse, 81.65% Acc
  - `+ I_inf-suffix (Ours)`: **85.35% reuse, 84.84% Acc**
- **Limitation (Appendix C, p.18)**: Assumes **homogeneous MAS** (all agents share identical model architecture); heterogeneous cross-model/cross-size transfer is left to future work.
