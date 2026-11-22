# Pre-registration (written before running): p = 0.003 with 100,000 pairs

Purpose: settle accuracy at p = 0.003, where 10k-pair runs had too few failures (5-15 per run).
The gate uses the revised setting K=10 with the R5 referee. This is what alarm-count routing chose on 100% of 0.003 shots
in discussion/14. It is compared with kit Relay-BP on the same shots, random order per shot, fresh seed 6030,
100,000 pairs, 8 workers. Rules as in 09: accuracy PASS if the 99.2% upper bound of the paired failure ratio
is < 1.2; latency PASS if the 95% bootstrap upper bounds of the mean, p90 and p99 ratios are all < 1. BP-OSD is not rerun
(discussion/14 already has 55 failed pairs in 10k).
