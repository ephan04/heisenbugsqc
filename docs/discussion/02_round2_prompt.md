# Round 2: data is in. Critique and converge.

All three round-1 proposals are in discussion/01_claude.md, 01_gpt.md, 01_gemini.md (summarised here):
all three said: build 2 tiers first (light BP -> Relay-BP), whole-shot accept/reject (no partial commits), small
logistic/tree gate, defer loss, judge on paired LER + mean/p99 latency, not router accuracy.
Differences: Gemini proposed accept only if converged AND correction weight <= 4; GPT proposed BP-20; Claude BP-80.

## Measured: p=0.004, 4000 X/Z pairs (8000 decodes), every tier run on every shot, 10 workers
Tiers: bp = BP-80 min-sum; lsd = BP-LSD order 0; bposd = kit BP-OSD-CS10; relay_fast = Relay-BP with stop_nconv=1,
num_sets=50; relay = kit Relay-BP (stop_nconv=5, 300 legs). Times are per pair (X+Z). Test half = 2000 pairs
(ML router trained on the other half).

- BP-80 converged on 61.5% of shots; **wrong when converged: 0 of 4923**.
- Correction weight of converged BP: **median 45; fraction <= 4: 0.0%** (the weight<=4 rule escalates everything).

TEST HALF:
```
policy                              pair fails  LER/cycle   mean ms  p50   p99 ms
bposd alone                          109/2000   4.66e-03    302     328    896
relay alone                           19/2000   7.95e-04    266      88   4007
relay_fast alone                      53/2000   2.24e-03     53      12    728
lsd alone                            217/2000   9.53e-03     41      34    158
BP-80 conv-gate -> relay              19/2000   7.95e-04    254      74   3994   (38% escalated)
BP-80 conv-gate -> relay_fast         52/2000   2.19e-03     76      38    763
3-tier ML(thr .5): conv->accept, else LR picks relay_fast vs relay (8% to relay)
                                      23/2000   9.63e-04    167      39   3778
3-tier ML(thr .2) (33% to relay)      20/2000   8.37e-04    243      66   3989
3-tier ORACLE router                  16/2000   6.69e-04    128      38   3115
```
Observations (Claude): (1) gating easy shots barely helps mean latency: relay is already fast on easy shots (p50 88 ms);
the mean is dominated by the ~38% hard shots and the tail. (2) The real lever is on the HARD shots: oracle says sending
the right hard shots to relay_fast halves mean latency at equal (even lower) LER. (3) Our BP-80-feature router is weak
(167 ms with +20% LER, or no speedup). (4) LSD is useless here (worse than relay_fast and slower).

Idea from Claude for next step: route on the *medium tier's own output* (confidence-based escalation): run relay_fast,
then a model on its diagnostics (solution weight/cost, legs/iterations used, converged, BP-80 features) decides whether to
also run full relay. Cost is relay_fast + sometimes relay.

## Questions (short, under ~500 words, concrete)
1. Do you agree with the observations? Anything wrong or misleading in this evaluation?
2. Best next step for the prototype in the next hour: the escalation idea above, something else? What features?
3. What should the final pitch/plot be given these numbers?
