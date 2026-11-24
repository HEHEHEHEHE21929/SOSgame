"""Stateless classroom-friendly simulation rules for Magyar Politika."""
import random
from copy import deepcopy

from .data import CAMPAIGN, COUNTIES, DIFFICULTIES, EVENTS, LEADERS, MENTORS, PARTIES, POLICIES

# Public figures used as selectable local candidates. Their county assignments in-game are fictional.
MP_CANDIDATES = [
    "Antall József", "Horn Gyula", "József Torgyán", "László Kövér",
    "Viktor Orbán", "Gergely Gulyás", "Katalin Novák", "László Surján",
    "Péter Magyar",
]
END = 479
TOTAL_SEATS = 199
COUNTY_SEATS = sum(county[2] for county in COUNTIES)
LIST_SEATS = TOTAL_SEATS - COUNTY_SEATS
MAJORITY = TOTAL_SEATS // 2 + 1
ELECTIONS = {39 + 36 * index for index in range(13)}


def year(month):
    return 1991 + int(month) // 12


def lean(party, county_type):
    urban, rural = PARTIES[party]["lean"]
    return {"U": urban, "R": rural, "M": (urban + rural) / 2}[county_type]


def baseline(party, month):
    frames = PARTIES[party]["support"]
    current_year = 1991 + month / 12
    if current_year <= frames[0][0]:
        return frames[0][1]
    for (year0, value0), (year1, value1) in zip(frames, frames[1:]):
        if current_year <= year1:
            return value0 + (value1 - value0) * (current_year - year0) / (year1 - year0)
    return frames[-1][1]


def vote_shares(state, noise=0):
    raw = {}
    for party, details in PARTIES.items():
        if party == "CUSTOM" and state["party"] != party:
            continue
        if party == state["party"]:
            value = max(baseline(party, state["m"]), 3) + state.get("boost", 0)
        elif year(state["m"]) >= details["founded"] and baseline(party, state["m"]) > .3:
            value = baseline(party, state["m"])
        else:
            continue
        raw[party] = max(.1, value) * random.uniform(1 - noise, 1 + noise)
    total = sum(raw.values()) or 1
    return {party: value * 100 / total for party, value in raw.items()}


def meta():
    return {
        "parties": {key: {"n": value["n"], "c": value["c"], "f": value["founded"]} for key, value in PARTIES.items()},
        "campaign": CAMPAIGN, "policies": POLICIES, "mentors": MENTORS,
        "leaders": LEADERS, "counties": COUNTIES, "difficulties": DIFFICULTIES,
        "mp_candidates": MP_CANDIDATES,
        "election": {"total_seats": TOTAL_SEATS, "county_seats": COUNTY_SEATS,
                     "list_seats": LIST_SEATS, "majority": MAJORITY, "threshold": 5},
    }


def op_new(data):
    party = str(data.get("party", "MDF"))
    if party not in PARTIES:
        raise ValueError("Choose a known party.")
    difficulty = str(data.get("difficulty", "normal"))
    if difficulty not in DIFFICULTIES:
        difficulty = "normal"
    settings = DIFFICULTIES[difficulty]
    mentor = data.get("mentor", "magyar")
    if mentor not in MENTORS:
        mentor = "magyar"
    leader = str(data.get("leader") or LEADERS.get(party, ["Party founder"])[0]).strip()[:60]
    pname = str(data.get("pname") or PARTIES[party]["n"]).strip()[:40] or "My Party"
    state = {
        "m": 0, "party": party, "pname": pname, "leader": leader,
        "mentor": mentor, "difficulty": difficulty,
        "money": settings["money"], "cap": settings["capital"], "boost": 0.0,
        "mood": {"U": 0.0, "R": 0.0, "M": 0.0}, "spent": {}, "reg": False,
        "polls": 0, "inpower": False, "seats": 0, "wins": [], "hist": [],
        "below": 0, "years_power": 0.0,
        "log": ["January 1991: the democratic era begins."],
        "event": None, "over": None, "result": None, "poll": {}, "flash": None,
        "score": 0, "founded_seen": [], "county_mps": {}, "county_support": {},
        "policy_history": [], "challenge_rewards": [],
    }
    state["poll"] = {key: round(value, 1) for key, value in vote_shares(state, settings["noise"]).items()}
    return state


