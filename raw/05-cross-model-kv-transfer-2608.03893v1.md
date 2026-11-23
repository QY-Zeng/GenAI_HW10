# [RAW SOURCE] Cross-Model KV Cache Transfer in LLM Families: A Closed-Form Linear Mapping for Prefill Reuse

- **Source ID**: `arXiv:2608.03893v1 [cs.LG]` (4 Aug 2026)
- **Authors**: Taekyung Heo, Rasoul Shafipour, Ritchie Zhao, Maximilian Golub, Mohammad Mahdi Kamani, Ritika Borkar, Makesh Tarun Chandran, Pantea Zardoshti, Bita Darvish Rouhani (NVIDIA)
- **Read-Only Notice**: Extracted verbatim from user-supplied PDF (21 pages). Do not modify.

## Abstract & Core Claims (p.1–2)
- Problem: Production LLM serving relies on multi-model orchestration (cost-quality cascading, mid-conversation switching, routing) across different-sized models within a family. Every model swap forces the receiver to re-prefill the accumulated context from scratch.
- Prior cross-model approaches (Table 6, Appendix A, p.3, 13):
  - C2C [Fu et al., 2026] & LatentAlign [Dery et al., 2026]: require gradient-based training.
  - IAM [Zhao et al., 2025]: transfers attention patterns, not KV values.
  - DroidSpeak [Liu et al., 2026, NSDI]: gradient-free & transfers KV values, but requires **identical architecture** (cannot work cross-scale).
  - **Ours**: Only method that is simultaneously **gradient-free, cross-scale, transfers KV values, and closed-form** (Table 6, p.13).
- Core discovery (§2.3, Fig. 2, p.3–4): Across **matched-KV** pairs within a family (same KV head count $n_{\text{kv}}^s = n_{\text{kv}}^t = 8$ and per-head dimension $d_h^s = d_h^t = 128$, even when layer counts $L_s \ne L_t$ and parameter sizes differ), cross-model KV exhibits substantial **linear structure**. On Qwen3 14B→32B, 1 source layer explains **56%** variance in target K ($R^2=0.5572$) and **32%** in V ($R^2=0.3249$), rising to **79%** ($0.7914$) and **65%** ($0.6541$) with $k=8$ source layers (Table 7, p.14).
- Headline results (§4, p.5–9):
  - Across 6 matched-KV pairs in 3 families (Qwen3, Llama 3.1, Ministral 3), closed-form ridge mapper retains **73–98%** of standalone accuracy averaged across 5 benchmarks on 4 **Tier 1** pairs (Qwen3 14B→32B: **97.6%**, Qwen3 8B→32B: **87.5%**, Ministral 3B→8B: **76.2%**, Llama 3.1 8B→70B: **72.8%**), while 2 **Tier 2** pairs degrade sharply (Ministral 3B→14B: **44.2%**, Ministral 8B→14B: **41.6%**; 11–15% floor-normalized) (Table 1, p.6).
  - A nonlinear **MLP** recovers **+24.3 to +36.8 pp** (+37 pp) HellaSwag retention on Tier 2 failure pairs, bringing all 4 tested pairs above **90%** (Table 3, p.7).
  - Speedup: **2.7–25×** faster than re-prefill in small-to-large direction (4.4–25.1× on Qwen3 14B→32B; 3.3–6.9× on 32B→14B across 64–32K tokens, Table 5 p.9, Table 16 p.19).
  - Stable across 10-turn CoQA multi-turn handoff (1.7 pp S→L widening over 10 turns; 0.33 pp/turn L→S linear drift, §4.6, Fig. 4, p.8–9).

## §3 Closed-Form Per-Head Ridge Mapper Design (p.4–5, Fig. 3)
Three core components:
1. **Per-head ridge regression (§3.1, Eq. 3–4, p.4–5)**:
   - Independent linear map per target `(layer l, head h)` for K and V separately: $\hat{\mathbf{K}}_t^{l,h} = \mathbf{X}_K^l \mathbf{W}_K^{l,h} + \mathbf{b}_K^{l,h}$.
   - Closed-form Tikhonov solution: $\mathbf{W}^* = (\mathbf{X}^\top \mathbf{X} + \lambda \mathbf{I})^{-1} \mathbf{X}^\top \mathbf{Y}$ with $\lambda = 0.01$ (centered $\mathbf{X}, \mathbf{Y}$).
   - Calibration: 500 FineWeb-Edu sequences × 1,024 tokens, stride-4 subsampled → $N \approx 128\text{K}$ tokens/head.
   - Compute (Appendix E, p.17): ~**47–87 min** per pair on a single 8×H100 node (no backprop); $\mathbf{X}^\top \mathbf{X}$ computed once per target layer and shared across heads.
   - Size & storage (Table 12, p.17): 1.01–3.36 B total params (**4–12 GB**, e.g., Qwen3 14B→32B $k=8$: 1.07 B / 4 GB; Llama 3.1 8B→70B $k=20$: 3.36 B / 12 GB). Can live on host CPU RAM/disk and page in (~80–480 ms over PCIe Gen4/5).
