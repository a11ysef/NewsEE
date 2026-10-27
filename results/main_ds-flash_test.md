# Main results: ds-flash (deepseek-flash) on test (120 documents)

| setting | Entity-C | Trig-I | Trig-C | Arg-I (EM) | Arg-C (EM) | Arg-C (BoW) | calls | parse fail | blocked | tokens (k) | cost (RMB, peak) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Baseline (zero-shot, all-in-one) | 46.8 | 42.4 | 32.3 | 21.6 | 15.6 | 19.3 | 120 | 0 | 0 | 205.6 | 1.1 |
| NewsEE framework | 57.4 | 60.6 | 57.5 | 28.6 | 26.0 | 32.4 | 685 | 0 | 0 | 1794.4 | 4.45 |
| Framework, gold triggers | 0.0 | 100.0 | 100.0 | 44.7 | 42.0 | 53.9 | 387 | 0 | 0 | 626.0 | 1.42 |

## Framework minus baseline (paired bootstrap, 1000 samples)

| metric | baseline | framework | difference | 95% CI | significant |
|---|---|---|---|---|---|
| Entity-C | 46.8 | 57.4 | +10.6 | [+7.5, +13.6] | yes |
| Trig-I | 42.4 | 60.6 | +18.1 | [+13.2, +22.9] | yes |
| Trig-C | 32.3 | 57.5 | +25.2 | [+19.9, +30.5] | yes |
| Arg-C (EM) | 15.6 | 26.0 | +10.4 | [+7.2, +13.9] | yes |
| Arg-C (BoW) | 19.3 | 32.4 | +13.1 | [+9.7, +16.8] | yes |

## Per event type (F1)

| event type | gold triggers | Trig-C baseline | Trig-C framework | Arg-C baseline | Arg-C framework |
|---|---|---|---|---|---|
| Attack | 117 | 30.4 | 58.7 | 16.4 | 25.0 |
| Military_operation | 166 | 0.0 | 56.2 | 0.0 | 21.7 |
| Conquering | 66 | 33.3 | 52.7 | 16.3 | 29.7 |
| Killing | 63 | 70.2 | 81.4 | 33.1 | 40.4 |
| Death | 47 | 59.8 | 76.1 | 26.0 | 42.2 |
| Bodily_harm | 47 | 40.0 | 64.4 | 13.6 | 31.0 |
| Catastrophe | 135 | 21.4 | 58.0 | 6.0 | 21.6 |
| Destroying | 47 | 62.2 | 68.8 | 24.4 | 24.3 |
| Damaging | 46 | 54.4 | 78.8 | 21.5 | 31.6 |
| Statement | 47 | 13.6 | 33.9 | 8.4 | 16.6 |
| Change_of_leadership | 19 | 41.9 | 30.4 | 22.9 | 20.0 |
| Arriving | 40 | 14.9 | 28.9 | 8.1 | 9.5 |

Verification removed (framework): {'argument_not_in_text': 18, 'entity_duplicate': 45, 'trigger_duplicate': 3, 'entity_not_in_text': 23, 'trigger_not_in_text': 1}
