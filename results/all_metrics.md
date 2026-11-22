| p | decoder | source | pairs | failed pairs | LER / cycle | mean ms/pair | p90 | p99 | pairs/s (8 workers) |
|---|---|---|---|---|---|---|---|---|---|
| 0.003 | BP-OSD | organisers (kit README) | 10000 | 56 | 4.70e-04 | 140 |  |  |  |
| 0.003 | BP-OSD | ours, same shots | 10000 | 55 | 4.59e-04 | 94 | 312 | 565 | 85 |
| 0.003 | ML router (Emma, t=0.7) | ours, 10k pairs | 10000 | 41 | 3.42e-04 | 61 | 137 | 391 |  |
| 0.003 | Relay-BP | organisers (kit README) | 10000 | 5 | 4.20e-05 | 100 |  |  |  |
| 0.003 | Relay-BP | ours, 100k pairs | 100000 | 74 | 6.17e-05 | 77 |  |  |  |
| 0.003 | Relay-BP | ours, same shots | 10000 | 5 | 4.17e-05 | 57 | 83 | 404 | 140 |
| 0.003 | agreement gate | ours, 100k pairs | 100000 | 86 | 7.17e-05 | 30 |  |  |  |
| 0.003 | agreement gate | ours, same shots | 10000 | 7 | 5.84e-05 | 22 | 13 | 307 | 365 |
| 0.004 | BP-OSD | organisers (kit README) | 10000 | 522 | 4.40e-03 | 330 |  |  |  |
| 0.004 | BP-OSD | ours, same shots | 6000 | 336 | 4.79e-03 | 282 | 649 | 849 | 28 |
| 0.004 | ML router (Emma, t=0.7) | ours, 10k pairs | 10000 | 351 | 2.97e-03 | 210 | 429 | 2182 |  |
| 0.004 | Relay-BP | organisers (kit README) | 10000 | 105 | 8.70e-04 | 380 |  |  |  |
| 0.004 | Relay-BP | ours, same shots | 6000 | 55 | 7.67e-04 | 262 | 436 | 4279 | 31 |
| 0.004 | agreement gate | ours, same shots | 6000 | 53 | 7.39e-04 | 191 | 236 | 4415 | 42 |
| 0.005 | BP-OSD | organisers (kit README) | 10000 | 2588 | 2.30e-02 | 590 |  |  |  |
| 0.005 | BP-OSD | ours, same shots | 3000 | 726 | 2.28e-02 | 578 | 909 | 1138 | 14 |
| 0.005 | ML router (Emma, t=0.7) | ours, 10k pairs | 10000 | 1413 | 1.26e-02 | 836 | 2373 | 5400 |  |
| 0.005 | Relay-BP | organisers (kit README) | 10000 | 825 | 6.90e-03 | 1700 |  |  |  |
| 0.005 | Relay-BP | ours, same shots | 3000 | 262 | 7.59e-03 | 1335 | 5038 | 7835 | 6 |
| 0.005 | agreement gate | ours, same shots | 3000 | 262 | 7.59e-03 | 1164 | 5108 | 7603 | 7 |
