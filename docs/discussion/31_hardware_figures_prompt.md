# 31 — Hardware facts and figures: fact-check and figure proposals (do not run tools)

We (hackathon team, Infleqtion Challenge 1, Gross code decoding) want to present the HARDWARE FACTS of our decoder
(the "agreement gate": Relay-BP seed 0 capped at 80+60K iterations; accept if solved in first 80; else run seed 1 and
accept if logicals agree; else fall back to full kit Relay-BP) and then a set of FIGURES comparing the organisers'
data with ours on speed and accuracy. Below: our consolidated metrics and the hardware probe.

Draft hardware facts (please check each against the data and flag anything wrong or overclaimed):
1. Everything runs on a MacBook Air (Apple M5, 10 cores = 4 performance + 6 efficiency, 16 GB), CPU only, no GPU.
   8 worker processes, so some work runs on efficiency cores.
2. One worker process holds ~96 MB after building the decoding problem (H is 936 x 8784, 30,672 nonzeros; built in 0.7 s
   per basis). Relay-BP adds ~1 MB, the gate ~5.5 MB (several Relay-BP instances), BP-OSD ~62 MB.
3. Building a decoder takes 5-20 ms once the matrices exist.
4. Throughput on 8 workers (estimated as 8 / mean time per pair): gate ~365 / 42 / 7 pairs per second at p = 0.003 /
   0.004 / 0.005; Relay-BP ~140 / 31 / 6; BP-OSD ~85 / 28 / 14.
5. Our laptop runs Relay-BP about 1.3-1.8x faster per pair than the organisers' machine (57 vs 100 ms, 262 vs 380,
   1335 vs 1700), so raw times must not be compared across machines; we compare ratios on the same shots.
6. The gate needs no training, no GPU, no extra data; its only extra state is a second Relay-BP seed.
7. Mean decode time per pair vs Relay-BP: 0.38 / 0.73 / 0.87; p99: 0.76 / 1.03 / 0.97.

Then propose 4-6 figures (title, what each axis shows, which rows, what message, honest caveat). The user asked for
"the data that they provided and our output, comparing speed and accuracy". Keep answer under 450 words.

## Metrics (results/all_metrics.md). Note: the organisers' "failed pairs" column is X failures + Z failures (an upper
bound on failed pairs); use their rate per cycle.
| p | decoder | source | pairs | failed pairs | LER / cycle | mean ms/pair | p90 | p99 | pairs/s (8 workers) |
|---|---|---|---|---|---|---|---|---|---|
| 0.003 | BP-OSD | organisers (kit README) | 10000 | 56 | 4.70e-04 | 140 |  |  |  |
| 0.003 | BP-OSD | ours, same shots | 10000 | 55 | 4.59e-04 | 94 | 312 | 565 | 85 |
| 0.003 | ML router (Emma, t=0.7) | ours, 10k pairs | 10000 | 41 | 3.42e-04 | 61 | 137 | 391 |  |
| 0.003 | Relay-BP | organisers (kit README) | 10000 | 5 | 4.20e-05 | 100 |  |  |  |
| 0.003 | Relay-BP | ours, 100k pairs | 100000 | 74 | 6.17e-05 | 77 |  |  |  |
| 0.003 | Relay-BP | ours, same shots | 10000 | 5 | 4.17e-05 | 57 | 83 | 404 | 140 |
| 0.003 | agreement gate | ours, 100k pairs | 100000 | 86 | 7.17e-05 | 30 |  |  |  |
| 0.003 | agreement gate | ours, same shots | 10000 | 7 | 5.84e-05 | 22 | 13 | 307 | 365 |
| 0.004 | BP-OSD | organisers (kit README) | 10000 | 522 | 4.40e-03 | 330 |  |  |  |
| 0.004 | BP-OSD | ours, same shots | 6000 | 336 | 4.79e-03 | 282 | 649 | 849 | 28 |
| 0.004 | ML router (Emma, t=0.7) | ours, 10k pairs | 10000 | 351 | 2.97e-03 | 210 | 429 | 2182 |  |
| 0.004 | Relay-BP | organisers (kit README) | 10000 | 105 | 8.70e-04 | 380 |  |  |  |
| 0.004 | Relay-BP | ours, same shots | 6000 | 55 | 7.67e-04 | 262 | 436 | 4279 | 31 |
| 0.004 | agreement gate | ours, same shots | 6000 | 53 | 7.39e-04 | 191 | 236 | 4415 | 42 |
| 0.005 | BP-OSD | organisers (kit README) | 10000 | 2588 | 2.30e-02 | 590 |  |  |  |
| 0.005 | BP-OSD | ours, same shots | 3000 | 726 | 2.28e-02 | 578 | 909 | 1138 | 14 |
| 0.005 | ML router (Emma, t=0.7) | ours, 10k pairs | 10000 | 1413 | 1.26e-02 | 836 | 2373 | 5400 |  |
| 0.005 | Relay-BP | organisers (kit README) | 10000 | 825 | 6.90e-03 | 1700 |  |  |  |
| 0.005 | Relay-BP | ours, same shots | 3000 | 262 | 7.59e-03 | 1335 | 5038 | 7835 | 6 |
| 0.005 | agreement gate | ours, same shots | 3000 | 262 | 7.59e-03 | 1164 | 5108 | 7603 | 7 |

