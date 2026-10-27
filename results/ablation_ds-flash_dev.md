| setting | Entity-C | Trig-I | Trig-C | Arg-I (EM) | Arg-C (EM) | Arg-C (BoW) | parse fail | blocked by filter | tokens (k) |
|---|---|---|---|---|---|---|---|---|---|
| Baseline: naive zero-shot all-in-one | 45.52 | 35.89 | 28.23 | 20.03 | 16.64 | 20.8 | 1/30 | 0 | 49.3 |
| Full framework | 54.79 | 56.36 | 53.18 | 30.3 | 27.91 | 32.97 | 0/182 | 0 | 102.6 |
| w/o decomposition (all-in-one) | 56.78 | 53.72 | 48.99 | 25.45 | 23.64 | 27.45 | 0/30 | 0 | 239.4 |
| w/o guidelines | 56.63 | 54.24 | 50.28 | 26.7 | 24.29 | 28.51 | 0/192 | 0 | 0.0 |
| random instead of retrieved demos | 51.93 | 56.52 | 50.37 | 29.05 | 25.29 | 30.3 | 0/179 | 0 | 96.7 |
| w/o demonstrations (zero-shot) | 45.66 | 57.82 | 51.56 | 27.5 | 23.51 | 27.06 | 0/171 | 0 | 42.6 |
| w/o verification | 55.12 | 56.2 | 53.03 | 30.14 | 27.76 | 32.8 | 0/182 | 0 | 0.0 |
| full, gold triggers (arguments only) | 0.0 | 100.0 | 100.0 | 50.54 | 48.37 | 57.62 | 0/103 | 0 | 0.0 |
