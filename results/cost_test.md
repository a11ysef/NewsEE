# Cost and efficiency on test

| model | method | docs | LLM calls | calls / doc | input tokens / doc (k) | output tokens / doc (k) | Trig-C | Arg-C (EM) | cost RMB (peak) | cost RMB (off-peak) |
|---|---|---|---|---|---|---|---|---|---|---|
| glm-4.7 | Baseline (zero-shot, all-in-one) | 120 | 120 | 1.0 | 0.8 | 0.96 | 34.9 | 15.6 | — | — |
| glm-4.7 | NewsEE framework | 120 | 736 | 6.1 | 14.8 | 1.36 | 55.7 | 23.9 | — | — |
| glm-4.7 | Framework, gold triggers | 120 | 387 | 3.2 | 7.8 | 0.43 | 100.0 | 41.5 | — | — |
| ds-pro | Baseline (zero-shot, all-in-one) | 120 | 120 | 1.0 | 0.8 | 1.34 | 25.5 | 12.7 | 5.15 | 2.57 |
| ds-pro | NewsEE framework | 120 | 732 | 6.1 | 14.7 | 2.04 | 47.2 | 22.7 | 22.46 | 11.23 |
| ds-pro | Framework, gold triggers | 120 | 387 | 3.2 | 7.6 | 0.48 | 100.0 | 43.0 | 9.83 | 4.91 |
| glm-air | Baseline (zero-shot, all-in-one) | 120 | 120 | 1.0 | 0.8 | 1.55 | 16.5 | 6.9 | — | — |
| glm-air | NewsEE framework | 120 | 754 | 6.3 | 15.2 | 1.70 | 38.8 | 17.6 | — | — |
| glm-air | Framework, gold triggers | 120 | 387 | 3.2 | 7.7 | 0.39 | 100.0 | 35.8 | — | — |
| ds-flash | Baseline (zero-shot, all-in-one) | 120 | 120 | 1.0 | 0.8 | 0.95 | 32.3 | 15.6 | 1.1 | 0.55 |
| ds-flash | NewsEE framework | 120 | 685 | 5.7 | 13.8 | 1.19 | 57.5 | 26.0 | 4.45 | 2.22 |
| ds-flash | Framework, gold triggers | 120 | 387 | 3.2 | 7.6 | 0.36 | 100.0 | 42.0 | 2.18 | 1.09 |
| ds-flash-think | Baseline (zero-shot, all-in-one) | 120 | 120 | 1.0 | 0.8 | 7.95 | 1.2 | 0.2 | 7.82 | 3.91 |
| ds-flash-think | NewsEE framework | 120 | 414 | 3.5 | 8.3 | 16.91 | 35.3 | 15.7 | 18.21 | 9.11 |

Tokens are estimated from fresh (non-cached) calls. Zhipu runs: resource packs, no cash cost.
DeepSeek costs use cache-miss list prices, so they are upper bounds.

## Cost of each framework variant (ds-flash, dev, 30 documents)

| setting | Trig-C | Arg-C (EM) | tokens (k) | relative to full |
|---|---|---|---|---|
| Baseline: naive zero-shot all-in-one | 28.23 | 16.64 | 49.3 | 0.10x |
| Full framework | 53.18 | 27.91 | 503.1 | 1.00x |
| w/o decomposition (all-in-one) | 50.16 | 24.75 | 239.9 | 0.48x |
| w/o guidelines | 50.28 | 24.29 | 471.8 | 0.94x |
| random instead of retrieved demos | 50.37 | 25.29 | 468.0 | 0.93x |
| w/o demonstrations (zero-shot) | 51.56 | 23.51 | 191.6 | 0.38x |
| full, gold triggers (arguments only) | 100.0 | 48.37 | 201.5 | 0.40x |

Entity guideline V1 run (all calls fresh); token counts of later re-runs are partly cached.
