# Tail latency: Relay-BP vs BP-OSD vs ML router vs agreement gate

All four decoders run on the **same 1,000 fresh X/Z pairs** per noise level (seeds 1000 for X and 1001 for Z, the same shots as the `ml-router` branch's `evaluate_router.py`). The decoder order is shuffled per shot, with one single-threaded process per noise level. The two noise levels ran at the same time on an 8-core Apple Silicon Mac (22 Nov 2026).

- Gate: `experiments/gate.py`, using `settings_for(p)` from `results/adaptive_selected.json`. That is K = 50 with the R5 referee at both levels.
- Router: `RoutedDecoder` from the `ml-router` branch at t = 0.7. At p = 0.004 it uses that branch's committed models (`result/route_{X,Z}_p0.004_safe_logistic.joblib`); at p = 0.005, routers retrained on 3,000 recorded shots per basis (seeds 5 and 6).

| p | decoder | failed pairs | LER / cycle | mean | p50 | p90 | p99 | max |
|---|---|---|---|---|---|---|---|---|
| 0.004 | Relay-BP | 13 | 1.09e-3 | 325 ms | 98 ms | 615 ms | 4.82 s | 6.15 s |
| 0.004 | BP-OSD | 53 | 4.53e-3 | 322 ms | 340 ms | 733 ms | 0.97 s | 2.44 s |
| 0.004 | ML router | 40 | 3.40e-3 | 246 ms | 103 ms | 499 ms | 2.96 s | 5.61 s |
| 0.004 | agreement gate | 11 | 9.21e-4 | 213 ms | 14 ms | 276 ms | 5.56 s | 7.30 s |
| 0.005 | Relay-BP | 95 | 8.28e-3 | 1.39 s | 388 ms | 4.79 s | 7.80 s | 10.57 s |
| 0.005 | BP-OSD | 272 | 2.61e-2 | 554 ms | 540 ms | 882 ms | 1.29 s | 1.90 s |
| 0.005 | ML router | 159 | 1.43e-2 | 978 ms | 420 ms | 3.13 s | 5.53 s | 9.49 s |
| 0.005 | agreement gate | 95 | 8.28e-3 | 1.26 s | 131 ms | 5.54 s | 7.81 s | 11.51 s |

Bootstrap 95% ranges for p99 at p = 0.004: Relay-BP 4.7–5.2 s, BP-OSD 0.93–1.1 s, router **1.2–4.7 s**, gate 4.2–5.9 s. The router's p99 sits on a cliff: about 1% of pairs still reach slow Relay-BP shots.

Absolute times are inflated by running four decoders per shot in one harness (Relay-BP's mean at p = 0.004 was 175–195 ms in standalone runs). Compare decoders within a noise level, not against other runs.

## Files

| file | contents |
|---|---|
| `tail_latency.png`, `.pdf` | survival curves (fraction of pairs at least this slow), one panel per p |
| `tail_p0.004.npz`, `tail_p0.005.npz` | per-shot seconds and failures, shape (1000, 2) for X and Z, per decoder; gate path per shot |
| `tail_p0.004.txt`, `tail_p0.005.txt` | run logs and summary lines |
| `tail_bench.py` | the benchmark |
| `plot_tail.py` | the chart |

## Reproduce

`tail_bench.py` imports `circuit`, `decoders`, `fast_bp` and `evaluate_router` from the `ml-router` branch's `src/`, and `gate` from `experiments/`. Put both on `PYTHONPATH` and add scikit-learn and joblib to the kit environment.

```bash
export OMP_NUM_THREADS=1 RAYON_NUM_THREADS=1 PYTHONPATH=<ml-router>/src:experiments
python results/tail_latency/tail_bench.py --p 0.004 --models X.joblib Z.joblib \
    --table results/adaptive_selected.json --out tail_p0.004.npz
python results/tail_latency/plot_tail.py tail_latency.png tail_p0.004.npz tail_p0.005.npz
```
