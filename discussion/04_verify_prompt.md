# Round 4: pre-register the verification of the agreement gate (BEFORE seeing new results)

The user asked us to double-check that the agreement gate is genuinely effective across shot counts and noise levels.
Recap of round 3: on 1500 pairs at p=0.004 (CPU-contended run), agreement gate (2 seeds of fast Relay-BP,
stop_nconv=1/num_sets=50; escalate on disagreement or no-solution) had 16-17 pair failures vs Relay-BP 21, mean
0.6-0.7x, median 0.3x of Relay-BP; 1.4% escalated; 3/2958 agreed-but-wrong. p99 not improved.

## Now running (fresh seeds, idle machine, 8 workers, every decoder on every shot; experiments/agree.py)
- p=0.004, 3000 pairs, seed 101
- p=0.003, 8000 pairs, seed 201 (Relay-BP fails ~1/1000 pairs here, so more shots)
- p=0.005, 3000 pairs, seed 301
- p=0.004, 3000 pairs, seed 401 (replication)
Stored per shot and basis: correct, seconds, success, iterations, 12-bit logical prediction, for
fast_s0, fast_s1, relay_nconv2, relay (kit settings).

## Planned report (experiments/agree_report.py, to be written)
Per run: pair failures + LER/cycle with exact (Clopper-Pearson) 95% CI; mean/p50/p95/p99/max pair time;
policies: Relay-BP, BP-OSD-free set (relay_fast alone, fast + escalate-if-no-solution [1 seed], agreement->relay,
agreement->nconv2), serial (sum of the two fast runs) and parallel (max) timing; escalation rate;
paired discordance vs Relay-BP (gate wrong & relay right, gate right & relay wrong) with exact McNemar test;
agreed-but-wrong count split by "both stopped in the shared deterministic first leg (iterations <= 80)" vs later;
seed check: fraction of hard shots where the two seeds' iterations differ; shot-count stability: metrics on
first 1000 / 2000 / all pairs; the two p=0.004 seeds compared; a plot of LER vs mean latency per p.

## Questions (under ~350 words)
1. What should count as "effective" (pre-registered pass/fail criteria) for accuracy and for latency?
2. What else must the report include or check so we don't fool ourselves? Anything wrong in the plan?
3. Any confound in the setup (timing, seeds, pairing, shared first leg, chunking) we should fix now?
