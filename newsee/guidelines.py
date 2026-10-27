"""Annotation guidelines injected into prompts when the 'guidelines' module is on.

Written from the MAVEN-Arg annotation conventions observed in the training data
and from the error patterns of the zero-shot baseline (type confusion between
conflict types; only the first occurrence of a repeated trigger being labelled).
"""
from .schema import ENTITY_TYPES, SCHEMA

ENTITY_RULES = """Entity annotation rules:
- Annotate named entities AND other mentions that refer to them: nominal phrases ("the plane", "the storm"), subject/object pronouns ("he", "she", "they", "him"), and nationality/group words ("British", "Ottomans").
- Do NOT annotate possessive pronouns ("his", "her", "their", "its"), dates or years ("3 January 1992", "2013").
- Numbers, quantities, ordinals and durations ("13", "two", "3rd", "two days") are entities of type Other.
- Annotate every occurrence, including repeated mentions of the same entity.
- Nationality or group words are typed by what they refer to: a country/place -> Location, an army/state/organisation -> Organization, a people -> Person."""

TRIGGER_RULES = """Trigger annotation rules:
- A trigger is the single word (sometimes a short phrase) that most clearly expresses the event; it can be a verb ("attacked") or a noun ("attack", "war", "fires").
- Annotate EVERY occurrence: if the same event is mentioned several times ("the fires ... the fires ..."), list each occurrence as a separate entry.
- Only annotate the 12 event types below; ignore other kinds of events.
- Disambiguation:
  * Military_operation = a war, battle, campaign or siege as a whole; Attack = one specific assault, bombing, raid, shelling or ambush.
  * Conquering = capturing or taking control of a place or group (captured, seized, took, defeated and occupied).
  * Killing = someone or something kills (killed, massacre, slain, executed); Death = the dying itself (died, death, dead, fatalities).
  * Catastrophe = the disaster event itself (storm, hurricane, fire, flood, crash, accident); Destroying = something is completely destroyed; Damaging = something is damaged but not destroyed.
  * Bodily_harm = injury or wounding (injured, wounded, injuries)."""

ARGUMENT_RULES = """Argument annotation rules:
- Arguments may be anywhere in the document, not only in the trigger's sentence.
- Copy the SHORTEST span that fully identifies the argument: prefer a name ("Seneca") over a longer phrase ("the Seneca in particular"); for people counts keep the number phrase ("30 such individuals").
- A role may have several arguments; omit a role if the document does not mention it.
- Consequence/Loss/Message/Details roles are usually clauses or longer phrases; copy them as written."""


def entity_block(with_defs):
    if not with_defs:
        return "Entity types: " + ", ".join(ENTITY_TYPES)
    lines = "\n".join(f"- {t}: {d}" for t, d in ENTITY_TYPES.items())
    return f"Entity types:\n{lines}\n\n{ENTITY_RULES}"


def event_type_block(with_defs, types=None):
    types = types or list(SCHEMA)
    if not with_defs:
        return "Event types: " + ", ".join(types)
    lines = []
    for t in types:
        s = SCHEMA[t]
        lines.append(f"- {t}: {s['definition']} (e.g. {', '.join(s['triggers'][:4])})")
    return "Event types:\n" + "\n".join(lines) + "\n\n" + TRIGGER_RULES


def role_block(event_type, with_defs):
    roles = SCHEMA[event_type]["roles"]
    if not with_defs:
        return f"Roles of {event_type}: " + ", ".join(roles)
    lines = "\n".join(f"- {r}: {d}" for r, d in roles.items())
    return (f"Event type {event_type}: {SCHEMA[event_type]['definition']}\nRoles:\n{lines}\n\n"
            f"{ARGUMENT_RULES}")
