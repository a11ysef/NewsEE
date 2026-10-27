# Main results: glm-air (glm-4.5-air) on test (120 documents)

| setting | Entity-C | Trig-I | Trig-C | Arg-I (EM) | Arg-C (EM) | Arg-C (BoW) | calls | parse fail | blocked | tokens (k) | cost (RMB, peak) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Baseline (zero-shot, all-in-one) | 33.4 | 20.6 | 16.5 | 9.8 | 6.9 | 9.8 | 120 | 0 | 0 | 280.5 | 0.0 |
| NewsEE framework | 52.1 | 42.8 | 38.8 | 20.2 | 17.6 | 23.5 | 754 | 5 | 5 | 2012.7 | 0.0 |
| Framework, gold triggers | 0.0 | 100.0 | 100.0 | 38.2 | 35.8 | 47.9 | 387 | 0 | 3 | 718.3 | 0.0 |

## Framework minus baseline (paired bootstrap, 1000 samples)

| metric | baseline | framework | difference | 95% CI | significant |
|---|---|---|---|---|---|
| Entity-C | 33.4 | 52.1 | +18.7 | [+15.9, +21.3] | yes |
| Trig-I | 20.6 | 42.8 | +22.2 | [+18.1, +26.4] | yes |
| Trig-C | 16.5 | 38.8 | +22.3 | [+18.3, +26.5] | yes |
| Arg-C (EM) | 6.9 | 17.6 | +10.6 | [+8.2, +13.2] | yes |
| Arg-C (BoW) | 9.8 | 23.5 | +13.7 | [+11.1, +16.6] | yes |

## Per event type (F1)

| event type | gold triggers | Trig-C baseline | Trig-C framework | Arg-C baseline | Arg-C framework |
|---|---|---|---|---|---|
| Attack | 117 | 26.1 | 40.1 | 11.1 | 16.1 |
| Military_operation | 166 | 8.5 | 39.3 | 2.6 | 13.7 |
| Conquering | 66 | 34.9 | 42.5 | 10.3 | 19.5 |
| Killing | 63 | 37.8 | 83.2 | 13.7 | 36.0 |
| Death | 47 | 27.5 | 63.2 | 13.1 | 35.1 |
| Bodily_harm | 47 | 25.9 | 58.6 | 6.7 | 29.8 |
| Catastrophe | 135 | 5.8 | 36.4 | 2.1 | 16.3 |
| Destroying | 47 | 32.2 | 58.7 | 11.0 | 19.2 |
| Damaging | 46 | 31.3 | 62.4 | 9.9 | 19.2 |
| Statement | 47 | 11.1 | 13.9 | 6.2 | 6.7 |
| Change_of_leadership | 19 | 5.3 | 15.8 | 2.7 | 12.5 |
| Arriving | 40 | 8.0 | 18.8 | 3.7 | 10.2 |

Verification removed (framework): {'argument_not_in_text': 66, 'entity_duplicate': 117, 'entity_not_in_text': 36, 'trigger_duplicate': 23, 'trigger_not_in_text': 11, 'argument_bad_role': 6, 'entity_bad_type': 2}
