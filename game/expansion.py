"""Optional fictional ethics and emergency scenarios for the classroom game.

Scenarios are invented game events, not claims about real-world incidents. They
focus on civic decision-making and humanitarian response, never operational harm.
"""
from copy import deepcopy

EMERGENCIES = {
    (2025, 4): {
        "id": "scenario-pandemic", "title": "Public health emergency",
        "text": "A fictional fast-moving pandemic scenario strains hospitals and household incomes. Choose a response that protects people and public trust.",
        "choices": [
            ["Fund hospitals and transparent public-health guidance", {"m": -18, "b": .45, "U": .2, "R": .3}],
            ["Coordinate local relief and publish regular updates", {"m": -10, "b": .35, "U": .1, "R": .35}],
            ["Delay action to avoid immediate costs", {"b": -.45, "U": -.45, "R": -.35}],
        ],
    },
    (2026, 8): {
        "id": "scenario-shooting", "title": "Community safety emergency",
        "text": "In this fictional scenario, a mass shooting has harmed a community. Prioritize survivors, affected families, and careful, verified public communication.",
        "choices": [
            ["Fund victim support and trauma-informed community care", {"m": -14, "b": .35, "U": .2, "R": .2}],
            ["Coordinate independent review and public safety services", {"m": -12, "c": 2, "b": .3}],
            ["Exploit the tragedy for campaign messaging", {"b": .2, "U": -.55, "R": -.55}],
        ],
    },
    (2028, 2): {
        "id": "scenario-war", "title": "War declared abroad",
        "text": "A fictional international conflict is declared. The game asks how leaders balance civilian protection, diplomacy, security, and public spending.",
        "choices": [
            ["Support diplomacy and humanitarian aid", {"m": -16, "b": .35, "U": .3, "R": .2}],
            ["Coordinate with allies and prepare civilian services", {"m": -12, "c": 2, "b": .2, "R": .25}],
            ["Escalate rhetoric without a relief plan", {"b": .25, "U": -.4, "R": -.4}],
        ],
    },
    (2029, 6): {
        "id": "scenario-nuclear", "title": "Nuclear detonation: humanitarian response",
        "text": "A fictional nuclear detonation has occurred overseas. This scenario contains no technical details; focus on civilian protection, emergency aid, diplomacy, and verified information.",
        "choices": [
            ["Mobilize humanitarian aid and emergency health support", {"m": -22, "b": .4, "U": .25, "R": .25}],
            ["Pursue urgent diplomacy and protect displaced civilians", {"m": -16, "c": 2, "b": .35}],
            ["Share unverified claims to gain attention", {"b": .15, "U": -.6, "R": -.6}],
        ],
    },
}

CORRUPT_ACTIONS = {
    "holiday": {"label": "Luxury holiday on public funds", "cost": 12, "boost": .45,
                "trust": .65, "note": "An improper personal trip is charged to the public budget."},
    "bias_media": {"label": "Bias public media coverage", "cost": 7, "boost": .7,
                     "trust": .8, "note": "Favorable coverage briefly helps, but media independence and trust suffer."},
    "nepotism": {"label": "Give a contract to an ally", "cost": 9, "boost": .5,
                 "trust": .75, "note": "Favoritism damages confidence in fair public procurement."},
}


def after_tick(state):
    """Attach at most one dated fictional emergency to a tick response."""
    if state.get("event") or state.get("over"):
        return state
    month = int(state.get("m", 0))
    current_year = 1991 + month // 12
    month_number = month % 12 + 1
    scenario = EMERGENCIES.get((current_year, month_number))
    if scenario:
        state = deepcopy(state)
        state["event"] = deepcopy(scenario)
        state.setdefault("log", []).append(f"{current_year}: fictional national emergency scenario begins.")
    return state


def op_corrupt(data):
    state = deepcopy(data["state"])
    action_id = data.get("action")
    action = CORRUPT_ACTIONS.get(action_id)
    if not action_id or not action:
        raise ValueError("Choose a listed fictional ethics scenario.")
    if not state.get("inpower"):
        state["flash"] = "These government-only choices are available only while your party leads government."
        return state
    if state.get("money", 0) < action["cost"]:
        state["flash"] = f"Not enough public funds for {action['label'].lower()}."
        return state
    state["money"] -= action["cost"]
    state["boost"] = state.get("boost", 0) + action["boost"]
    state["trust"] = max(0, state.get("trust", 100) - action["trust"] * 10)
    state["corruption"] = state.get("corruption", 0) + 1
    state["flash"] = f"Ethics breach: {action['note']} Simulated public trust fell by {action['trust'] * 10:.0f} points."
    state.setdefault("log", []).append(state["flash"])
    return state


def op_emergency_choice(data):
    state = deepcopy(data["state"])
    scenario = state.get("event")
    if not scenario or not str(scenario.get("id", "")).startswith("scenario-"):
        raise ValueError("There is no fictional emergency awaiting a response.")
    choices = scenario.get("choices", [])
    index = data.get("i")
    if not isinstance(index, int) or not 0 <= index < len(choices):
        raise ValueError("Choose one of the displayed response options.")
    label, effect = choices[index]
    state["boost"] = state.get("boost", 0) + effect.get("b", 0)
    state["money"] = state.get("money", 0) + effect.get("m", 0)
    state["cap"] = min(20, state.get("cap", 0) + effect.get("c", 0))
    mood = state.setdefault("mood", {"U": 0, "R": 0, "M": 0})
    mood["U"] = mood.get("U", 0) + effect.get("U", 0)
    mood["R"] = mood.get("R", 0) + effect.get("R", 0)
    mood["M"] = (mood["U"] + mood["R"]) / 2
    if "exploit" in label.lower() or "unverified" in label.lower():
        state["trust"] = max(0, state.get("trust", 100) - 12)
    state["event"] = None
    state["flash"] = f"Emergency response recorded: {label}. This was a fictional classroom scenario."
    state.setdefault("log", []).append(state["flash"])
    return state
