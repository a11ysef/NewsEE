| setting | Entity-C | Trig-I | Trig-C | Arg-I (EM) | Arg-C (EM) | Arg-C (BoW) | parse fail | blocked by filter | tokens (k) |
|---|---|---|---|---|---|---|---|---|---|
| Baseline: naive zero-shot all-in-one | 35.83 | 20.52 | 14.16 | 10.21 | 6.8 | 9.1 | 0/30 | 0 | 76.9 |
| Full framework | 51.38 | 42.37 | 37.57 | 18.72 | 17.05 | 21.35 | 1/196 | 2 | 301.9 |
| w/o decomposition (all-in-one) | 51.95 | 27.01 | 23.28 | 14.47 | 13.36 | 16.96 | 1/30 | 0 | 256.0 |
| w/o guidelines | 51.83 | 35.43 | 30.0 | 16.44 | 14.86 | 18.71 | 0/208 | 3 | 507.0 |
| random instead of retrieved demos | 46.93 | 40.23 | 34.28 | 17.91 | 15.57 | 19.6 | 1/186 | 3 | 496.7 |
| w/o demonstrations (zero-shot) | 36.76 | 39.38 | 32.07 | 15.52 | 13.32 | 17.98 | 1/181 | 1 | 226.9 |
| w/o verification | 51.46 | 41.72 | 37.0 | 18.6 | 16.98 | 21.18 | 1/196 | 2 | 0.0 |
| full, gold triggers (arguments only) | 0.0 | 100.0 | 100.0 | 41.17 | 39.17 | 48.72 | 0/103 | 1 | 211.3 |