def largest_remainder(values, total):
    """Allocate integer seats proportionally using the largest-remainder method."""
    if total < 0:
        raise ValueError("Seat total cannot be negative.")
    if not values or total == 0:
        return dict.fromkeys(values, 0)
    denominator = sum(values.values())
    if denominator <= 0:
        return dict.fromkeys(values, 0)
    exact = {key: value * total / denominator for key, value in values.items()}
    allocated = {key: int(value) for key, value in exact.items()}
    remaining = total - sum(allocated.values())
    order = sorted(exact, key=lambda key: (exact[key] - allocated[key], str(key)), reverse=True)
    for key in order[:remaining]:
        allocated[key] += 1
    return allocated


def run_election(state):
    player = state["party"]
    difficulty = DIFFICULTIES.get(state.get("difficulty", "normal"), DIFFICULTIES["normal"])
    shares = vote_shares(state, difficulty["noise"])
    if not state.get("reg"):
        shares[player] *= .6
        total = sum(shares.values()) or 1
        shares = {party: value * 100 / total for party, value in shares.items()}
    eligible = {party: share for party, share in shares.items() if share >= 5}
    excluded = {party: round(share, 1) for party, share in shares.items() if share < 5}
    if not eligible:
        leader = max(shares, key=shares.get)
        eligible = {leader: shares[leader]}

    seats = dict.fromkeys(shares, 0)
    winners = []
    difficulty_bonus = {"easy": 1.12, "normal": 1.0, "hard": .90}.get(state.get("difficulty"), 1.0)
    local_candidates = state.get("county_mps", {})
    local_support = state.get("county_support", {})
    for index, (_name, county_type, constituency_seats) in enumerate(COUNTIES):
        scores = {
            party: share * lean(party, county_type) * random.uniform(.92, 1.08)
            + (state.get("mood", {}).get(county_type, 0) * 2 if party == player and state.get("inpower") else 0)
            for party, share in eligible.items()
        }
        if player in scores:
            local_edge = min(.12, max(0, float(local_support.get(str(index), 0)) * .02))
            candidate_edge = .03 if str(index) in local_candidates else 0
            scores[player] *= difficulty_bonus + local_edge + candidate_edge
        winner = max(scores, key=scores.get)
        seats[winner] += constituency_seats
        winners.append(winner)

    list_allocations = largest_remainder(eligible, LIST_SEATS)
    for party, count in list_allocations.items():
        seats[party] += count
    ranked = sorted(seats, key=lambda key: (seats[key], key == player), reverse=True)
    government = ranked[0]
    coalition = ranked[1] if seats[government] < MAJORITY and len(ranked) > 1 else None
    if coalition and seats[government] + seats[coalition] < MAJORITY:
        coalition = None

    state["inpower"] = government == player or coalition == player
    state["seats"] = seats.get(player, 0)
    state["wins"] = winners
    share = shares.get(player, 0)
    state["below"] = state.get("below", 0) + 1 if share < 5 else 0
    state["result"] = {
        "year": year(state["m"]), "shares": {party: round(value, 1) for party, value in shares.items()},
        "seats": seats, "county_winners": winners, "list_seats": list_allocations,
        "excluded_from_list": excluded, "gov": government, "coalition": coalition,
        "maj": MAJORITY, "total_seats": TOTAL_SEATS,
        "supermaj": seats[government] * 3 >= TOTAL_SEATS * 2,
        "lesson": f"The simulation allocates {COUNTY_SEATS} county seats plus {LIST_SEATS} proportional list seats. Parties below 5% do not receive list seats.",
    }
    state.setdefault("hist", []).append({"year": year(state["m"]), "seats": state["seats"], "gov": government, "share": round(share, 1)})
    state.setdefault("log", []).append(f"{year(state['m'])} simulated election: {state['seats']} of {TOTAL_SEATS} seats; list seats use proportional allocation with a 5% threshold.")
    state["reg"] = False
    state["spent"] = {}
    state["county_support"] = {}
    if state["inpower"]:
        state["cap"] = min(20, state["cap"] + 3)
    if state["below"] >= 2:
        state["over"] = "dissolved"
        finish(state)


