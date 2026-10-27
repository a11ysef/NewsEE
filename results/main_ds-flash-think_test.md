# Main results: ds-flash-think (deepseek-flash) on test (120 documents)

| setting | Entity-C | Trig-I | Trig-C | Arg-I (EM) | Arg-C (EM) | Arg-C (BoW) | calls | parse fail | blocked | tokens (k) | cost (RMB, peak) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Baseline (zero-shot, all-in-one) | 9.2 | 1.9 | 1.2 | 0.9 | 0.2 | 0.4 | 120 | 1 | 0 | 1049.0 | 7.82 |
| NewsEE framework | 13.0 | 36.2 | 35.3 | 16.4 | 15.7 | 19.0 | 414 | 4 | 0 | 3020.7 | 18.21 |

## Framework minus baseline (paired bootstrap, 1000 samples)

| metric | baseline | framework | difference | 95% CI | significant |
|---|---|---|---|---|---|
| Entity-C | 9.2 | 13.0 | +3.8 | [-2.9, +10.3] | no |
| Trig-I | 1.9 | 36.2 | +34.4 | [+25.4, +42.5] | yes |
| Trig-C | 1.2 | 35.3 | +34.1 | [+25.4, +42.2] | yes |
| Arg-C (EM) | 0.2 | 15.7 | +15.4 | [+10.9, +20.2] | yes |
| Arg-C (BoW) | 0.4 | 19.0 | +18.6 | [+13.7, +23.6] | yes |

## Per event type (F1)

| event type | gold triggers | Trig-C baseline | Trig-C framework | Arg-C baseline | Arg-C framework |
|---|---|---|---|---|---|
| Attack | 117 | 0.0 | 36.2 | 0.0 | 10.8 |
| Military_operation | 166 | 0.0 | 25.7 | 0.0 | 9.7 |
| Conquering | 66 | 0.0 | 25.5 | 0.0 | 15.0 |
| Killing | 63 | 3.1 | 63.9 | 0.0 | 35.1 |
| Death | 47 | 0.0 | 50.0 | 0.0 | 29.2 |
| Bodily_harm | 47 | 0.0 | 33.3 | 0.0 | 25.9 |
| Catastrophe | 135 | 2.9 | 33.5 | 0.0 | 3.3 |
| Destroying | 47 | 0.0 | 56.7 | 0.0 | 29.7 |
| Damaging | 46 | 0.0 | 27.6 | 0.0 | 9.5 |
| Statement | 47 | 7.8 | 34.0 | 5.1 | 21.1 |
| Change_of_leadership | 19 | 0.0 | 10.5 | 0.0 | 2.9 |
| Arriving | 40 | 0.0 | 29.6 | 0.0 | 17.6 |

Verification removed (framework): {'argument_not_in_text': 2, 'entity_duplicate': 4}
