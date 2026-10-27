# Main results: ds-pro (deepseek-v4-pro) on test (120 documents)

| setting | Entity-C | Trig-I | Trig-C | Arg-I (EM) | Arg-C (EM) | Arg-C (BoW) | calls | parse fail | blocked | tokens (k) | cost (RMB, peak) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Baseline (zero-shot, all-in-one) | 42.5 | 33.5 | 25.5 | 17.9 | 12.7 | 16.1 | 120 | 1 | 0 | 251.6 | 5.15 |
| NewsEE framework | 57.2 | 50.5 | 47.2 | 25.0 | 22.7 | 28.3 | 732 | 7 | 0 | 2005.3 | 22.46 |
| Framework, gold triggers | 0.0 | 100.0 | 100.0 | 45.0 | 43.0 | 54.3 | 387 | 0 | 0 | 668.2 | 6.73 |

## Framework minus baseline (paired bootstrap, 1000 samples)

| metric | baseline | framework | difference | 95% CI | significant |
|---|---|---|---|---|---|
| Entity-C | 42.5 | 57.2 | +14.8 | [+11.8, +17.4] | yes |
| Trig-I | 33.5 | 50.5 | +17.1 | [+12.7, +21.9] | yes |
| Trig-C | 25.5 | 47.2 | +21.7 | [+16.9, +27.2] | yes |
| Arg-C (EM) | 12.7 | 22.7 | +10.0 | [+7.1, +13.2] | yes |
| Arg-C (BoW) | 16.1 | 28.3 | +12.3 | [+9.1, +15.7] | yes |

## Per event type (F1)

| event type | gold triggers | Trig-C baseline | Trig-C framework | Arg-C baseline | Arg-C framework |
|---|---|---|---|---|---|
| Attack | 117 | 30.2 | 44.3 | 14.2 | 18.6 |
| Military_operation | 166 | 3.4 | 49.7 | 1.2 | 19.1 |
| Conquering | 66 | 35.2 | 50.2 | 14.9 | 26.5 |
| Killing | 63 | 72.7 | 80.9 | 34.2 | 44.2 |
| Death | 47 | 43.4 | 64.9 | 17.8 | 32.9 |
| Bodily_harm | 47 | 54.0 | 61.2 | 24.6 | 27.9 |
| Catastrophe | 135 | 10.9 | 42.2 | 3.2 | 21.0 |
| Destroying | 47 | 59.3 | 68.8 | 25.5 | 27.8 |
| Damaging | 46 | 31.6 | 56.1 | 12.0 | 24.6 |
| Statement | 47 | 15.1 | 20.9 | 7.7 | 9.3 |
| Change_of_leadership | 19 | 18.5 | 23.9 | 12.5 | 19.0 |
| Arriving | 40 | 13.5 | 30.0 | 9.5 | 14.4 |

Verification removed (framework): {'argument_not_in_text': 18, 'entity_duplicate': 45, 'trigger_duplicate': 4, 'entity_not_in_text': 22}
