# Dictionary + LLM combination (dev, 30 documents)

Dictionary: 498 trigger words with annotation rate >= 50% in the training texts.

| model | system | Entity-C | Trig-I | Trig-C | Arg-C (EM) | Arg-C (BoW) | Trig-C P | Trig-C R |
|---|---|---|---|---|---|---|---|---|
| ds-flash | dictionary | 46.0 | 66.2 | 63.2 | 0.0 | 0.0 | 61.3 | 65.1 |
| ds-flash | framework | 54.8 | 56.4 | 53.2 | 27.9 | 33.0 | 42.4 | 71.3 |
| ds-flash | dictionary + framework | 54.8 | 60.7 | 57.3 | 27.9 | 32.9 | 43.6 | 83.3 |
| glm-air | dictionary | 46.0 | 66.2 | 63.2 | 0.0 | 0.0 | 61.3 | 65.1 |
| glm-air | framework | 51.4 | 42.4 | 37.6 | 17.1 | 21.4 | 29.6 | 51.5 |
| glm-air | dictionary + framework | 51.4 | 52.1 | 48.0 | 17.2 | 21.4 | 34.8 | 77.5 |

## Paired bootstrap, 1000 samples

| model | comparison | metric | A | B | B - A | 95% CI | significant |
|---|---|---|---|---|---|---|---|
| ds-flash | hybrid vs framework | Entity-C | 54.8 | 54.8 | +0.0 | [+0.0, +0.0] | no |
| ds-flash | hybrid vs framework | Trig-I | 56.4 | 60.7 | +4.4 | [+1.7, +6.9] | yes |
| ds-flash | hybrid vs framework | Trig-C | 53.2 | 57.3 | +4.1 | [+1.3, +6.8] | yes |
| ds-flash | hybrid vs framework | Arg-C (EM) | 27.9 | 27.9 | -0.0 | [-0.2, +0.1] | no |
| ds-flash | hybrid vs framework | Arg-C (BoW) | 33.0 | 32.9 | -0.1 | [-0.3, +0.1] | no |
| ds-flash | hybrid vs dictionary | Entity-C | 46.0 | 54.8 | +8.8 | [+2.6, +14.7] | yes |
| ds-flash | hybrid vs dictionary | Trig-I | 66.2 | 60.7 | -5.5 | [-12.3, +1.0] | no |
| ds-flash | hybrid vs dictionary | Trig-C | 63.2 | 57.3 | -5.9 | [-12.9, +0.5] | no |
| glm-air | hybrid vs framework | Entity-C | 51.4 | 51.4 | +0.0 | [+0.0, +0.0] | no |
| glm-air | hybrid vs framework | Trig-I | 42.4 | 52.1 | +9.7 | [+5.4, +13.4] | yes |
| glm-air | hybrid vs framework | Trig-C | 37.6 | 48.0 | +10.4 | [+6.0, +14.6] | yes |
| glm-air | hybrid vs framework | Arg-C (EM) | 17.1 | 17.2 | +0.1 | [-0.2, +0.4] | no |
| glm-air | hybrid vs framework | Arg-C (BoW) | 21.4 | 21.4 | +0.1 | [-0.3, +0.5] | no |
| glm-air | hybrid vs dictionary | Entity-C | 46.0 | 51.4 | +5.4 | [-0.2, +10.7] | no |
| glm-air | hybrid vs dictionary | Trig-I | 66.2 | 52.1 | -14.1 | [-20.1, -8.1] | yes |
| glm-air | hybrid vs dictionary | Trig-C | 63.2 | 48.0 | -15.1 | [-21.1, -9.3] | yes |

## Precision of the framework's triggers, by what the training data says about the word

Groups: in dictionary = annotated in >= 50% of its training occurrences; ambiguous = annotated as a trigger in training but in < 50% of occurrences; never a trigger = never annotated as a trigger.

| model | in dictionary: correct / predicted (P) | ambiguous | never a trigger in training |
|---|---|---|---|
| ds-flash | 137 / 215 (63.7) | 46 / 167 (27.5) | 1 / 52 (1.9) |
| glm-air | 101 / 149 (67.8) | 32 / 123 (26.0) | 0 / 178 (0.0) |
