# Round 5: verification results are in. Interpret them honestly against the pre-registration.

Pre-registration: discussion/05_preregistration.md (accuracy: paired failure ratio one-sided 95% upper < 1.2 = PASS,
point > 1.2 = FAIL, else INCONCLUSIVE; latency: paired-bootstrap 95% upper of mean ratio <= 0.8).
Seed check done: Relay-BP's RNG state persists across decodes in one decoder object (verified), seeds 0/1 give
different searches (logical vectors differ on 64-344 hard shots per run) -> diversity is real; results depend on
chunking but that is not a bias.

Full report (results/agree_report.txt):

=== data/agree_p0.003_s201.npz: p=0.003, 8000 pairs, seed 201 ===
policy                                fails           LER/cycle [95% CI]    esc    mean    p50    p95     p99     max  (ms per pair)
Relay-BP (kit)                           10  1.04e-04 [5.0e-05, 1.9e-04]   0.0%    70.3   42.4    147     523    4524
fast Relay-BP alone                      19  1.98e-04 [1.2e-04, 3.1e-04]   0.0%    13.4    7.2     34     122     800
1 seed, escalate if no solution          14  1.46e-04 [8.0e-05, 2.4e-04]   0.1%    17.9    7.2     34     122    5299
AGREEMENT -> Relay-BP (primary)           9  9.38e-05 [4.3e-05, 1.8e-04]   0.2%    34.1   14.5     74     255    6068
agreement -> Relay-BP, parallel*          9  9.38e-05 [4.3e-05, 1.8e-04]   0.2%    22.6    7.4     44     178    5299
agreement -> nconv2                       6  6.25e-05 [2.3e-05, 1.4e-04]   0.2%    32.5   14.5     74     255    6310

primary vs Relay-BP: failure ratio 0.90 (one-sided 95% upper 1.00)  gate-worse 0 / gate-better 1  McNemar p=1.00
                     mean-latency ratio 0.48 (95% upper 0.53)  p99 ratio 0.49 (95% upper 0.59)
                     VERDICT accuracy: PASS   latency: PASS
gate: escalated 16 no-solution + 13 disagreement of 16000 basis-shots; agreed-but-wrong 0/15971 (first leg 0/15445, later 0/526; X/Z [0, 0])
seeds: of 555 shots past the first leg, iterations differ on 543, logical vectors differ on 19
prefix (descriptive): 1000 pairs: 2 vs 2 fails, latency x0.49; 2000 pairs: 3 vs 3 fails, latency x0.46; 8000 pairs: 9 vs 10 fails, latency x0.48

=== data/agree_p0.004_s101.npz: p=0.004, 3000 pairs, seed 101 ===
policy                                fails           LER/cycle [95% CI]    esc    mean    p50    p95     p99     max  (ms per pair)
Relay-BP (kit)                           30  8.37e-04 [5.6e-04, 1.2e-03]   0.0%   220.9   74.0    815    3816    6786
fast Relay-BP alone                      80  2.25e-03 [1.8e-03, 2.8e-03]   0.0%    43.2   10.3    202     648    1424
1 seed, escalate if no solution          48  1.34e-03 [9.9e-04, 1.8e-03]   0.9%    95.2   10.3    202    3470    8210
AGREEMENT -> Relay-BP (primary)          35  9.77e-04 [6.8e-04, 1.4e-03]   1.5%   156.8   20.6    419    4488    9502
agreement -> Relay-BP, parallel*         35  9.77e-04 [6.8e-04, 1.4e-03]   1.5%   126.0   10.9    319    4130    8210
agreement -> nconv2                      38  1.06e-03 [7.5e-04, 1.5e-03]   1.5%   133.4   20.6    405    3364    6461

primary vs Relay-BP: failure ratio 1.17 (one-sided 95% upper 1.36)  gate-worse 6 / gate-better 1  McNemar p=0.12
                     mean-latency ratio 0.71 (95% upper 0.77)  p99 ratio 1.18 (95% upper 1.32)
                     VERDICT accuracy: INCONCLUSIVE   latency: PASS
gate: escalated 73 no-solution + 19 disagreement of 6000 basis-shots; agreed-but-wrong 12/5908 (first leg 2/5187, later 10/721; X/Z [5, 7])
seeds: of 813 shots past the first leg, iterations differ on 781, logical vectors differ on 64
prefix (descriptive): 1000 pairs: 16 vs 13 fails, latency x0.74; 2000 pairs: 28 vs 24 fails, latency x0.73; 3000 pairs: 35 vs 30 fails, latency x0.71

