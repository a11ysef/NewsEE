"""Event schema used in NewsEE.

12 MAVEN-Arg event types grouped into 4 news themes. Role inventories are
taken from the MAVEN-Arg training data (all roles that occur for each type).
Definitions are written for this project in plain English so they can be
injected into prompts (the "guideline" module of the framework).
"""

ENTITY_TYPES = {
    "Person": "a named or described human individual or group of people",
    "Organization": "a company, army, government body, team, party or other organised group",
    "Location": "a geographic place: country, city, region, body of water, battlefield, etc.",
    "Building": "a man-made structure or facility: hotel, fort, bridge, airport, etc.",
    "Product": "a man-made object or product: vehicle, ship, aircraft, weapon model, etc.",
    "Art": "a creative work: book, film, song, painting, etc.",
    "Other": "any other named thing relevant to events (e.g. nationalities, named events, ideologies)",
}

THEMES = {
    "conflict": ["Attack", "Military_operation", "Conquering"],
    "casualty": ["Killing", "Death", "Bodily_harm"],
    "disaster": ["Catastrophe", "Destroying", "Damaging"],
    "politics": ["Statement", "Change_of_leadership", "Arriving"],
}

EVENT_TYPES = [t for ts in THEMES.values() for t in ts]

# definition, typical triggers (examples only), role -> definition
SCHEMA = {
    "Attack": {
        "definition": "An agent physically assaults or launches a violent attack on a target (bombing, ambush, raid, shooting, assault).",
        "triggers": ["attack", "assaulted", "ambushed", "bombing", "raid", "fire"],
        "roles": {
            "Agent": "the attacker",
            "Patient": "the target being attacked",
            "Location": "where the attack happens",
            "Consequence": "the result of the attack (e.g. casualties, what was gained)",
        },
    },
    "Military_operation": {
        "definition": "Organised armed conflict between forces: a war, battle, campaign, siege or military operation as a whole.",
        "triggers": ["war", "battle", "fought", "campaign", "siege", "conflict"],
        "roles": {
            "Agent": "a side conducting the operation",
            "Patient": "the opposing side the operation is directed against",
            "Location": "where the operation takes place",
        },
    },
    "Conquering": {
        "definition": "An agent takes control of a place or group by force (capture, seize, conquer, occupy).",
        "triggers": ["captured", "conquer", "seized", "taken", "occupied"],
        "roles": {
            "Agent": "the conqueror",
            "Patient": "the party that loses control",
            "Location": "the place that is captured or where it happens",
            "Name": "the name of the conquest event (e.g. 'The Battle of Malacca')",
        },
    },
    "Killing": {
        "definition": "A killer causes the death of a victim (an agent is responsible for the death).",
        "triggers": ["killed", "killing", "murdered", "massacre", "executed"],
        "roles": {
            "Killer": "the person or force that kills",
            "Victim": "who is killed",
            "Location": "where the killing happens",
            "Cause": "the event or thing causing the death",
            "Instrument": "the weapon or means used",
        },
    },
    "Death": {
        "definition": "Someone dies, with focus on the death itself rather than on a killer.",
        "triggers": ["died", "death", "dead", "deaths", "perished"],
        "roles": {
            "Agent": "who dies (person, people or a count such as 'seven')",
            "Cause": "what caused the death (e.g. a bombing, a crash, a cyclone)",
            "Location": "where the death happens",
            "Instrument": "the means of death",
        },
    },
    "Bodily_harm": {
        "definition": "Someone is physically injured or wounded.",
        "triggers": ["injured", "wounded", "injuries", "hurt", "suffered"],
        "roles": {
            "Agent": "who or what causes the injury",
            "Patient": "who is injured",
            "Location": "where the injury happens",
            "Cause": "the event causing the injury",
        },
    },
    "Catastrophe": {
        "definition": "A natural or man-made disaster happens (storm, flood, earthquake, crash, fire, accident).",
        "triggers": ["hurricane", "storm", "flood", "earthquake", "crash", "disaster"],
        "roles": {
            "Patient": "the entity or area affected by the disaster",
            "Location": "where the disaster happens",
            "Loss": "the losses caused (deaths, damage, destroyed homes)",
            "Content": "what kind of disaster it is (e.g. 'industrial disaster', 'a derailment')",
        },
    },
    "Destroying": {
        "definition": "Something is destroyed completely (destroyed, demolished, sunk, burned down).",
        "triggers": ["destroyed", "destruction", "demolished", "sank", "capsized"],
        "roles": {
            "Agent": "who or what destroys",
            "Patient": "what is destroyed",
            "Location": "where it happens",
            "Loss": "the losses resulting from the destruction",
        },
    },
    "Damaging": {
        "definition": "Something is damaged but not completely destroyed.",
        "triggers": ["damage", "damaged", "struck", "battered"],
        "roles": {
            "Agent": "who or what causes the damage",
            "Patient": "what is damaged",
            "Location": "where it happens",
            "Loss": "the amount or extent of damage (e.g. '1,700 homes', '$86.4 million')",
        },
    },
    "Statement": {
        "definition": "A speaker communicates a message (says, states, announces, describes, reports).",
        "triggers": ["said", "stated", "announced", "described", "reported"],
        "roles": {
            "Speaker": "who makes the statement",
            "Message": "what is communicated",
            "Location": "where the statement is made",
            "Details": "additional characterisation in the statement (e.g. 'one of the most horrific massacres')",
        },
    },
    "Change_of_leadership": {
        "definition": "Leadership or control of a polity or organisation changes (election, coup, revolution, ousting, independence, replacement of a leader).",
        "triggers": ["elected", "coup", "revolution", "ousted", "replaced", "independence"],
        "roles": {
            "New_leader": "who becomes the leader",
            "Old_leader": "who loses leadership",
            "Location": "the polity or place whose leadership changes",
            "Selector": "who brings about the change (voters, revolutionaries, an organisation)",
            "New_Occupation": "the position the new leader takes",
            "Old_Occupation": "the position the old leader leaves",
        },
    },
    "Arriving": {
        "definition": "An agent arrives at or reaches a place.",
        "triggers": ["arrived", "reached", "entered", "landed", "approached"],
        "roles": {
            "Agent": "who or what arrives",
            "Location": "the place arrived at",
        },
    },
}

assert set(SCHEMA) == set(EVENT_TYPES)


def roles_of(event_type):
    return list(SCHEMA[event_type]["roles"])
