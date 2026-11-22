# Round 20: result of the hard-shot spotter quick check (design in discussion/19). Under 350 words. Do not run tools.

Implemented as agreed: features (alarms, other-basis alarms, adjacent alarm pairs, pair density, isolated alarms, same-check repeats in consecutive cycles, per-cycle counts, max per cycle, causal p_hat), label = escalated (plus a GBDT on time saved), split 50% train / 20% validation (thresholds per settings regime; objective mean of mean/p90/p99 ratios with failures <= gate + 1) / 30% held out, measured inference cost charged per decode.

```
training decodes 24500, escalated 10.1%
inference cost per basis decode: alarm-count rule 2 us, logistic (escalated) 112 us, GBDT (escalated) 2828 us, GBDT (time saved) 717 us

held-out 40%... (last 30% of each discovery file; thresholds from the 20% validation slice)

 p=0.003  (3000 held-out pairs)
   gate as is             fails   5 (RBP   5)  mean 0.40  p90 0.16  p99 0.71
   perfect spotter        fails   5            mean 0.37  p90 0.16  p99 0.44  skip 0.7%
   alarm-count rule       fails   5            mean 0.40  p90 0.16  p99 0.71  skip 0.0%
   logistic (escalated)   fails   5            mean 0.41  p90 0.16  p99 0.71  skip 0.0%
   GBDT (escalated)       fails   5            mean 0.49  p90 0.22  p99 0.72  skip 0.0%
   GBDT (time saved)      fails   5            mean 0.43  p90 0.18  p99 0.71  skip 0.0%

 p=0.004  (1800 held-out pairs)
   gate as is             fails  16 (RBP  17)  mean 0.70  p90 0.59  p99 1.02
   perfect spotter        fails  16            mean 0.63  p90 0.50  p99 0.99  skip 5.0%
   alarm-count rule       fails  16            mean 0.70  p90 0.59  p99 1.02  skip 0.0%
   logistic (escalated)   fails  16            mean 0.70  p90 0.60  p99 1.02  skip 0.0%
   GBDT (escalated)       fails  16            mean 0.72  p90 0.61  p99 1.02  skip 0.0%
   GBDT (time saved)      fails  16            mean 0.71  p90 0.60  p99 1.02  skip 0.0%

 p=0.0045  (900 held-out pairs)
   gate as is             fails  20 (RBP  18)  mean 0.81  p90 0.92  p99 1.02
   perfect spotter        fails  20            mean 0.73  p90 0.77  p99 0.99  skip 9.9%
   alarm-count rule       fails  20            mean 0.81  p90 0.92  p99 1.02  skip 0.0%
   logistic (escalated)   fails  20            mean 0.81  p90 0.92  p99 1.02  skip 0.1%
   GBDT (escalated)       fails  20            mean 0.82  p90 0.93  p99 1.02  skip 0.0%
   GBDT (time saved)      fails  20            mean 0.81  p90 0.93  p99 1.02  skip 0.0%

 p=0.005  (900 held-out pairs)
   gate as is             fails  71 (RBP  69)  mean 0.89  p90 1.00  p99 0.99
   perfect spotter        fails  71            mean 0.82  p90 0.96  p99 0.96  skip 20.3%
   alarm-count rule       fails  71            mean 0.89  p90 1.00  p99 0.99  skip 0.0%
   logistic (escalated)   fails  71            mean 0.90  p90 0.99  p99 0.99  skip 4.9%
   GBDT (escalated)       fails  71            mean 0.89  p90 1.00  p99 1.00  skip 0.0%
   GBDT (time saved)      fails  71            mean 0.89  p90 1.00  p99 0.99  skip 0.0%

 p=0.0055  (450 held-out pairs)
   gate as is             fails  90 (RBP  87)  mean 0.70  p90 0.96  p99 0.76
   perfect spotter        fails  90            mean 0.66  p90 0.94  p99 0.74  skip 39.2%
   alarm-count rule       fails  90            mean 0.70  p90 0.96  p99 0.76  skip 0.2%
   logistic (escalated)   fails  90            mean 0.70  p90 0.96  p99 0.76  skip 1.9%
   GBDT (escalated)       fails  90            mean 0.71  p90 0.96  p99 0.76  skip 0.3%
   GBDT (time saved)      fails  90            mean 0.70  p90 0.96  p99 0.76  skip 0.0%

 p=0.006  (300 held-out pairs)
   gate as is             fails 130 (RBP 125)  mean 0.59  p90 0.57  p99 1.00
   perfect spotter        fails 130            mean 0.56  p90 0.55  p99 0.98  skip 56.3%
   alarm-count rule       fails 131            mean 0.59  p90 0.57  p99 1.00  skip 1.5%
   logistic (escalated)   fails 131            mean 0.59  p90 0.57  p99 0.99  skip 5.5%
   GBDT (escalated)       fails 131            mean 0.59  p90 0.57  p99 1.00  skip 2.0%
   GBDT (time saved)      fails 130            mean 0.59  p90 0.57  p99 1.00  skip 0.2%

logistic top features (standardised coefficients): p_hat +0.62, pair_density +0.56, adj_pairs -0.49, other_alarms +0.44, max_cycle +0.19, alarms +0.18, cycle_5 +0.16, cycle_7 +0.15

held-out separability of 'the gate would escalate this decode'
      p esc rate AUC count AUC logit   precision among top-scored decodes (logistic): top1% top5% top10%
 0.0030     0.7%      0.74      0.73      2%     3%     2%
        time saved by skipping an escalated decode: median 149 ms; time lost by skipping a non-escalated one: median 13 ms
 0.0040     5.0%      0.69      0.74     39%    18%    13%
        time saved by skipping an escalated decode: median 159 ms; time lost by skipping a non-escalated one: median 23 ms
 0.0045     9.9%      0.69      0.73     28%    32%    24%
        time saved by skipping an escalated decode: median 158 ms; time lost by skipping a non-escalated one: median 31 ms
 0.0050    20.3%      0.67      0.69     67%    57%    49%
        time saved by skipping an escalated decode: median 184 ms; time lost by skipping a non-escalated one: median 44 ms
 0.0055    39.2%      0.70      0.73     89%    78%    72%
        time saved by skipping an escalated decode: median 108 ms; time lost by skipping a non-escalated one: median -8 ms
 0.0060    56.3%      0.68      0.69    100%    93%    92%
        time saved by skipping an escalated decode: median 101 ms; time lost by skipping a non-escalated one: median -10 ms
```

Questions: (1) Is it right to stop here (no fresh-seed confirmation), per the plan's decision point? (2) Is the conclusion 'pre-decode syndrome features carry little information about whether the fast decoder will escalate (AUC ~0.7, the same as the alarm count)' justified, or did the design handicap it (e.g., the objective, the thresholds, the cost charge)? (3) One sentence each for the report: what does this negative result teach, and where should ML go next?
