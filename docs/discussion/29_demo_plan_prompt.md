# 29 — Plan a quick LIVE demo of our decoder (plan only, do not build)

We are a hackathon team (MidQWest 2026, Infleqtion Challenge 1: decoding the [[144,12,12]] Gross code).
We want a short live demo, on stage, of OUR decoder: the "agreement gate" (no ML; a teammate's ML router is NOT part
of this demo). When the run finishes it must show a figure comparing the data the organisers provided with our output,
on SPEED and ACCURACY, ideally 2 panels per run. If possible the graph should update live while decoding runs.

## What we have
- `experiments/gate.py`: `AgreementGate(H, L, priors, K=10, referee="R5").decode(syndrome)`. It runs Relay-BP with seed 0
  for a capped number of iterations; accepts if solved within the first 80 iterations; otherwise runs seed 1 and
  accepts if the logical predictions agree; otherwise falls back to the full kit Relay-BP ("referee").
  `.last_path` is one of first_leg / agreed / no_solution / disagreed.
- Kit (`kit/`): `circuit.py` (load_circuit, dem_matrices, detector_ids, sample), `decoders.py` (bposd_decoder,
  relay_decoder, score, print_score), `baseline.py --p 0.004 --shots 10000` (multiprocessing pool, 8 cores).
  Decoding is per basis: X memory and Z memory shot k form a pair; the pair fails if either fails.
  LER per cycle = 1 - (1 - P_pair_fail)^(1/12).
- The organisers' reference table (kit README, 10,000 pairs per p, on their 8-core machine):

| p | decoder | failures X, Z | rate per cycle | mean time per basis decode |
|---|---|---|---|---|
| 0.003 | BP-OSD | 26, 30 | 4.7e-4 ± 0.6e-4 | 0.14 s |
| 0.003 | Relay-BP | 3, 2 | 4.2e-5 ± 1.9e-5 | 0.10 s |
| 0.004 | BP-OSD | 253, 269 | 4.4e-3 ± 0.2e-3 | 0.33 s |
| 0.004 | Relay-BP | 45, 60 | 8.7e-4 ± 0.9e-4 | 0.38 s |
| 0.005 | BP-OSD | 1302, 1286 | 2.3e-2 ± 0.05e-2 | 0.59 s |
| 0.005 | Relay-BP | 411, 414 | 6.9e-3 ± 0.2e-3 | 1.7 s |

- Our measured results on our laptop (Apple Silicon, 8 workers), same-shot comparisons:
  - gate failures: 0.003: 7 of 10k pairs (Relay-BP 5); 0.004: 53 of 6k (Relay-BP 55); 0.005: 262 of 3k (Relay-BP 262).
  - mean time per pair vs Relay-BP: 0.38x / 0.73x / 0.87x. p99: 0.80x / 1.03x / 0.97x.
  - mean ms per PAIR (X + Z): gate 23 / 191 / 1164; Relay-BP 60 / 262 / 1335; BP-OSD 99 / 282 / 578.
  - throughput of the gate on 8 cores: about 360 / 42 / 7 pairs per second.
  - building decoders (DEM extraction + Relay-BP/BP-OSD construction) takes a few seconds per basis per process.
- Important caveats: (1) the organisers' times are from THEIR machine, so speed must be compared to Relay-BP/BP-OSD run
  live on OUR machine (or to ratios), not to their raw seconds; (2) at small shot counts the accuracy error bars are huge,
  especially at p = 0.003 (5 failures in 10k pairs); (3) Python, CPU only, no GPU.
- Python env has stim, ldpc, relay_bp, numpy, scipy, matplotlib, scikit-learn. A browser is available. Optional libs can be
  pip-installed (e.g. plotly/dash, streamlit, bokeh) but fewer moving parts is better on stage.

## Questions — answer concisely, as a concrete plan
1. Demo length and content: which p values, how many shots, and which decoders run live (gate only vs gate + live
   Relay-BP/BP-OSD on the same shots)? It must finish in ~1-3 minutes on the laptop. Give numbers.
2. What exactly the final figure shows: the 2 panels (accuracy, speed), axes, what is "their data" vs "ours", error bars,
   how to handle the machine-speed difference honestly.
3. The live graph: technology (matplotlib interactive window, a local web page, a terminal UI ...), how results stream
   from the worker pool to the plot (e.g. imap_unordered), update rate, what the audience sees while it runs.
4. Risk management on stage: warm-up/decoder build time, a pre-recorded fallback, fixed seeds, what if it is slow.
5. A short script of what the presenter says while it runs (3-5 lines).
Keep it under ~500 words. Do not run tools.
