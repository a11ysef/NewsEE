# All models on test

| model | method | Entity-C | Trig-I | Trig-C | Arg-C (EM) | Arg-C (BoW) |
|---|---|---|---|---|---|---|
| glm-4.7 | Baseline (zero-shot, all-in-one) | 49.0 | 43.9 | 34.9 | 15.6 | 19.6 |
| glm-4.7 | NewsEE framework | 57.4 | 58.6 | 55.7 | 23.9 | 30.2 |
| glm-4.7 | Framework, gold triggers | 0.0 | 100.0 | 100.0 | 41.5 | 51.8 |
| ds-pro | Baseline (zero-shot, all-in-one) | 42.5 | 33.5 | 25.5 | 12.7 | 16.1 |
| ds-pro | NewsEE framework | 57.2 | 50.5 | 47.2 | 22.7 | 28.3 |
| ds-pro | Framework, gold triggers | 0.0 | 100.0 | 100.0 | 43.0 | 54.3 |
| glm-air | Baseline (zero-shot, all-in-one) | 33.4 | 20.6 | 16.5 | 6.9 | 9.8 |
| glm-air | NewsEE framework | 52.1 | 42.8 | 38.8 | 17.6 | 23.5 |
| glm-air | Framework, gold triggers | 0.0 | 100.0 | 100.0 | 35.8 | 47.9 |
| ds-flash | Baseline (zero-shot, all-in-one) | 46.8 | 42.4 | 32.3 | 15.6 | 19.3 |
| ds-flash | NewsEE framework | 57.4 | 60.6 | 57.5 | 26.0 | 32.4 |
| ds-flash | Framework, gold triggers | 0.0 | 100.0 | 100.0 | 42.0 | 53.9 |

Framework minus baseline (✱ = 95% CI excludes 0):

| model | Entity-C | Trig-I | Trig-C | Arg-C (EM) | Arg-C (BoW) |
|---|---|---|---|---|---|
| glm-4.7 | +8.4 ✱ | +14.7 ✱ | +20.8 ✱ | +8.3 ✱ | +10.6 ✱ |
| ds-pro | +14.8 ✱ | +17.1 ✱ | +21.7 ✱ | +10.0 ✱ | +12.3 ✱ |
| glm-air | +18.7 ✱ | +22.2 ✱ | +22.3 ✱ | +10.6 ✱ | +13.7 ✱ |
| ds-flash | +10.6 ✱ | +18.1 ✱ | +25.2 ✱ | +10.4 ✱ | +13.1 ✱ |
