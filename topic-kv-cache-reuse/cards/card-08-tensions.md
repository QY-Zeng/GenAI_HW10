# 證據卡 08：四大跨文獻張力與工程前提邊界

- **唯一來源頁**：`wiki/syntheses/conflicts-and-tensions.md`（嚴禁混入其他來源）
- **張力 1（靜態 RAG vs. 動態 MAS）**：CacheBlend 在靜態 RAG 品質損 ≤ 0.02 `[CacheBlend, §7.2, p.12]`；但 RelayCaching 實測將其移至動態多代理 Decode-to-Prefill 時 GSM8K 跌至 74.73–77.56% 且 12K 線性膨脹（1.08 s vs 0.42 s），根因是 Decoding KV 主導偏差為 Value Cosine（0.800）而非 Value Norm（0.926）`[RelayCaching, §3.1, §5.2–5.3, Table 1, Fig. 8, p.3, 7]`。
- **張力 2（同架構重算 vs. 跨尺寸線性映射）**：DroidSpeak 不假設線性但限同架構（1.7–2.6×）；NVIDIA 閉式 Ridge 突破跨尺寸且最高快 25×，但 Tier 2 配對驟降至 41.6–44.2%，須改訓練 MLP 救回 92–96% `[DroidSpeak, §3.1, §5.2, p.4, 10; Cross-Model KV, §4.2, §4.4, Table 1, 3, p.6–7]`。
- **張力 3（重建 $R^2$ 失靈 vs. 注意力子空間保真度）**：校準集 $R_K^2$ 跨配對相關性為 **$r = -0.20$**，Attention-Output Cosine 達 **$r = +0.57$**，證明誤差「落點（K-concentration）」遠比平均大小重要 `[Cross-Model KV, §4.5, Table 4, p.7–8]`。
- **張力 4（遠端卸載交叉點與截斷反噬）**：S3 Express 遠端載入在 Company C 降 22–32% TTFT，但 32 Gbps 低頻寬下須 >256K tokens 才快過 Prefill（64–128 Gbps 全勝）；滑動視窗截斷則讓 Company F 命中率從 **~85% 跌至 ~45%** `[LMCache, §8.7, §9, Fig. 15, p.14–15]`。
