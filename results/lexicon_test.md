# Dictionary baseline versus LLM framework (test, 120 documents)

## Overall (F1)

| system | Entity-C | Trig-I | Trig-C | Arg-C (EM) | Trig-C P | Trig-C R |
|---|---|---|---|---|---|---|
| Dictionary (all entries) | 31.9 | 49.8 | 46.7 | 0.0 | 31.4 | 91.3 |
| Dictionary (rate >= 50%) | 45.4 | 71.3 | 69.1 | 0.0 | 68.3 | 69.9 |
| ds-flash zero-shot | 46.8 | 42.4 | 32.3 | 15.6 | 32.8 | 31.8 |
| ds-flash framework | 57.4 | 60.6 | 57.5 | 26.0 | 46.7 | 74.6 |
| glm-4.7 zero-shot | 49.0 | 43.9 | 34.9 | 15.6 | 32.3 | 38.1 |
| glm-4.7 framework | 57.4 | 58.6 | 55.7 | 23.9 | 44.7 | 74.0 |
| ds-pro zero-shot | 42.5 | 33.5 | 25.5 | 12.7 | 19.5 | 36.7 |
| ds-pro framework | 57.2 | 50.5 | 47.2 | 22.7 | 36.5 | 66.7 |
| glm-air zero-shot | 33.4 | 20.6 | 16.5 | 6.9 | 12.9 | 22.9 |
| glm-air framework | 52.1 | 42.8 | 38.8 | 17.6 | 30.3 | 53.8 |

## Framework minus dictionary (rate >= 50%), paired bootstrap, 1000 samples

| model | metric | dictionary | framework | difference | 95% CI | significant |
|---|---|---|---|---|---|---|
| ds-flash | Entity-C | 45.4 | 57.4 | +12.0 | [+9.1, +14.9] | yes |
| ds-flash | Trig-I | 71.3 | 60.6 | -10.7 | [-13.7, -7.5] | yes |
| ds-flash | Trig-C | 69.1 | 57.5 | -11.6 | [-14.8, -8.2] | yes |
| glm-4.7 | Entity-C | 45.4 | 57.4 | +12.0 | [+8.9, +14.8] | yes |
| glm-4.7 | Trig-I | 71.3 | 58.6 | -12.7 | [-15.7, -9.7] | yes |
| glm-4.7 | Trig-C | 69.1 | 55.7 | -13.3 | [-16.8, -10.1] | yes |
| ds-pro | Entity-C | 45.4 | 57.2 | +11.8 | [+8.5, +14.9] | yes |
| ds-pro | Trig-I | 71.3 | 50.5 | -20.8 | [-24.5, -16.8] | yes |
| ds-pro | Trig-C | 69.1 | 47.2 | -21.9 | [-25.7, -17.9] | yes |
| glm-air | Entity-C | 45.4 | 52.1 | +6.7 | [+3.3, +9.8] | yes |
| glm-air | Trig-I | 71.3 | 42.8 | -28.5 | [-31.9, -25.0] | yes |
| glm-air | Trig-C | 69.1 | 38.8 | -30.3 | [-33.9, -26.9] | yes |

## Trig-C F1 per event type (dictionary vs ds-flash framework)

| event type | gold triggers | dictionary | framework | difference |
|---|---|---|---|---|
| Attack | 117 | 65.2 | 58.7 | -6.5 |
| Military_operation | 166 | 66.0 | 56.2 | -9.8 |
| Conquering | 66 | 77.9 | 52.7 | -25.2 |
| Killing | 63 | 86.4 | 81.4 | -5.0 |
| Death | 47 | 83.5 | 76.1 | -7.4 |
| Bodily_harm | 47 | 78.3 | 64.4 | -14.0 |
| Catastrophe | 135 | 56.3 | 58.0 | +1.7 |
| Destroying | 47 | 74.7 | 68.8 | -5.9 |
| Damaging | 46 | 82.5 | 78.8 | -3.7 |
| Statement | 47 | 64.7 | 33.9 | -30.8 |
| Change_of_leadership | 19 | 46.8 | 30.4 | -16.4 |
| Arriving | 40 | 59.8 | 28.9 | -30.9 |

## Trig-C recall by whether the gold trigger word is a dictionary entry

| system | in dictionary: found / gold (recall) | not in dictionary: found / gold (recall) |
|---|---|---|
| Dictionary (all entries) | 587 / 606 (96.9) | 180 / 234 (76.9) |
| Dictionary (rate >= 50%) | 587 / 606 (96.9) | 0 / 234 (0.0) |
| ds-flash zero-shot | 240 / 606 (39.6) | 27 / 234 (11.5) |
| ds-flash framework | 503 / 606 (83.0) | 124 / 234 (53.0) |
| glm-4.7 zero-shot | 279 / 606 (46.0) | 41 / 234 (17.5) |
| glm-4.7 framework | 489 / 606 (80.7) | 133 / 234 (56.8) |
| ds-pro zero-shot | 269 / 606 (44.4) | 39 / 234 (16.7) |
| ds-pro framework | 452 / 606 (74.6) | 108 / 234 (46.2) |
| glm-air zero-shot | 167 / 606 (27.6) | 25 / 234 (10.7) |
| glm-air framework | 365 / 606 (60.2) | 87 / 234 (37.2) |

Dictionary entries: words annotated as triggers in the 1,919 training documents; the rate-50 dictionary keeps a word only if at least half of its occurrences in the training texts are annotated. 'In dictionary' = the gold trigger word is an entry that the rate-50 dictionary used in this split.
