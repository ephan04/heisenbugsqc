# Heisenbugs QC: noise-adaptive agreement gate for the Gross code (MidQWest 2026, Challenge 1)

A hierarchical decoder for the [[144,12,12]] Gross code, built on the kit's Relay-BP. It has no ML yet: the noise level is given, and it picks the settings.

- `challenge-1-ml-decoder-kit/`: the challenge kit, unmodified. `kit` links to it, and the experiments import from `kit/`.
- `experiments/gate.py`: the gate as a decoder. A fast Relay-BP run with seed 0 is accepted if it solves the shot in its first leg. A second seed must agree otherwise. Shots with no solution or a disagreement go to a referee (the kit's Relay-BP).
- `experiments/adaptive_*.py`: stage 1 discovery, settings selection, stage 2 confirmation, and the verdicts report.
- `results/`: outputs (`adaptive_confirm.txt` holds the confirmed verdicts).
- `discussion/`: the Claude / GPT / Gemini discussion rounds and pre-registrations. Start with `13_noise_adaptive_conclusion.md`, then `16_ml_bposd_conclusion.md`.

Setup: `uv venv --python 3.12 .venv && uv pip install -r challenge-1-ml-decoder-kit/requirements.txt matplotlib`

```bash
python experiments/adaptive_collect.py --p 0.004 --shots 6000 --seed 1040 --out data/adapt_p0.004.npz
python experiments/adaptive_select.py data/adapt_p*.npz          # freezes results/adaptive_selected.json
python experiments/adaptive_confirm.py --p 0.004 --shots 6000 --seed 2040 --out data/confirm_p0.004.npz
python experiments/adaptive_report.py data/confirm_p*.npz
```
The `data/` files are not committed. The seeds above regenerate them.
