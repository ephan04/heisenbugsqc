# Pre-registration (written before running): gate with noise-detector routing vs BP-OSD and Relay-BP

Fresh seeds 5030 / 5040 / 5050 at p = 0.003 / 0.004 / 0.005, with 10,000 / 6,000 / 3,000 pairs. Every shot runs
kit BP-OSD, kit Relay-BP (R5) and the gate routed by the alarm-count estimate, in random order per shot. The
estimate averages the last 10 pairs. The first third of the shots also runs the gate routed by the MLP estimate
(last 10 pairs).

Routing table (revised, discussion/13): nearest of {0.003..0.005: K=10, R5; 0.0055: K=5, R2; 0.006: K=5, R1}.
Both estimators were trained on seeds 9000+ only.

Verdicts vs Relay-BP, the same rules as 09: accuracy PASS if the 99.2% upper bound of the paired failure ratio is < 1.2;
latency PASS if the 95% bootstrap upper bounds of the mean, p90 and p99 ratios are all < 1. The MLP subset is
exploratory. Gate vs BP-OSD is reported descriptively (failure counts, times). Estimator cost is reported separately.
Timing uses 8 workers on one Mac (ratios are the claim; absolute ms are machine-specific).