=== data/agree_p0.004_s401.npz: p=0.004, 3000 pairs, seed 401 ===
policy                                fails           LER/cycle [95% CI]    esc    mean    p50    p95     p99     max  (ms per pair)
Relay-BP (kit)                           28  7.81e-04 [5.2e-04, 1.1e-03]   0.0%   290.2   99.4   1028    4854    6140
fast Relay-BP alone                      72  2.02e-03 [1.6e-03, 2.5e-03]   0.0%    53.7   13.6    237     839    1154
1 seed, escalate if no solution          39  1.09e-03 [7.7e-04, 1.5e-03]   0.8%   107.0   13.6    237    3518    6515
AGREEMENT -> Relay-BP (primary)          26  7.25e-04 [4.7e-04, 1.1e-03]   1.7%   202.1   27.2    564    5953    7420
agreement -> Relay-BP, parallel*         26  7.25e-04 [4.7e-04, 1.1e-03]   1.7%   164.0   14.0    395    5688    6839
agreement -> nconv2                      28  7.81e-04 [5.2e-04, 1.1e-03]   1.7%   166.6   27.2    527    3492    7028

primary vs Relay-BP: failure ratio 0.93 (one-sided 95% upper 1.04)  gate-worse 1 / gate-better 3  McNemar p=0.62
                     mean-latency ratio 0.70 (95% upper 0.75)  p99 ratio 1.23 (95% upper 1.32)
                     VERDICT accuracy: PASS   latency: PASS
gate: escalated 69 no-solution + 31 disagreement of 6000 basis-shots; agreed-but-wrong 7/5900 (first leg 2/5151, later 5/749; X/Z [4, 3])
seeds: of 849 shots past the first leg, iterations differ on 827, logical vectors differ on 81
prefix (descriptive): 1000 pairs: 7 vs 10 fails, latency x0.70; 2000 pairs: 17 vs 19 fails, latency x0.72; 3000 pairs: 26 vs 28 fails, latency x0.70

=== data/agree_p0.005_s301.npz: p=0.005, 3000 pairs, seed 301 ===
policy                                fails           LER/cycle [95% CI]    esc    mean    p50    p95     p99     max  (ms per pair)
Relay-BP (kit)                          259  7.50e-03 [6.6e-03, 8.5e-03]   0.0%  1431.6  404.0   5560    7424   11154
fast Relay-BP alone                     504  1.52e-02 [1.4e-02, 1.7e-02]   0.0%   244.5   57.2    953    1430    2002
1 seed, escalate if no solution         279  8.10e-03 [7.2e-03, 9.1e-03]   7.3%   901.3   57.2   6130    6866   13044
AGREEMENT -> Relay-BP (primary)         247  7.13e-03 [6.3e-03, 8.1e-03]  11.2%  1373.9  140.6   7093    8415   14757
agreement -> Relay-BP, parallel*        247  7.13e-03 [6.3e-03, 8.1e-03]  11.2%  1186.8   89.6   6290    7388   13045
agreement -> nconv2                     254  7.35e-03 [6.5e-03, 8.3e-03]  11.2%  1146.5  140.6   6831    8190   14625

primary vs Relay-BP: failure ratio 0.95 (one-sided 95% upper 0.98)  gate-worse 2 / gate-better 14  McNemar p=0.00
                     mean-latency ratio 0.96 (95% upper 0.99)  p99 ratio 1.13 (95% upper 1.26)
                     VERDICT accuracy: PASS   latency: FAIL
gate: escalated 591 no-solution + 81 disagreement of 6000 basis-shots; agreed-but-wrong 24/5328 (first leg 7/3830, later 17/1498; X/Z [11, 13])
seeds: of 2170 shots past the first leg, iterations differ on 1853, logical vectors differ on 344
prefix (descriptive): 1000 pairs: 81 vs 86 fails, latency x0.94; 2000 pairs: 164 vs 172 fails, latency x0.95; 3000 pairs: 247 vs 259 fails, latency x0.96

replication at p=0.004 (seeds 101 vs 401): Relay-BP (kit): 30 vs 28 fails (Fisher p=0.90); AGREEMENT -> Relay-BP (primary): 35 vs 26 fails (Fisher p=0.30); escalations 92 vs 100 (Fisher p=0.61)

pooled over 17000 pairs: gate 317 vs Relay-BP 327 pair failures -> pooled check PASS

Timing validation (single worker, decoder order randomised per shot, OMP/RAYON threads=1, p=0.004, 400 pairs, seed 501):
Relay-BP 2 fails mean 142.9 ms p99 2137; agreement 2 fails mean 113.4 ms p99 2779; mean ratio 0.79 (95% upper 0.92), p99 ratio 1.30.

Questions (under ~350 words):
1. Your verdict per noise level and overall. Is the agreement gate "effective"? For what claim exactly?
2. Explain the p=0.005 result (significantly fewer failures than Relay-BP, 14 vs 2 discordant, but no speed-up), and
   the p=0.004 seed-101 vs seed-401 disagreement (35 vs 26 fails). Anything suspicious?
3. The single-worker timing ratio (0.79, upper 0.92) is weaker than the 8-worker ratio (0.70). Which should be quoted?
4. What is the one most valuable next change to the method?
