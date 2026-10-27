# Main results: ds-flash-think (deepseek-flash) on dev (3 documents)

| setting | Entity-C | Trig-I | Trig-C | Arg-I (EM) | Arg-C (EM) | Arg-C (BoW) | calls | parse fail | blocked | tokens (k) | cost (RMB, peak) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Baseline (zero-shot, all-in-one) | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 3 | 0 | 0 | 26.7 | 0.2 |
| NewsEE framework | 62.7 | 20.0 | 20.0 | 13.3 | 13.3 | 14.0 | 9 | 0 | 0 | 55.2 | 0.33 |

## Framework minus baseline (paired bootstrap, 1000 samples)

| metric | baseline | framework | difference | 95% CI | significant |
|---|---|---|---|---|---|
| Entity-C | 0.0 | 62.7 | +62.7 | [+0.0, +94.1] | no |
| Trig-I | 0.0 | 20.0 | +20.0 | [+0.0, +66.7] | no |
| Trig-C | 0.0 | 20.0 | +20.0 | [+0.0, +66.7] | no |
| Arg-C (EM) | 0.0 | 13.3 | +13.3 | [+0.0, +33.3] | no |
| Arg-C (BoW) | 0.0 | 14.0 | +14.0 | [+0.0, +35.0] | no |

## Per event type (F1)

| event type | gold triggers | Trig-C baseline | Trig-C framework | Arg-C baseline | Arg-C framework |
|---|---|---|---|---|---|
| Attack | 0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Military_operation | 1 | 0.0 | 0.0 | 0.0 | 0.0 |
| Conquering | 2 | 0.0 | 0.0 | 0.0 | 0.0 |
| Killing | 0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Death | 2 | 0.0 | 66.7 | 0.0 | 22.2 |
| Bodily_harm | 1 | 0.0 | 100.0 | 0.0 | 50.0 |
| Catastrophe | 8 | 0.0 | 0.0 | 0.0 | 0.0 |
| Destroying | 1 | 0.0 | 0.0 | 0.0 | 0.0 |
| Damaging | 0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Statement | 1 | 0.0 | 0.0 | 0.0 | 0.0 |
| Change_of_leadership | 0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Arriving | 1 | 0.0 | 0.0 | 0.0 | 0.0 |

Verification removed (framework): {'argument_not_in_text': 0}
