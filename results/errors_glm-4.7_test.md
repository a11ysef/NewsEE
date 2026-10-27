# Error analysis: glm-4.7 on test (staged_G_retrieval3_V_glm-4.7_test)

## Triggers

| category | count | share of all trigger decisions (%) |
|---|---|---|
| spurious | 738 | 46.8 |
| correct | 622 | 39.4 |
| missed | 186 | 11.8 |
| type confusion | 32 | 2.0 |

Of the missed triggers, 12 are further mentions of an event whose other mention was found.

Most frequent type confusions (gold -> predicted):

| gold | predicted | count |
|---|---|---|
| Military_operation | Attack | 5 |
| Catastrophe | Destroying | 3 |
| Attack | Military_operation | 3 |
| Destroying | Catastrophe | 3 |
| Killing | Death | 3 |
| Attack | Bodily_harm | 2 |
| Military_operation | Change_of_leadership | 1 |
| Attack | Arriving | 1 |
| Damaging | Destroying | 1 |
| Destroying | Attack | 1 |

Why the spurious triggers are spurious (full MAVEN-Arg annotation):

| reason | count | share (%) |
|---|---|---|
| listed by MAVEN as a non-trigger candidate (negative instance) | 433 | 58.7 |
| annotated as an event type outside the 12 | 245 | 33.2 |
| not annotated at all | 60 | 8.1 |

Schema-boundary pairs (predicted type -> annotated type outside the 12):

| predicted | annotated | count |
|---|---|---|
| Attack | Terrorism | 16 |
| Conquering | Arrest | 12 |
| Arriving | Motion | 9 |
| Catastrophe | Motion | 9 |
| Statement | Communication | 8 |
| Arriving | Retreat | 7 |
| Conquering | Surrendering | 7 |
| Statement | Expressing_publicly | 7 |
| Military_operation | Besieging | 6 |
| Arriving | Removing | 5 |

## Arguments

| category | count | share (%) |
|---|---|---|
| from wrong event | 2249 | 41.1 |
| spurious | 867 | 15.8 |
| correct | 774 | 14.1 |
| missed (event not found) | 612 | 11.2 |
| missed (event found) | 574 | 10.5 |
| boundary | 366 | 6.7 |
| wrong role | 32 | 0.6 |

## Hallucinations removed by verification

| item | count |
|---|---|
| entity_duplicate | 68 |
| entity_not_in_text | 33 |
| argument_bad_role | 10 |
| argument_not_in_text | 7 |
| trigger_duplicate | 4 |
| trigger_not_in_text | 3 |
| entity_bad_type | 1 |
