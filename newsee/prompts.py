"""Prompt templates.

Week 1 only contains the naive all-in-one baseline (type and role NAMES only, no
definitions, no demonstrations). The framework prompts (guidelines, decomposition,
retrieved demonstrations, verification) are added in week 2 so that every module
can be switched on/off for the ablation study.
"""
import json

from .schema import ENTITY_TYPES, EVENT_TYPES, roles_of

SYSTEM = "You are a precise information extraction system. You only output valid JSON."

OUTPUT_FORMAT = {
    "entities": [{"text": "<entity mention copied from the text>", "type": "<entity type>"}],
    "events": [{
        "trigger": "<word or short phrase in the text that signals the event>",
        "type": "<event type>",
        "arguments": {"<role>": ["<argument span copied from the text>"]},
    }],
}


def baseline_all_in_one(text):
    type_lines = "\n".join(f"- {t}: roles = {', '.join(roles_of(t))}" for t in EVENT_TYPES)
    user = f"""Extract entities and events from the document below.

Entity types: {', '.join(ENTITY_TYPES)}

Event types and their argument roles:
{type_lines}

Rules:
1. Copy every entity mention, trigger and argument exactly as it appears in the document.
2. List every entity mention (including repeated mentions of the same entity).
3. Create one event entry for every trigger occurrence of the event types above. Ignore other kinds of events.
4. Arguments may appear anywhere in the document, not only in the trigger's sentence. Omit roles with no argument.

Return a JSON object in exactly this format:
{json.dumps(OUTPUT_FORMAT, indent=2)}

Document:
{text}"""
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]


def to_prediction(doc_id, obj):
    """Coerce a parsed LLM reply into the scorer's prediction format."""
    obj = obj or {}
    ents = [{"text": str(e.get("text", "")), "type": str(e.get("type", ""))}
            for e in obj.get("entities", []) or [] if isinstance(e, dict)]
    evs = []
    for e in obj.get("events", []) or []:
        if not isinstance(e, dict):
            continue
        args = e.get("arguments") or {}
        if not isinstance(args, dict):
            args = {}
        clean = {}
        for r, v in args.items():
            vals = v if isinstance(v, list) else [v]
            vals = [str(x) for x in vals if isinstance(x, (str, int, float)) and str(x).strip()]
            if vals:
                clean[str(r)] = vals
        evs.append({"trigger": str(e.get("trigger", "")), "type": str(e.get("type", "")), "arguments": clean})
    return {"id": doc_id, "entities": ents, "events": evs}
