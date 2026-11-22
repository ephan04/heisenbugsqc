# Round 10: review of stage-1 discovery (noise-adaptive agreement gate, NO ML)

Context: Gross code [[144,12,12]], 12 cycles, per-basis Relay-BP decoding. Agreement gate: fast Relay-BP seed 0 (stop_nconv=1, at most K restart legs) -> accept if solved in the deterministic first 80 iterations; escalate to the referee if there is no solution; otherwise run seed 1 and accept if the logicals agree, else the referee. Referees: R5 = kit Relay-BP (stop_nconv=5, 300 sets), R2 = stop_nconv=2, R1 = stop_nconv=1 with 300 sets. Baseline = R5 alone. The noise level is given (a future ML/alarm-count estimator will supply it). The pre-registered rule (discussion/09): among settings with failure ratio <= 1.05, pick the lowest mean time. Capped K<50 values are derived from the uncapped runs. Stage 2 (fresh seeds, real decoder, random per-shot order) is running now with these frozen picks. Accuracy PASS = 99.2% upper bound of the paired failure ratio < 1.2; latency PASS = 95% bootstrap upper bounds of the mean/p90/p99 ratios < 1.

Discovery table (ratios vs baseline on identical shots; esc = fraction of decodes escalated):

p = 0.003  (10000 pairs)  baseline R5: 12 failed pairs, mean 61 ms, p90 89, p99 455
     K  ref  fails  ratio   mean    p90    p99    esc
     5   R5     13   1.08   0.42   0.16   1.01   1.2%
     5   R2     10   0.83   0.32   0.16   0.53   1.2%
     5   R1     15   1.25   0.28   0.16   0.48   1.2%
    10   R5     13   1.08   0.40   0.16   0.75   0.6%
    10   R2     10   0.83   0.32   0.16   0.55   0.6%
    10   R1     15   1.25   0.29   0.16   0.51   0.6%
    20   R5     12   1.00   0.38   0.16   0.53   0.3%
    20   R2     10   0.83   0.32   0.16   0.50   0.3%
    20   R1     15   1.25   0.30   0.16   0.50   0.3%
    50   R5     12   1.00   0.36   0.16   0.53   0.2%
    50   R2     10   0.83   0.33   0.16   0.50   0.2%
    50   R1     15   1.25   0.31   0.16   0.50   0.2%
   SELECTED: K=5 referee=R2

p = 0.004  (6000 pairs)  baseline R5: 61 failed pairs, mean 249 ms, p90 435, p99 4026
     K  ref  fails  ratio   mean    p90    p99    esc
     5   R5     60   0.98   0.73   0.88   1.02   7.3%
     5   R2     77   1.26   0.50   0.51   0.78   7.3%
     5   R1     77   1.26   0.36   0.46   0.35   7.3%
    10   R5     60   0.98   0.71   0.57   1.03   4.9%
    10   R2     72   1.18   0.51   0.51   0.75   4.9%
    10   R1     76   1.25   0.38   0.51   0.36   4.9%
    20   R5     61   1.00   0.67   0.53   1.07   3.0%
    20   R2     72   1.18   0.52   0.52   0.75   3.0%
    20   R1     74   1.21   0.41   0.52   0.38   3.0%
    50   R5     59   0.97   0.64   0.53   1.14   1.7%
    50   R2     70   1.15   0.54   0.52   0.75   1.7%
    50   R1     74   1.21   0.46   0.52   0.48   1.7%
   SELECTED: K=50 referee=R5

p = 0.0045  (3000 pairs)  baseline R5: 80 failed pairs, mean 514 ms, p90 1251, p99 4427
     K  ref  fails  ratio   mean    p90    p99    esc
     5   R5     85   1.06   0.85   1.01   1.01  14.5%
     5   R2    110   1.38   0.55   0.48   1.00  14.5%
     5   R1    111   1.39   0.42   0.32   0.96  14.5%
    10   R5     83   1.04   0.83   1.01   1.02  10.5%
    10   R2    109   1.36   0.57   0.49   1.02  10.5%
    10   R1    109   1.36   0.45   0.38   0.98  10.5%
    20   R5     80   1.00   0.80   0.95   1.06   7.0%
    20   R2    104   1.30   0.59   0.52   1.05   7.0%
    20   R1    108   1.35   0.48   0.47   1.01   7.0%
    50   R5     80   1.00   0.77   0.55   1.17   4.2%
    50   R2     99   1.24   0.62   0.51   1.15   4.2%
    50   R1    104   1.30   0.54   0.51   1.12   4.2%
   SELECTED: K=50 referee=R5

