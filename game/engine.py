"""Game rules. State is passed in and out; it is not stored server-side."""
from copy import deepcopy
from datetime import date

from game.data import CAMPAIGNS, COUNTIES, PARTIES, POLICIES


def _party(name):
    return next((p for p in PARTIES if p["name"] == name), PARTIES[0])


def new_game(party_name="MDF", leader=""):
    party = _party(party_name)
    return {
        "date": "1991-01-01", "end_year": 2030, "party": party["name"],
        "party_color": party["color"], "leader": leader or party["name"] + " party leader",
        "mentor": "Magyar Péter", "budget": 100, "capital": 10, "support": 18,
        "seats": 0, "in_power": False, "elections_won": 0, "years_in_power": 0,
        "below_threshold": 0, "dissolved": False,
        "county_support": {c["name"]: 18 for c in COUNTIES}, "county_winners": {},
        "events_seen": [], "policies_used": [],
        "log": ["A new political era begins. Build support and manage your budget."],
        "last_election": None, "game_over": False,
    }


def _log(state, message):
    state["log"] = (state.get("log", []) + [message])[-12:]


def _date(state):
    return date.fromisoformat(state["date"])


def advance_month(state):
    state = deepcopy(state)
    if state.get("game_over") or state.get("dissolved"):
        return state
    current = _date(state)
    month = current.month + 1
    year = current.year + (1 if month > 12 else 0)
    month = 1 if month > 12 else month
    state["date"] = date(year, month, 1).isoformat()
    income = 5 + max(0, state["support"] // 10)
    if state["in_power"]:
        income += 7
    state["budget"] += income - (4 if state["budget"] >= 0 else 8)
    state["capital"] = min(20, state["capital"] + 1)
    if state["budget"] < 0:
        state["support"] = max(0, state["support"] - 1)
        _log(state, "Debt is growing: support slips and monthly costs increase.")
    if year >= 2030 and month == 12:
        state["game_over"] = True
        state["score"] = max(0, state["seats"] + state["years_in_power"] * 3 + state["budget"] // 5)
        _log(state, "The simulation ends in December 2030.")
    return state


def campaign(state, action_id, county_name=None):
    state = deepcopy(state)
    action = next((a for a in CAMPAIGNS if a["id"] == action_id), None)
    if not action:
        return state
    if state["budget"] < action["cost"]:
        _log(state, "Not enough party funds for that campaign action.")
        return state
    state["budget"] -= action["cost"]
    bonus = 0.3 if state["mentor"] == "Magyar Péter" and action_id in ("volunteers", "polling") else 0
    selected = next((c for c in COUNTIES if c["name"] == county_name), None)
    targets = [selected] if selected else COUNTIES
    for county in targets:
        value = state["county_support"].get(county["name"], 18)
        match = 1.0 if county["kind"] == action["target"] else 0.55
        state["county_support"][county["name"]] = min(65, value + (action["effect"] + bonus) * match)
    state["support"] = round(sum(state["county_support"].values()) / len(COUNTIES))
    _log(state, f"{action['name']} campaign completed.")
    return state


def enact_policy(state, policy_id):
    state = deepcopy(state)
    policy = next((p for p in POLICIES if p["id"] == policy_id), None)
    if not policy:
        return state
    if not state["in_power"]:
        _log(state, "Only the governing party can enact policies.")
        return state
    if state["budget"] < policy["cost"] or state["capital"] < policy["capital"]:
        _log(state, "Not enough money or political capital.")
        return state
    state["budget"] -= policy["cost"]
    state["capital"] -= policy["capital"]
    state["support"] = max(0, min(75, state["support"] + policy["effects"]["support"]))
    state["budget"] += policy["effects"]["budget"]
    state["policies_used"].append(policy["name"])
    for county in state["county_support"]:
        state["county_support"][county] = max(0, min(75, state["county_support"][county] + policy["effects"]["support"] * 0.5))
    _log(state, f"{policy['name']} enacted. Simplified trade-offs apply.")
    return state


def resolve_event(state, choice=0):
    state = deepcopy(state)
    event = state.get("pending_event")
    if not event:
        return state
    choice = int(choice)
    effects = event["choices"][max(0, min(choice, len(event["choices"] - 1))]["effects"]
    state["budget"] += effects.get("budget", 0)
    state["support"] = max(0, min(75, state["support"] + effects.get("support", 0)))
    state["capital"] = max(0, min(20, state["capital"] + effects.get("capital", 0)))
    state["events_seen"].append(event["id"])
    _log(state, f"Response chosen: {event['title']}.")
    state.pop("pending_event", None)
    return state


EVENTS = [
    (1991, 1, "Transition era", "Institutions and the economy are changing rapidly.", [("Invest in public services", {"budget": -8, "support": 2}), ("Prioritize fiscal stability", {"budget": 6, "support": -1})]),
    (1999, 3, "NATO accession", "Hungary joins NATO in March 1999.", [("Support cooperation", {"support": 2, "capital": 1}), ("Focus on domestic priorities", {"budget": 2})]),
    (2004, 5, "EU accession", "Hungary joins the European Union in May 2004.", [("Invest in cooperation", {"budget": -6, "support": 2}), ("Review domestic impacts", {"capital": 1, "support": 1})]),
    (2008, 9, "Financial crisis", "The global financial crisis reaches the region.", [("Protect household support", {"budget": -10, "support": 2}), ("Reduce spending", {"budget": 5, "support": -2})]),
    (2015, 9, "Migration debate", "Migration becomes a major public policy debate.", [("Coordinate public services", {"budget": -6, "support": 1}), ("Prioritize border administration", {"budget": -3, "capital": 1})]),
    (2020, 3, "COVID-19", "The COVID-19 pandemic creates public health challenges.", [("Fund health measures", {"budget": -10, "support": 2}), ("Balance services and budgets", {"budget": -4, "capital": 1})]),
    (2022, 2, "War in Ukraine", "Russia's full-scale invasion of Ukraine reshapes European policy.", [("Support humanitarian assistance", {"budget": -7, "support": 1}), ("Review energy resilience", {"budget": -5, "capital": 1})]),
]


def election(state):
    state = deepcopy(state)
    results = []
    total = 0
    won = 0
    for county in COUNTIES:
        support = state["county_support"].get(county["name"], state["support"])
        seats = 10 if county["name"] == "Budapest" else 9 if county["name"] == "Pest" else 8
        party_seats = round(seats * support / 100) if state["support"] >= 5 else 0
        total += party_seats
        other = _party(state["party"])
        winner = other["name"] if support >= 30 else "Other parties"
        state["county_winners"][county["name"]] = winner
        won += 1 if winner == other["name"] else 0
        results.append({"county": county["name"], "seats": party_seats, "winner": winner})
    state["seats"] = min(199, total)
    state["last_election"] = {"seats": state["seats"], "counties_won": won, "results": results}
    state["in_power"] = state["seats"] >= 100
    if state["in_power"]:
        state["elections_won"] += 1
        state["support"] = min(75, state["support"] + 2)
        _log(state, f"Election result: {state['seats']} simplified seats. You form a government.")
    else:
        _log(state, f"Election result: {state['seats']} simplified seats. You continue in opposition.")
    if state["support"] < 5:
        state["below_threshold"] += 1
    else:
        state["below_threshold"] = 0
    if state["below_threshold"] >= 2:
        state["dissolved"] = True
        state["game_over"] = True
        _log(state, "The party falls below the threshold in two elections and dissolves.")
    return state