2. **Cross-layer source selection (§3.2, Eq. 5, p.5)**:
   - Each target layer $l$ selects its **top-$k$** most predictive source layers by head-averaged $R^2$ (averaged over $K_{\text{stripped}}$ and $V$) and concatenates all KV heads from those $k$ source layers. Largest single contributor in ablation (§4.3).
3. **Content-space mapping / RoPE factoring (§3.3, p.5)**:
   - Strip source RoPE, map in position-free content space, re-encode with target RoPE: $\hat{\mathbf{K}}_t = (\mathbf{K}_s \mathbf{R}_{\Theta_s}^{-1}(t)\mathbf{W}_K + \mathbf{b}_K)\mathbf{R}_{\Theta_t}(t)$.
   - Decouples position from semantics so the 1,024-token calibration fit generalizes to different RoPE configs and up to 32K contexts. Values have no RoPE and map directly.

## §4 Experiments & Deep Mechanism Analysis (p.5–9, Appendices C–H p.14–21)
- **Benchmarks (§4.1, Table 11, p.6, 16)**: ARC-Challenge, HellaSwag, WinoGrande, MMLU (5-shot), GSM8K (8-shot CoT), prefix-conditioned WikiText-2 PPL, CoQA (100 convs, ~15 turns); plus 3 held-out benchmarks PIQA, BoolQ, ARC-Easy (Table 18, p.21: Tier 1 pairs all >96%, Tier 2 <64%).
- **Ablation on Qwen3 14B→32B (§4.3, Table 2 p.7, Tables 7–9 p.14–16)**:
  - Full ($k=8$, ridge, content-space): ARC-C 61.60, HellaSwag 80.70, WinoGrande 68.98, MMLU 78.09, GSM8K 90.98, PPL 7.33.
  - `− inference RoPE` (mismatch): MMLU crashes 78.09 → 25.79, GSM8K crashes 90.98 → 4.17.
  - `− all RoPE` (coupled): Similar at 1,024 tokens, but fails to generalize across RoPE configs/lengths.
  - `− RoPE − cross-layer (k=1)`: HellaSwag 44.81, GSM8K 0.38, PPL 22.73 (largest drop).
  - Calibration robustness (Table 8, p.15): Wide flat regions for $\lambda \in [0, 0.1]$ (collapses at $\lambda=1$: −15.79 pp) and $N \in [50, 1000]$ (flattens after $N=200$). Calibration domain matters: Wikipedia retains 99.4% mean vs. FineWeb-Edu, whereas CodeAlpaca drops −5.24 pp on HellaSwag (95.9% mean, Table 9, p.16).
- **Nonlinear MLP Recovery (§4.4, Table 3, p.7)**:
  - Per-(layer, head, K|V) 2-hidden-layer 1024-unit ReLU MLP trained with Adam (lr $10^{-3}$, 20 epochs, MSE).
  - On Tier 1 pairs, MLP slightly underperforms ridge (Qwen3 14B→32B: 97.6% → 97.3%, −0.3 pp; Ministral 3B→8B: 93.3% → 91.8%, −1.5 pp).
  - On Tier 2 failure pairs, MLP rescues retention: Ministral 3B→14B **68.0% → 92.3% (+24.3 pp)**; Ministral 8B→14B **58.7% → 95.5% (+36.8 pp)**.
- **What determines transfer quality? (§4.5, Table 4, p.7–8)**:
  - **Calibration $R^2$ fails to predict cross-pair retention**: Across 12 matched-KV pair evaluations (6 S→L + 6 L→S), calibration $R_K^2$ correlates at Pearson **$r = -0.20$**! (E.g., Llama 3.1 8B→70B has $R_K^2=0.84$ and 94% HS S→L, but only 37% L→S; Ministral 3B→8B has same $R_K^2=0.84$ and 93% both ways.)
  - **Attention-output cosine** correlates with HellaSwag retention at Pearson **$r = +0.57$**.
  - **Error placement (concentration) > error magnitude**: Projecting K error onto target query right singular vectors $\mathbf{Q}_h$ (K-concentration) reveals that on Tier 2 failure pairs, ridge error lands in attention-sensitive subspaces (and eval-domain $R_K^2$ is deeply negative: −7.81 and −3.22). MLP reduces K-concentration ($\Delta \approx -2.5$), raises attention-output cosine ($\Delta \approx +0.45$), and restores retention!
- **Prefill Latency (§4.7, Table 5 p.9, Table 16 p.19)**:
  - Qwen3 14B→32B ($k=8$): 64 tok (14.0 vs 61.7 ms, 4×), 8K tok (67.8 vs 1,154.8 ms, 17×), 32K tok (277.6 vs 6,975.3 ms, **25×**).
  - Qwen3 32B→14B ($k=20$): 32K tok (427.1 vs 2,952.7 ms, **7×**).
  - Llama 3.1 8B→70B ($k=20$): 32K tok (777 vs 11,562 ms, **14.9×**).

## §5 Limitations & Future Work (p.9)
- Single-domain calibration (FineWeb-Edu); in-sample $k$ selection (LOO max effect ≤2.49 pp, Table 17, p.21); only tested **matched-KV** pairs within the **same family** over **dense full-attention** models (cross-family, mismatched-KV, and hybrid attention/SSM architectures like Nemotron 3 remain future work).
