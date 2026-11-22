# Round 3: escalation results (negative-ish). Final recommendation.

Bugs GPT flagged in escalate.py were fixed (mask shapes; unsuccessful fast runs now always escalate; edge cases).
Data: p=0.004, 3000 pairs, split 50/25/25 train/val/test by pair; thresholds picked on validation as the fastest
policy with val pair failures <= Relay-BP's. TEST (750 pairs):
```
BP-OSD (kit)                   fails 46/750  LER/cycle 5.26e-03  mean 381 ms  p50 425  p99 1321
Relay-BP (kit)                 fails 12/750  LER/cycle 1.34e-03  mean 361 ms  p50 112  p99 5630
Relay-fast alone               fails 25/750  LER/cycle 2.82e-03  mean  71 ms  p50  16  p99 1035
rule: escalate if no solution  fails 16/750                      mean 168 ms           p99 6380
ML gate (LR on rf_* diag.)     fails 17/750                      mean 265 ms           p99 6397  (4.7% escalated)
rule: iters<=K & cost<=W       fails 13/750                      mean 312 ms           p99 6573
oracle gate                    fails  8/750                      mean 128 ms           p99 2114
```
Reading (Claude): the single-run diagnostics of relay_fast cannot tell when its (valid) solution is in the wrong
logical class; validation has ~12 failures so threshold selection is noisy. Oracle headroom is ~2.8x.

Now running (results soon): **agreement gate** — two relay_fast runs with seeds 0 and 1; if both succeed and predict the
same logical observables, accept; else run full Relay-BP (or Relay-BP stop_nconv=2). No learned parameters.

Questions (under ~350 words):
1. Is the agreement gate the right next idea? Pitfalls (e.g. both legs share the same deterministic first leg, so
   easy shots always "agree" — is that a problem)?
2. Where should ML go in the final pipeline so it is *genuinely* useful rather than decorative? One concrete proposal.
3. One-paragraph final recommendation for the team for the remaining hackathon time.