def finish(state):
    state["over"] = state.get("over") or "end"
    state["score"] = sum(item["seats"] for item in state.get("hist", [])) + round(state.get("years_power", 0) * 8) + max(0, round(state.get("money", 0) / 10))


def op_tick(data):
    state = deepcopy(data["state"])
    if state.get("over") or state.get("event"):
        return state
    state["result"] = None
    state["flash"] = None
    state["m"] = min(state["m"] + 1, END)
    current_year = year(state["m"])
    month_number = state["m"] % 12 + 1
    mentor = MENTORS.get(state.get("mentor"), MENTORS["magyar"])["bonus"]
    state["money"] = state.get("money", 0) + 1.5 + state.get("poll", {}).get(state["party"], 0) * .25 + state.get("seats", 0) * .05 - 2
    state["cap"] = min(20, state.get("cap", 0) + (1 if state.get("inpower") else .3) + mentor.get("cap", 0))
    state["boost"] = state.get("boost", 0) * (.965 if state.get("inpower") else .975)
    state.setdefault("mood", {"U": 0.0, "R": 0.0, "M": 0.0})
    for group in "UR":
        state["mood"][group] *= .98
    state["mood"]["M"] = (state["mood"]["U"] + state["mood"]["R"]) / 2
    if state["money"] < 0:
        state["boost"] -= .08
    if state.get("inpower"):
        state["years_power"] = state.get("years_power", 0) + 1 / 12
    state["polls"] = max(0, state.get("polls", 0) - 1)
    settings = DIFFICULTIES.get(state.get("difficulty", "normal"), DIFFICULTIES["normal"])
    state["poll"] = {party: round(value, 1) for party, value in vote_shares(state, .02 if state["polls"] else settings["noise"]).items()}

    if month_number == 1:
        for party, details in PARTIES.items():
            if details["founded"] == current_year and current_year > 1991 and party != "CUSTOM" and party not in state.setdefault("founded_seen", []):
                state["founded_seen"].append(party)
                state["event"] = {"id": "new-" + party, "title": "New party founded!", "text": f"{details['n']} enters the political landscape in this game year.", "choices": [["Continue", {}]]}
                state.setdefault("log", []).append(f"{current_year}: {details['n']} founded in this simulation.")
                break
    if not state.get("event"):
        for item in EVENTS:
            if item["y"] == current_year and item["mo"] == month_number:
                state["event"] = deepcopy(item)
                break
    if state["m"] in ELECTIONS:
        run_election(state)
    if state["m"] >= END:
        finish(state)
    return state


def op_campaign(data):
    state = deepcopy(data["state"])
    action = data.get("action")
    if action not in CAMPAIGN:
        raise ValueError("Unknown campaign action.")
    label, cost, gain = CAMPAIGN[action]
    bonus = MENTORS.get(state.get("mentor"), MENTORS["magyar"])["bonus"]
    if state.get("money", 0) < cost:
        state["flash"] = "Not enough money for that action."
        return state
    state["money"] -= cost
    if action == "reg":
        state["reg"] = True
        state["flash"] = "Candidates registered for the next election; the unregistered-ballot penalty is removed."
        return state
    if action == "poll":
        state["polls"] = 6
        state["flash"] = "More accurate polling is active for six months."
        return state
    if action in ("tv", "social"):
        gain *= 1 + bonus.get("tv", 0)
    if action == "vol":
        gain *= 1 + bonus.get("vol", 0)
    if action == "social" and year(state["m"]) >= 2010:
        gain *= 1.5
    index = data.get("county")
    if index is not None:
        if not isinstance(index, int) or not 0 <= index < len(COUNTIES):
            raise ValueError("Choose a county on the map first.")
        key = str(index)
        support = state.setdefault("county_support", {})
        actual_gain = gain / (1 + state.setdefault("spent", {}).get(action, 0) / 60)
        support[key] = support.get(key, 0) + actual_gain
        state["spent"][action] = state["spent"].get(action, 0) + cost
        state["flash"] = f"{label} campaign held in {COUNTIES[index][0]}; local support increased by {actual_gain:.2f} (diminishing returns apply)."
    else:
        spent = state.setdefault("spent", {})
        actual_gain = gain / (1 + spent.get(action, 0) / 60)
        spent[action] = spent.get(action, 0) + cost
        state["boost"] = state.get("boost", 0) + actual_gain
        state["flash"] = f"{label}: national support increased by {actual_gain:.2f}; repeated actions have diminishing returns."
    state.setdefault("log", []).append(state["flash"])
    return state


