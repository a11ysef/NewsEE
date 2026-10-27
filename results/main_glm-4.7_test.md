# Main results: glm-4.7 (glm-4.7) on test (120 documents)

| setting | Entity-C | Trig-I | Trig-C | Arg-I (EM) | Arg-C (EM) | Arg-C (BoW) | calls | parse fail | blocked | tokens (k) | cost (RMB, peak) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Baseline (zero-shot, all-in-one) | 49.0 | 43.9 | 34.9 | 21.5 | 15.6 | 19.6 | 120 | 0 | 0 | 190.3 | 0.0 |
| NewsEE framework | 57.4 | 58.6 | 55.7 | 26.5 | 23.9 | 30.2 | 736 | 0 | 4 | 1934.2 | 0.0 |
| Framework, gold triggers | 0.0 | 100.0 | 100.0 | 44.1 | 41.5 | 51.8 | 387 | 0 | 4 | 623.3 | 0.0 |

## Framework minus baseline (paired bootstrap, 1000 samples)

| metric | baseline | framework | difference | 95% CI | significant |
|---|---|---|---|---|---|
| Entity-C | 49.0 | 57.4 | +8.4 | [+5.5, +11.5] | yes |
| Trig-I | 43.9 | 58.6 | +14.7 | [+10.2, +19.1] | yes |
| Trig-C | 34.9 | 55.7 | +20.8 | [+16.4, +25.2] | yes |
| Arg-C (EM) | 15.6 | 23.9 | +8.3 | [+5.3, +11.5] | yes |
| Arg-C (BoW) | 19.6 | 30.2 | +10.6 | [+7.4, +14.2] | yes |

## Per event type (F1)

| event type | gold triggers | Trig-C baseline | Trig-C framework | Arg-C baseline | Arg-C framework |
|---|---|---|---|---|---|
| Attack | 117 | 38.5 | 56.1 | 14.3 | 21.5 |
| Military_operation | 166 | 6.4 | 53.8 | 3.9 | 19.1 |
| Conquering | 66 | 43.8 | 60.1 | 22.3 | 34.4 |
| Killing | 63 | 74.0 | 84.0 | 34.2 | 38.4 |
| Death | 47 | 64.7 | 75.0 | 26.4 | 39.1 |
| Bodily_harm | 47 | 54.7 | 66.7 | 19.7 | 37.2 |
| Catastrophe | 135 | 25.6 | 57.7 | 8.2 | 18.7 |
| Destroying | 47 | 60.2 | 69.5 | 17.4 | 26.8 |
| Damaging | 46 | 64.4 | 75.2 | 21.8 | 26.5 |
| Statement | 47 | 24.1 | 21.8 | 12.1 | 11.1 |
| Change_of_leadership | 19 | 34.5 | 33.0 | 19.9 | 18.3 |
| Arriving | 40 | 12.1 | 33.8 | 6.9 | 16.7 |

Verification removed (framework): {'argument_not_in_text': 7, 'entity_not_in_text': 33, 'entity_duplicate': 68, 'trigger_duplicate': 4, 'trigger_not_in_text': 3, 'entity_bad_type': 1, 'argument_bad_role': 10}
