# Error analysis: ds-pro on test (staged_G_retrieval3_V_ds-pro_test)

## Triggers

| category | count | share of all trigger decisions (%) |
|---|---|---|
| spurious | 934 | 52.6 |
| correct | 560 | 31.6 |
| missed | 240 | 13.5 |
| type confusion | 40 | 2.3 |

Of the missed triggers, 10 are further mentions of an event whose other mention was found.

Most frequent type confusions (gold -> predicted):

| gold | predicted | count |
|---|---|---|
| Catastrophe | Destroying | 3 |
| Bodily_harm | Attack | 3 |
| Military_operation | Attack | 3 |
| Destroying | Catastrophe | 3 |
| Catastrophe | Attack | 3 |
| Catastrophe | Death | 2 |
| Attack | Damaging | 2 |
| Attack | Military_operation | 2 |
| Destroying | Damaging | 2 |
| Killing | Death | 2 |

Why the spurious triggers are spurious (full MAVEN-Arg annotation):

| reason | count | share (%) |
|---|---|---|
| annotated as an event type outside the 12 | 408 | 43.7 |
| listed by MAVEN as a non-trigger candidate (negative instance) | 397 | 42.5 |
| not annotated at all | 129 | 13.8 |

Schema-boundary pairs (predicted type -> annotated type outside the 12):

| predicted | annotated | count |
|---|---|---|
| Attack | Terrorism | 17 |
| Conquering | Arrest | 16 |
| Statement | Expressing_publicly | 12 |
| Catastrophe | Motion | 10 |
| Conquering | Surrendering | 9 |
| Statement | Communication | 9 |
| Conquering | Removing | 9 |
| Attack | Use_firearm | 9 |
| Arriving | Motion | 8 |
| Military_operation | Retreat | 8 |

## Arguments

| category | count | share (%) |
|---|---|---|
| from wrong event | 2535 | 45.9 |
| correct | 729 | 13.2 |
| missed (event not found) | 692 | 12.5 |
| spurious | 627 | 11.4 |
| missed (event found) | 572 | 10.4 |
| boundary | 337 | 6.1 |
| wrong role | 28 | 0.5 |

## Hallucinations removed by verification

| item | count |
|---|---|
| entity_duplicate | 45 |
| entity_not_in_text | 22 |
| argument_not_in_text | 18 |
| trigger_duplicate | 4 |
