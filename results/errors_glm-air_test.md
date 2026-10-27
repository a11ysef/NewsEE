# Error analysis: glm-air on test (staged_G_retrieval3_V_glm-air_test)

## Triggers

| category | count | share of all trigger decisions (%) |
|---|---|---|
| spurious | 991 | 54.1 |
| correct | 452 | 24.7 |
| missed | 341 | 18.6 |
| type confusion | 47 | 2.6 |

Of the missed triggers, 24 are further mentions of an event whose other mention was found.

Most frequent type confusions (gold -> predicted):

| gold | predicted | count |
|---|---|---|
| Conquering | Military_operation | 7 |
| Catastrophe | Destroying | 4 |
| Military_operation | Attack | 4 |
| Bodily_harm | Attack | 3 |
| Destroying | Catastrophe | 3 |
| Killing | Death | 3 |
| Conquering | Attack | 2 |
| Attack | Military_operation | 2 |
| Change_of_leadership | Conquering | 2 |
| Killing | Military_operation | 2 |

Why the spurious triggers are spurious (full MAVEN-Arg annotation):

| reason | count | share (%) |
|---|---|---|
| annotated as an event type outside the 12 | 527 | 53.2 |
| listed by MAVEN as a non-trigger candidate (negative instance) | 315 | 31.8 |
| not annotated at all | 149 | 15.0 |

Schema-boundary pairs (predicted type -> annotated type outside the 12):

| predicted | annotated | count |
|---|---|---|
| Arriving | Motion | 21 |
| Statement | Expressing_publicly | 15 |
| Arriving | Retreat | 12 |
| Attack | Terrorism | 10 |
| Conquering | Removing | 9 |
| Statement | Know | 9 |
| Arriving | Cause_change_of_strength | 9 |
| Conquering | Arrest | 8 |
| Statement | Agree_or_refuse_to_act | 7 |
| Conquering | Surrendering | 7 |

## Arguments

| category | count | share (%) |
|---|---|---|
| from wrong event | 2637 | 47.7 |
| missed (event not found) | 846 | 15.3 |
| missed (event found) | 594 | 10.7 |
| correct | 552 | 10.0 |
| spurious | 535 | 9.7 |
| boundary | 343 | 6.2 |
| wrong role | 23 | 0.4 |

## Hallucinations removed by verification

| item | count |
|---|---|
| entity_duplicate | 117 |
| argument_not_in_text | 66 |
| entity_not_in_text | 36 |
| trigger_duplicate | 23 |
| trigger_not_in_text | 11 |
| argument_bad_role | 6 |
| entity_bad_type | 2 |
