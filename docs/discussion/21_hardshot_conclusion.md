# Hard-shot spotter (ML version a): conclusion

Design: discussion/19 (with GPT and Gemini). Result: results/hardshot_check.txt and hardshot_separability.txt. Review: discussion/20.

- Ceiling (perfect spotter, discovery replay): mean -3 to -7 points; p99 at 0.004 1.03 -> 0.99; p90 at 0.005 1.01 -> 0.97.
- Models: logistic and GBDT on pre-decode syndrome features, plus a GBDT on time saved. Inference cost per decode: rule 2 us, logistic 112 us, GBDT 0.7-2.8 ms.
- Held out (last 30% of each discovery file): every policy, including the simple alarm-count rule, chose to skip almost nothing, with results equal to the plain gate.
- Separability of "the gate would escalate": AUC 0.67-0.74 for the alarm count and 0.69-0.74 for logistic. Top-1% precision is 2% at 0.003 and 39% at 0.004.
- Decision (pre-agreed decision point; GPT and Gemini agree): stop; no fresh-seed confirmation.
- Wording (GPT): pre-decode syndrome summaries moderately predict escalation, but the tested routing policies yield no convincing net latency benefit under the tail-latency objective, the failure constraint and the inference costs.
- Next (both): use early in-flight decoder state (for example, unsatisfied checks after the first 80-iteration leg) to decide early escalation, rather than syndrome summaries alone. This needs instrumenting Relay-BP.
