# 28 — Emma's ML router at p = 0.003 / 0.004 / 0.005, 10,000 pairs each

Code: `ml_router/` (unchanged from branch `ml-router`), run through `experiments/router_compare.py` on 8 workers,
t = 0.7. Models: her own for p = 0.004; trained with her exact recipe (3000 shots per basis, seeds 1/2, label "safe",
logistic) for 0.003 and 0.005. Test seeds 5030/5040/5050 (X) and +1 (Z). Full output: `results/router_eval.txt`.

| p | decoder | failed pairs | LER / cycle | mean ms | p90 ms | p99 ms |
|---|---|---|---|---|---|---|
| 0.003 | BP-OSD | 55 | 4.59e-4 | 99 | 329 | 597 |
| | Relay-BP | 5 | 4.17e-5 | 60 | 87 | 419 |
| | ML router | 41 | 3.42e-4 | 61 | 137 | 391 |
| 0.004 | BP-OSD | 545 | 4.66e-3 | 273 | 638 | 804 |
| | Relay-BP | 94 | 7.87e-4 | 262 | 435 | 4244 |
| | ML router | 351 | 2.97e-3 | 210 | 429 | 2182 |
| 0.005 | BP-OSD | 2418 | 2.28e-2 | 534 | 842 | 1043 |
| | Relay-BP | 827 | 7.17e-3 | 1215 | 4616 | 6813 |
| | ML router | 1413 | 1.26e-2 | 836 | 2373 | 5400 |

- Her p = 0.004 README claims hold at 10× the shots: the router is the fastest on average (210 ms vs 262 and 273) and
  halves Relay-BP's p99 (0.51×), at about 3.8× Relay-BP's logical error rate and 0.64× BP-OSD's.
- p = 0.005: 0.69× Relay-BP's mean time and 0.79× its p99 (latency PASS), at 1.7× its error rate.
- p = 0.003: no gain. BP-OSD is slower than Relay-BP here, so routing to it costs accuracy and saves no time.
- The accuracy cost comes from the decodes sent to BP-OSD (40 / 317 / 1087 of the router's failed basis decodes).
  The fast-BP first stage never failed at any p.
- Versus our gate (earlier runs, same seeds, fewer pairs): the gate keeps Relay-BP's accuracy (7.4e-4 at 0.004,
  7.6e-3 at 0.005) and is faster on average at 0.003 / 0.004 (0.38× / 0.73× Relay-BP), but does not cut p99.
  The router cuts p99 by trading accuracy. They are different points on the speed / accuracy trade-off.