## Gate vs Relay-BP verdicts (same shots)
0.003 only gate 3 only relay 1 ratio_upper 1.99 FAIL {'mean': [0.38, 0.42], 'p90': [0.16, 0.16], 'p99': [0.76, 0.99]} PASS
0.004 only gate 19 only relay 21 ratio_upper 1.29 INCONCLUSIVE {'mean': [0.73, 0.76], 'p90': [0.54, 0.63], 'p99': [1.03, 1.09]} FAIL
0.005 only gate 61 only relay 61 ratio_upper 1.11 PASS {'mean': [0.87, 0.89], 'p90': [1.01, 1.02], 'p99': [0.97, 1.05]} FAIL
100k p=0.003: gate 86 relay 74 INCONCLUSIVE paths {'first_leg': 0.9653, 'agreed': 0.0288, 'no_solution': 0.0035, 'disagreed': 0.0023}
## Teammate tail-latency run (1000 pairs, 1 process each, OLD gate setting K=50)
results/tail_latency/tail_p0.004.txt:relay   fails [ 3 10] pairs   13 LER 1.09e-03  mean   325.3  p50    98.3  p90   614.6  p99    4824  max    6149 ms
results/tail_latency/tail_p0.004.txt:bposd   fails [27 26] pairs   53 LER 4.53e-03  mean   321.9  p50   340.2  p90   733.1  p99     971  max    2439 ms
results/tail_latency/tail_p0.004.txt:router  fails [18 22] pairs   40 LER 3.40e-03  mean   246.4  p50   103.4  p90   498.5  p99    2959  max    5608 ms
results/tail_latency/tail_p0.004.txt:gate    fails [2 9] pairs   11 LER 9.21e-04  mean   212.6  p50    13.6  p90   276.0  p99    5563  max    7296 ms
results/tail_latency/tail_p0.005.txt:relay   fails [50 46] pairs   95 LER 8.28e-03  mean  1385.7  p50   387.8  p90  4787.8  p99    7804  max   10566 ms
results/tail_latency/tail_p0.005.txt:bposd   fails [143 150] pairs  272 LER 2.61e-02  mean   553.9  p50   540.2  p90   881.5  p99    1288  max    1897 ms
results/tail_latency/tail_p0.005.txt:router  fails [82 84] pairs  159 LER 1.43e-02  mean   978.2  p50   420.4  p90  3131.0  p99    5530  max    9485 ms
results/tail_latency/tail_p0.005.txt:gate    fails [52 44] pairs   95 LER 8.28e-03  mean  1264.7  p50   131.4  p90  5543.5  p99    7808  max   11510 ms
