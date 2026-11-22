# Experiments

Every script runs from the **repository root**, for example `python experiments/bposd_compare_report.py data/compare_p*.npz`.
The scripts read shots and per-shot outcomes from `data/` and write summaries to `results/`.
Each script's first lines give its exact command.

The decoder itself is [`gate.py`](gate.py). Everything else is a study of it, listed below in the order we ran them.
The "plan" and "conclusion" links go to the team discussion in [`docs/discussion/`](../docs/discussion/).

## 1. Finding an idea (p = 0.004)

| Script | What it does |
|---|---|
| `probe_bp.py` | How often short BP converges, and whether it's right when it does |
| `collect.py`, `analyze.py` | Run every candidate decoder on the same shots and replay routing policies offline |
| `escalate.py` | Fast Relay-BP first, then a learned rule decides whether to escalate (did not work) |
| `agree.py`, `agree_report.py`, `agree_plot.py` | **The agreement gate**: two cheap Relay-BP runs with different seeds; escalate only if they disagree |
| `lean_gate.py`, `high_noise.py` | Exploratory variants of the gate |

Plan: `05_preregistration.md`. Conclusion: `07_conclusion.md`, `SUMMARY.md`.

## 2. Settings per noise level (p = 0.003 to 0.006)

| Script | What it does |
|---|---|
| `adaptive_collect.py` | Stage 1: per-shot data for 12 gate settings (restart cap K, referee R5 / R2 / R1) |
| `adaptive_select.py` | Picks one setting per noise level and freezes it (`results/adaptive_selected.json`) |
| `adaptive_confirm.py`, `adaptive_report.py` | Stage 2: the frozen settings vs Relay-BP on fresh shots, with pass/fail verdicts |

Plan: `09_noise_adaptive_prereg.md`, `12_addendum_prereg.md`. Conclusion: `13_noise_adaptive_conclusion.md`.

## 3. Detecting the noise level

| Script | What it does |
|---|---|
| `noise_estimate.py` | Can the alarm count alone tell the noise level? (Yes, within about 3%) |
| `noise_ml.py` | A small neural network vs simple alarm counting (no better) |
| `estimated_priors.py`, `estimated_priors_report.py` | Decoders built from the estimated noise level instead of the true one (partial run) |

Plan: `08_noise_adaptive_prompt.md`, `27_estimated_priors_prereg.md`. Conclusion: `16_ml_bposd_conclusion.md`.

## 4. Headline comparison: gate vs BP-OSD vs Relay-BP

| Script | What it does |
|---|---|
| `bposd_compare.py`, `bposd_compare_report.py` | All decoders on the same shots at p = 0.003 / 0.004 / 0.005 (10k / 6k / 3k pairs), plus a 100k-pair run at 0.003 |

Plan: `14_bposd_compare_prereg.md`, `15_p0003_large_prereg.md`. Conclusion: `16_ml_bposd_conclusion.md`.

## 5. Can ML spot the hard shots?

| Script | What it does |
|---|---|
| `hardshot.py` | Models predict which shots need the slow fallback; the ceiling, then real models |

Plan: `19_hardshot_design_prompt.md`. Conclusion: `21_hardshot_conclusion.md` (no useful time saving).

## 6. Emma's ML router (from branch `ml-router`)

| Script | What it does |
|---|---|
| `router_compare.py`, `router_compare_report.py` | Her router vs our decoders at p = 0.003 |
| `router_eval_report.py` | Her router vs BP-OSD and Relay-BP at all three noise levels, 10k pairs each |

Her code is in [`ml_router/`](../ml_router/). Plan: `25_router_compare_prereg.md`. Conclusions: `26_router_compare_result.md`, `28_router_eval_10k.md`.

## 7. Hardware cost and figures

| Script | What it does |
|---|---|
| `hardware_probe.py` | Memory and build time of each decoder |
| `metrics_summary.py` | Every headline number in one table (`results/all_metrics.md`) |
| `hardware_figures.py` | The five figures in [`figures/`](../figures/) |
| `report_figures.py` | The figures in the PDF report |

Notes: `31_*`, `32_hardware_figures.md`.
