# Slide 11：別只看單篇結論！四大跨文獻張力與前提邊界

- **頁碼**：11 / 12
- **來源卡片**：`cards/card-08-tensions.md`
- **Wiki 出處**：`wiki/syntheses/conflicts-and-tensions.md`

## 核心內容
- **張力 1｜靜態 RAG vs. 動態 MAS（CacheBlend vs. RelayCaching）**：
  - CacheBlend 在靜態 RAG 品質損 **≤ 0.02**；但 RelayCaching 將其移至動態多代理時 GSM8K 跌至 **74.73–77.56%** 且 12K 呈線性膨脹（1.08 s vs 0.42 s），因解碼重用主導偏差為 **Value Cosine（0.800）** 而非 Value Norm（0.926）`[CacheBlend, §7.2, p.12; RelayCaching, §3.1, §5.2–5.3, Table 1, Fig. 8, p.3, 7]`。
- **張力 2｜同架構重算 vs. 跨尺寸映射（DroidSpeak vs. NVIDIA）**：
  - DroidSpeak 不假設線性但限同架構（1.7–2.6×）；NVIDIA Ridge 跨尺寸最高快 **25×**，但在 Ministral Tier 2 五基準平均跌至 **41.6–44.2%**，須改訓練 MLP 救回 HellaSwag 至 92–96% `[DroidSpeak, §3.1, §5.2, p.4, 10; Cross-Model KV, §4.2, §4.4, Table 1, 3, p.6–7]`。
- **張力 3｜重建誤差 $R^2$ 失靈 vs. 注意力子空間保真度**：
  - $R^2$ 適合單配對挑源層，跨配對卻失靈（$r = -0.20$）；須改看 Attention-Output Cosine（$r = +0.57$）與 K-concentration `[Cross-Model KV, §4.5, Table 4, p.7–8]`。
- **張力 4｜遠端卸載交叉點與截斷反噬（LMCache）**：
  - 高速物件儲存降 **22–32% TTFT**，但 32 Gbps 低頻寬下須 >**256K tokens** 才勝過重算；滑動視窗截斷則讓命中率從 **~85%** 腰斬至 **~45%** `[LMCache, §8.7, §9, Fig. 15, p.14–15]`。
- **頁尾出處**：`wiki/syntheses/conflicts-and-tensions.md`｜`[CacheBlend, §7.2; DroidSpeak, §3.1, §5.2; LMCache, §8.7, §9; RelayCaching, §3.1, §5.2–5.3; Cross-Model KV, §4.2–4.5]`
