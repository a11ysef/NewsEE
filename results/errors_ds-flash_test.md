# Error analysis: ds-flash on test (staged_G_retrieval3_V_ds-flash_test)

## Triggers

| category | count | share of all trigger decisions (%) |
|---|---|---|
| spurious | 681 | 44.8 |
| correct | 627 | 41.2 |
| missed | 179 | 11.8 |
| type confusion | 34 | 2.2 |

Of the missed triggers, 8 are further mentions of an event whose other mention was found.

Most frequent type confusions (gold -> predicted):

| gold | predicted | count |
|---|---|---|
| Attack | Military_operation | 4 |
| Catastrophe | Destroying | 3 |
| Catastrophe | Bodily_harm | 3 |
| Military_operation | Attack | 3 |
| Destroying | Catastrophe | 3 |
| Destroying | Conquering | 2 |
| Attack | Damaging | 2 |
| Killing | Death | 2 |
| Catastrophe | Arriving | 2 |
| Military_operation | Change_of_leadership | 1 |

Why the spurious triggers are spurious (full MAVEN-Arg annotation):

| reason | count | share (%) |
|---|---|---|
| listed by MAVEN as a non-trigger candidate (negative instance) | 423 | 62.1 |
| annotated as an event type outside the 12 | 205 | 30.1 |
| not annotated at all | 53 | 7.8 |

Schema-boundary pairs (predicted type -> annotated type outside the 12):

| predicted | annotated | count |
|---|---|---|
| Attack | Terrorism | 16 |
| Conquering | Arrest | 12 |
| Statement | Expressing_publicly | 10 |
| Statement | Communication | 10 |
| Catastrophe | Motion | 9 |
| Conquering | Releasing | 8 |
| Arriving | Retreat | 7 |
| Conquering | Removing | 7 |
| Conquering | Surrendering | 6 |
| Arriving | Motion | 6 |

## Arguments

| category | count | share (%) |
|---|---|---|
| from wrong event | 1892 | 38.6 |
| correct | 761 | 15.5 |
| spurious | 647 | 13.2 |
| missed (event found) | 640 | 13.1 |
| missed (event not found) | 572 | 11.7 |
| boundary | 352 | 7.2 |
| wrong role | 33 | 0.7 |

## Hallucinations removed by verification

| item | count |
|---|---|
| entity_duplicate | 45 |
| entity_not_in_text | 23 |
| argument_not_in_text | 18 |
| trigger_duplicate | 3 |
| trigger_not_in_text | 1 |
