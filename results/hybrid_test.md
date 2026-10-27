# Dictionary + LLM combination (test, 120 documents)

Dictionary: 498 trigger words with annotation rate >= 50% in the training texts.

| model | system | Entity-C | Trig-I | Trig-C | Arg-C (EM) | Arg-C (BoW) | Trig-C P | Trig-C R |
|---|---|---|---|---|---|---|---|---|
| ds-flash | dictionary | 45.4 | 71.3 | 69.1 | 0.0 | 0.0 | 68.3 | 69.9 |
| ds-flash | framework | 57.4 | 60.6 | 57.5 | 26.0 | 32.4 | 46.7 | 74.6 |
| ds-flash | dictionary + framework | 57.4 | 63.5 | 60.7 | 26.3 | 32.8 | 47.3 | 84.6 |
| glm-4.7 | dictionary | 45.4 | 71.3 | 69.1 | 0.0 | 0.0 | 68.3 | 69.9 |
| glm-4.7 | framework | 57.4 | 58.6 | 55.7 | 23.9 | 30.2 | 44.7 | 74.0 |
| glm-4.7 | dictionary + framework | 57.4 | 62.2 | 59.6 | 24.0 | 30.3 | 45.7 | 85.7 |
| ds-pro | dictionary | 45.4 | 71.3 | 69.1 | 0.0 | 0.0 | 68.3 | 69.9 |
| ds-pro | framework | 57.2 | 50.5 | 47.2 | 22.7 | 28.3 | 36.5 | 66.7 |
| ds-pro | dictionary + framework | 57.2 | 56.1 | 53.3 | 22.8 | 28.4 | 39.3 | 82.7 |
| glm-air | dictionary | 45.4 | 71.3 | 69.1 | 0.0 | 0.0 | 68.3 | 69.9 |
| glm-air | framework | 52.1 | 42.8 | 38.8 | 17.6 | 23.5 | 30.3 | 53.8 |
| glm-air | dictionary + framework | 52.1 | 52.8 | 50.1 | 17.7 | 23.8 | 36.4 | 80.2 |

## Paired bootstrap, 1000 samples

| model | comparison | metric | A | B | B - A | 95% CI | significant |
|---|---|---|---|---|---|---|---|
| ds-flash | hybrid vs framework | Entity-C | 57.4 | 57.4 | +0.0 | [+0.0, +0.0] | no |
| ds-flash | hybrid vs framework | Trig-I | 60.6 | 63.5 | +2.9 | [+1.6, +4.2] | yes |
| ds-flash | hybrid vs framework | Trig-C | 57.5 | 60.7 | +3.2 | [+1.6, +4.8] | yes |
| ds-flash | hybrid vs framework | Arg-C (EM) | 26.0 | 26.3 | +0.3 | [+0.1, +0.6] | yes |
| ds-flash | hybrid vs framework | Arg-C (BoW) | 32.4 | 32.8 | +0.3 | [+0.1, +0.7] | yes |
| ds-flash | hybrid vs dictionary | Entity-C | 45.4 | 57.4 | +12.0 | [+9.1, +14.9] | yes |
| ds-flash | hybrid vs dictionary | Trig-I | 71.3 | 63.5 | -7.8 | [-10.8, -4.6] | yes |
| ds-flash | hybrid vs dictionary | Trig-C | 69.1 | 60.7 | -8.4 | [-11.4, -5.2] | yes |
| glm-4.7 | hybrid vs framework | Entity-C | 57.4 | 57.4 | +0.0 | [+0.0, +0.0] | no |
| glm-4.7 | hybrid vs framework | Trig-I | 58.6 | 62.2 | +3.6 | [+2.3, +5.1] | yes |
| glm-4.7 | hybrid vs framework | Trig-C | 55.7 | 59.6 | +3.9 | [+2.2, +5.7] | yes |
| glm-4.7 | hybrid vs framework | Arg-C (EM) | 23.9 | 24.0 | +0.1 | [-0.1, +0.3] | no |
| glm-4.7 | hybrid vs framework | Arg-C (BoW) | 30.2 | 30.3 | +0.2 | [-0.1, +0.4] | no |
| glm-4.7 | hybrid vs dictionary | Entity-C | 45.4 | 57.4 | +12.0 | [+8.9, +14.8] | yes |
| glm-4.7 | hybrid vs dictionary | Trig-I | 71.3 | 62.2 | -9.0 | [-12.1, -5.8] | yes |
| glm-4.7 | hybrid vs dictionary | Trig-C | 69.1 | 59.6 | -9.5 | [-12.5, -6.3] | yes |
| ds-pro | hybrid vs framework | Entity-C | 57.2 | 57.2 | +0.0 | [+0.0, +0.0] | no |
| ds-pro | hybrid vs framework | Trig-I | 50.5 | 56.1 | +5.6 | [+3.5, +8.1] | yes |
| ds-pro | hybrid vs framework | Trig-C | 47.2 | 53.3 | +6.1 | [+4.1, +8.8] | yes |
| ds-pro | hybrid vs framework | Arg-C (EM) | 22.7 | 22.8 | +0.1 | [-0.2, +0.3] | no |
| ds-pro | hybrid vs framework | Arg-C (BoW) | 28.3 | 28.4 | +0.1 | [-0.2, +0.4] | no |
| ds-pro | hybrid vs dictionary | Entity-C | 45.4 | 57.2 | +11.8 | [+8.5, +14.9] | yes |
| ds-pro | hybrid vs dictionary | Trig-I | 71.3 | 56.1 | -15.2 | [-18.5, -11.3] | yes |
| ds-pro | hybrid vs dictionary | Trig-C | 69.1 | 53.3 | -15.8 | [-19.2, -12.1] | yes |
| glm-air | hybrid vs framework | Entity-C | 52.1 | 52.1 | +0.0 | [+0.0, +0.0] | no |
| glm-air | hybrid vs framework | Trig-I | 42.8 | 52.8 | +9.9 | [+7.2, +12.9] | yes |
| glm-air | hybrid vs framework | Trig-C | 38.8 | 50.1 | +11.3 | [+8.4, +14.4] | yes |
| glm-air | hybrid vs framework | Arg-C (EM) | 17.6 | 17.7 | +0.2 | [-0.0, +0.3] | no |
| glm-air | hybrid vs framework | Arg-C (BoW) | 23.5 | 23.8 | +0.2 | [+0.0, +0.5] | yes |
| glm-air | hybrid vs dictionary | Entity-C | 45.4 | 52.1 | +6.7 | [+3.3, +9.8] | yes |
| glm-air | hybrid vs dictionary | Trig-I | 71.3 | 52.8 | -18.6 | [-21.5, -15.5] | yes |
| glm-air | hybrid vs dictionary | Trig-C | 69.1 | 50.1 | -19.0 | [-22.0, -16.0] | yes |

## Precision of the framework's triggers, by what the training data says about the word

Groups: in dictionary = annotated in >= 50% of its training occurrences; ambiguous = annotated as a trigger in training but in < 50% of occurrences; never a trigger = never annotated as a trigger.

| model | in dictionary: correct / predicted (P) | ambiguous | never a trigger in training |
|---|---|---|---|
| ds-flash | 503 / 699 (72.0) | 121 / 464 (26.1) | 3 / 179 (1.7) |
| glm-4.7 | 489 / 676 (72.3) | 127 / 453 (28.0) | 6 / 263 (2.3) |
| ds-pro | 452 / 626 (72.2) | 102 / 426 (23.9) | 6 / 482 (1.2) |
| glm-air | 365 / 498 (73.3) | 79 / 344 (23.0) | 8 / 648 (1.2) |