p = 0.005  (3000 pairs)  baseline R5: 241 failed pairs, mean 1250 ms, p90 4489, p99 7165
     K  ref  fails  ratio   mean    p90    p99    esc
     5   R5    242   1.00   0.91   0.99   0.98  25.9%
     5   R2    262   1.09   0.63   0.66   0.84  25.9%
     5   R1    277   1.15   0.47   0.35   0.78  25.9%
    10   R5    240   1.00   0.90   1.01   1.00  20.6%
    10   R2    260   1.08   0.65   0.68   0.85  20.6%
    10   R1    272   1.13   0.49   0.36   0.79  20.6%
    20   R5    242   1.00   0.89   1.04   1.00  16.0%
    20   R2    259   1.07   0.67   0.72   0.89  16.0%
    20   R1    273   1.13   0.52   0.40   0.81  16.0%
    50   R5    238   0.99   0.89   1.13   1.07  11.0%
    50   R2    256   1.06   0.72   0.80   0.95  11.0%
    50   R1    261   1.08   0.60   0.49   0.91  11.0%
   SELECTED: K=50 referee=R5

p = 0.0055  (1500 pairs)  baseline R5: 286 failed pairs, mean 2362 ms, p90 5597, p99 10093
     K  ref  fails  ratio   mean    p90    p99    esc
     5   R5    287   1.00   0.94   1.00   1.02  39.6%
     5   R2    297   1.04   0.71   0.94   0.83  39.6%
     5   R1    318   1.11   0.54   0.90   0.66  39.6%
    10   R5    288   1.01   0.94   1.01   1.04  33.9%
    10   R2    297   1.04   0.72   0.96   0.85  33.9%
    10   R1    315   1.10   0.56   0.92   0.67  33.9%
    20   R5    287   1.00   0.94   1.04   1.07  28.1%
    20   R2    295   1.03   0.75   0.99   0.88  28.1%
    20   R1    310   1.08   0.60   0.94   0.70  28.1%
    50   R5    284   0.99   0.95   1.13   1.16  20.7%
    50   R2    287   1.00   0.81   1.09   0.92  20.7%
    50   R1    303   1.06   0.68   1.03   0.84  20.7%
   SELECTED: K=5 referee=R2

p = 0.006  (1000 pairs)  baseline R5: 367 failed pairs, mean 4037 ms, p90 9292, p99 10563
     K  ref  fails  ratio   mean    p90    p99    esc
     5   R5    368   1.00   0.97   1.00   1.02  56.2%
     5   R2    373   1.02   0.76   0.74   0.99  56.2%
     5   R1    376   1.02   0.60   0.64   0.94  56.2%
    10   R5    370   1.01   0.97   1.01   1.03  50.9%
    10   R2    374   1.02   0.77   0.75   1.00  50.9%
    10   R1    377   1.03   0.62   0.65   0.97  50.9%
    20   R5    369   1.01   0.97   1.03   1.07  44.1%
    20   R2    374   1.02   0.80   0.78   1.04  44.1%
    20   R1    376   1.02   0.65   0.67   1.00  44.1%
    50   R5    367   1.00   1.02   1.06   1.17  37.1%
    50   R2    368   1.00   0.88   0.83   1.13  37.1%
    50   R1    375   1.02   0.74   0.74   1.08  37.1%
   SELECTED: K=5 referee=R1

frozen selection -> results/adaptive_selected.json

Questions (be concise, under 400 words, and do not run tools):
1. Interpret the pattern: R2/R1 are fine at 0.003 and >= 0.0055 but cost 15-39% at 0.004-0.005. Why might cheaper referees be harmless at high noise? (At high noise most failures are shared and Relay-BP fails anyway?)
2. Are the K=5 picks at 0.0055/0.006 and the R2 pick at 0.003 likely to hold in stage 2, given the small discordant counts? Which verdicts do you predict will be PASS, FAIL or INCONCLUSIVE?
3. Is the mean-time-only selection rule leaving value on the table (e.g. p99 > 1 for K=50 at 0.004-0.005)? Suggest a follow-up rule for the NEXT pre-registration, without changing this one.
4. For the future noise estimator: given that single-shot noise classification is ~56-82% accurate and a 10-shot window gives ~4% error, what is the cost of misrouting (e.g. a true 0.004 shot routed to the 0.003 setting K=5,R2)? Estimate from the table.
