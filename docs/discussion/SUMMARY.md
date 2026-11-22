# Three-agent discussion: summary (Claude, GPT via Codex, Gemini via agy)

> **Superseded by `07_conclusion.md`.** The verification on 17,000 fresh pairs did not confirm that the gate is more accurate than Relay-BP at p=0.004; it *matches* Relay-BP. The speed-up holds at p ≤ 0.004 but not at p=0.005. The round-3 numbers below came from one CPU-contended run.

Files: `00_brief.md` → round 1 (`01_*`) → data → round 2 (`02_*`) → round 3 (`03_*`).

## What we agreed on
- Whole-shot accept/escalate, no "commit confident bits" partial decoding (BB checks are long-range; frozen bits can lock a wrong logical class).
- Judge every policy on paired X/Z pair failures and LER per cycle on the same shots, with mean, p50 and p99 latency. Router accuracy doesn't count.
- Defer qubit loss until the core result is solid.
- Choose thresholds on validation shots only; test once; failures are rare, so small samples mislead.

## What the data showed (p = 0.004)
| Finding | Evidence |
|---|---|
| Converged BP-80 is essentially always right | 0 wrong out of 4,923 converged shots (95% upper bound ≈ 0.06%) |
| "Accept if correction weight ≤ 4" is wrong | Median weight of a correct correction is 45; the rule escalates 100% |
| Skipping easy shots barely saves time | BP gate → Relay-BP: 254 ms vs 266 ms. Cost is in the hard ~38% and the tail |
| BP-LSD is a poor middle tier for this goal | 9.5e-3 LER, worse than BP-OSD |
| Single-run confidence gates don't work | Best rule: 13 vs 12 fails, only ~14% faster; ML gate +5 fails |
| Oracle headroom is large | Perfect gate: 8 fails at 128 ms vs Relay-BP 12 fails at 361 ms |
| **Agreement gate works best** | 2 seeds of fast Relay-BP; escalate only on disagreement (1.4%): **16–17 fails vs Relay-BP 21** on 1,500 pairs, mean ≈ 0.6–0.7× and median ≈ 0.3× of Relay-BP |

Caveats: the agreement run was CPU-contended (absolute times ≈ 2.5× inflated for every decoder alike). The p99 tail is not improved. Only p = 0.004 has been tested so far.

## Final recommendation (consensus)
1. Main pipeline: **fast Relay-BP × 2 seeds → agree? accept : full Relay-BP (or stop_nconv=2)**. It has no learned parameters, so every shot is a test shot.
2. Rerun on an idle machine at p = 0.003, 0.004, 0.005, with ≥ 3,000 pairs each and fresh seeds. Plot LER vs mean latency and p99 against BP-OSD and Relay-BP, and include the oracle as a reference.
3. Put ML where it adds measurable value, not decoration. Candidates:
   - GPT: a model that picks the second run's perturbation schedule to maximise disagreement on wrong shots.
   - Gemini: a pre-decode hardness classifier that sends obviously hard shots straight to full Relay-BP, skipping the doomed fast runs.
   - Claude: also run the two fast seeds in parallel on 2 cores (latency = max, not sum).
4. If ML doesn't beat the fixed rule on held-out data, say so, and present the oracle headroom as the target.