def op_policy(data):
    state = deepcopy(data["state"])
    policy = next((item for item in POLICIES if item["id"] == data.get("id")), None)
    if policy is None:
        raise ValueError("Unknown policy.")
    if not state.get("inpower"):
        state["flash"] = "Policy not enacted: your party must lead the government."
    elif state.get("cap", 0) < policy["cap"] or state.get("money", 0) < policy["cost"]:
        state["flash"] = "Policy not enacted: insufficient political capital or funds."
    else:
        state["cap"] -= policy["cap"]
        state["money"] -= policy["cost"]
        mentor_bonus = MENTORS.get(state.get("mentor"), MENTORS["magyar"])["bonus"].get("anti", 0) if policy["id"] == "anti" else 0
        state["boost"] = state.get("boost", 0) + policy["b"] + mentor_bonus
        state.setdefault("mood", {"U": 0, "R": 0, "M": 0})
        state["mood"]["U"] += policy["U"]
        state["mood"]["R"] += policy["R"]
        state.setdefault("policy_history", []).append({"id": policy["id"], "label": policy["label"], "year": year(state["m"]), "status": "enacted"})
        state["flash"] = f"POLICY ENACTED: {policy['label']}. Helps {policy['win']}; trade-off {policy['lose']}."
        state.setdefault("log", []).append(state["flash"])
    return state


def op_appoint(data):
    state = deepcopy(data["state"])
    index = data.get("county")
    name = str(data.get("name", "")).strip()[:80]
    if not isinstance(index, int) or not 0 <= index < len(COUNTIES):
        raise ValueError("Select a county first.")
    if name not in MP_CANDIDATES:
        raise ValueError("Choose a listed Hungarian public figure for the local candidate.")
    if state.get("money", 0) < 2:
        state["flash"] = "Not appointed: you need 2 M Ft for local organizing."
        return state
    state["money"] -= 2
    state.setdefault("county_mps", {})[str(index)] = name
    state["flash"] = f"{name} recruited as your local game candidate for {COUNTIES[index][0]} (2 M Ft)."
    state.setdefault("log", []).append(state["flash"])
    return state


def op_choice(data):
    state = deepcopy(data["state"])
    event = state.get("event")
    if not event:
        raise ValueError("There is no event waiting for a choice.")
    choices = event.get("choices", [])
    index = data.get("i")
    if not isinstance(index, int) or not 0 <= index < len(choices):
        raise ValueError("Choose one of the displayed event options.")
    effect = choices[index][1]
    state["boost"] = state.get("boost", 0) + effect.get("b", 0)
    state["money"] += effect.get("m", 0)
    state["cap"] = min(20, state["cap"] + effect.get("c", 0))
    state.setdefault("mood", {"U": 0, "R": 0, "M": 0})
    state["mood"]["U"] += effect.get("U", 0)
    state["mood"]["R"] += effect.get("R", 0)
    state["event"] = None
    state["flash"] = f"Decision recorded: {choices[index][0]}. {event.get('text', '')}"
    state.setdefault("log", []).append(state["flash"])
    return state


def op_mentor(data):
    state = deepcopy(data["state"])
    mentor = data.get("mentor")
    if mentor not in MENTORS:
        raise ValueError("Choose a known mentor.")
    state["mentor"] = mentor
    state["flash"] = f"Mentor selected: {MENTORS[mentor]['n']}."
    return state
