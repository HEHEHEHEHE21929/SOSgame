"""Stateless simulation rules for Magyar Politika."""
import random
from copy import deepcopy

from .data import CAMPAIGN, COUNTIES, DIFFICULTIES, EVENTS, LEADERS, MENTORS, PARTIES, POLICIES

END = 479  # December 2030 when January 1991 is month zero.
ELECTIONS = {39 + 36 * index for index in range(13)}  # First: April 1994.


def year(month):
    return 1991 + int(month) // 12


def month_name(month):
    return ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")[int(month) % 12]


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
            value = max(baseline(party, state["m"]), 3) + state["boost"]
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
        "campaign": CAMPAIGN,
        "policies": POLICIES,
        "mentors": MENTORS,
        "leaders": LEADERS,
        "counties": COUNTIES,
        "difficulties": DIFFICULTIES,
    }


def op_new(data):
    party = str(data.get("party", "MDF"))
    if party not in PARTIES:
        raise ValueError("Choose a known party.")
    difficulty = str(data.get("difficulty", "normal"))
    if difficulty not in DIFFICULTIES:
        difficulty = "normal"
    settings = DIFFICULTIES[difficulty]
    leader = str(data.get("leader") or LEADERS.get(party, ["Party founder"])[0])[:60]
    pname = str(data.get("pname") or PARTIES[party]["n"])[:40]
    mentor = str(data.get("mentor", "magyar"))
    if mentor not in MENTORS:
        mentor = "magyar"
    state = {
        "m": 0, "party": party, "pname": pname, "leader": leader,
        "mentor": mentor, "difficulty": difficulty,
        "money": settings["money"], "cap": settings["capital"], "boost": 0.0,
        "mood": {"U": 0.0, "R": 0.0, "M": 0.0}, "spent": {}, "reg": False,
        "polls": 0, "inpower": False, "seats": 0, "wins": [], "hist": [],
        "below": 0, "years_power": 0.0,
        "log": ["January 1991: the democratic era begins."],
        "event": None, "over": None, "result": None, "poll": {}, "flash": None,
        "score": 0, "founded_seen": [],
    }
    state["poll"] = {key: round(value, 1) for key, value in vote_shares(state, settings["noise"]).items()}
    return state


def largest_remainder(values, total):
    denominator = sum(values.values()) or 1
    exact = {key: value * total / denominator for key, value in values.items()}
    allocated = {key: int(value) for key, value in exact.items()}
    remaining = total - sum(allocated.values())
    order = sorted(exact, key=lambda key: exact[key] - allocated[key], reverse=True)
    for key in order[:remaining]:
        allocated[key] += 1
    return allocated


def run_election(state):
    player = state["party"]
    difficulty = DIFFICULTIES.get(state.get("difficulty", "normal"), DIFFICULTIES["normal"])
    shares = vote_shares(state, difficulty["noise"])
    if not state["reg"]:
        shares[player] *= .6
        total = sum(shares.values()) or 1
        shares = {party: value * 100 / total for party, value in shares.items()}

    eligible = {party: share for party, share in shares.items() if share >= 5}
    if not eligible:
        leader = max(shares, key=shares.get)
        eligible = {leader: shares[leader]}

    seats = dict.fromkeys(eligible, 0)
    winners = []
    difficulty_bonus = {"easy": 1.12, "normal": 1.0, "hard": .90}.get(state.get("difficulty"), 1.0)
    for _name, county_type, constituency_seats in COUNTIES:
        scores = {
            party: share * lean(party, county_type) * random.uniform(.92, 1.08)
            + (state["mood"][county_type] * 2 if party == player and state["inpower"] else 0)
            for party, share in eligible.items()
        }
        if player in scores:
            scores[player] *= difficulty_bonus
        winner = max(scores, key=scores.get)
        seats[winner] += constituency_seats
        winners.append(winner)

    for party, count in largest_remainder(eligible, 93).items():
        seats[party] += count
    majority = 100
    ranked = sorted(seats, key=seats.get, reverse=True)
    government = ranked[0]
    coalition = ranked[1] if seats[government] < majority and len(ranked) > 1 else None
    if coalition and seats[government] + seats[coalition] < majority:
        coalition = None

    state["inpower"] = government == player or (coalition == player)
    state["seats"] = seats.get(player, 0)
    state["wins"] = winners
    share = shares.get(player, 0)
    state["below"] = state["below"] + 1 if share < 5 else 0
    state["result"] = {
        "year": year(state["m"]), "shares": {party: round(value, 1) for party, value in shares.items()},
        "seats": seats, "gov": government, "coalition": coalition,
        "maj": majority, "supermaj": seats[government] * 3 >= 199 * 2,
    }
    state["hist"].append({"year": year(state["m"]), "seats": state["seats"], "gov": government, "share": round(share, 1)})
    state["log"].append(f"{year(state['m'])} election: your party won {state['seats']} simplified seats.")
    state["reg"] = False
    state["spent"] = {}
    if state["inpower"]:
        state["cap"] = min(20, state["cap"] + 3)
    if state["below"] >= 2:
        state["over"] = "dissolved"
        finish(state)


def finish(state):
    state["over"] = state.get("over") or "end"
    state["score"] = sum(item["seats"] for item in state["hist"]) + round(state["years_power"] * 8) + max(0, round(state["money"] / 10))


def op_tick(data):
    state = deepcopy(data["state"])
    if state.get("over") or state.get("event"):
        return state
    state["result"] = None
    state["flash"] = None
    state["m"] = min(state["m"] + 1, END)
    current_year = year(state["m"])
    month_number = state["m"] % 12 + 1
    mentor = MENTORS.get(state["mentor"], MENTORS["magyar"])["bonus"]
    state["money"] += 1.5 + state["poll"].get(state["party"], 0) * .25 + state["seats"] * .05 - 2
    state["cap"] = min(20, state["cap"] + (1 if state["inpower"] else .3) + mentor.get("cap", 0))
    state["boost"] *= .975 if not state["inpower"] else .965
    for group in "UR":
        state["mood"][group] *= .98
    state["mood"]["M"] = (state["mood"]["U"] + state["mood"]["R"]) / 2
    if state["money"] < 0:
        state["boost"] -= .08
    if state["inpower"]:
        state["years_power"] += 1 / 12
    state["polls"] = max(0, state["polls"] - 1)
    settings = DIFFICULTIES.get(state.get("difficulty", "normal"), DIFFICULTIES["normal"])
    state["poll"] = {party: round(value, 1) for party, value in vote_shares(state, .02 if state["polls"] else settings["noise"]).items()}

    if month_number == 1:
        for party, details in PARTIES.items():
            if details["founded"] == current_year and current_year > 1991 and party != "CUSTOM" and party not in state["founded_seen"]:
                state["founded_seen"].append(party)
                state["event"] = {"id": "new-" + party, "title": "New party founded!", "text": f"{details['n']} enters the political landscape in this game year.", "choices": [["Continue", {}]]}
                state["log"].append(f"{current_year}: {details['n']} founded in this simulation.")
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
    action = data["action"]
    if action not in CAMPAIGN:
        raise ValueError("Unknown campaign action.")
    label, cost, gain = CAMPAIGN[action]
    bonus = MENTORS.get(state["mentor"], MENTORS["magyar"])["bonus"]
    if state["money"] < cost:
        state["flash"] = "Not enough money for that action."
        return state
    state["money"] -= cost
    if action == "reg":
        state["reg"] = True
        state["flash"] = "Candidates registered for the next election."
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
    actual_gain = gain / (1 + state["spent"].get(action, 0) / 60)
    state["spent"][action] = state["spent"].get(action, 0) + cost
    state["boost"] += actual_gain
    state["flash"] = f"{label}: campaign support increased. Repeated actions have diminishing returns."
    return state


def op_policy(data):
    state = deepcopy(data["state"])
    policy = next((item for item in POLICIES if item["id"] == data.get("id")), None)
    if policy is None:
        raise ValueError("Unknown policy.")
    if not state["inpower"]:
        state["flash"] = "Your party must lead the government to enact policies."
    elif state["cap"] < policy["cap"] or state["money"] < policy["cost"]:
        state["flash"] = "Not enough political capital or money."
    else:
        state["cap"] -= policy["cap"]
        state["money"] -= policy["cost"]
        mentor_bonus = MENTORS.get(state["mentor"], MENTORS["magyar"])["bonus"].get("anti", 0) if policy["id"] == "anti" else 0
        state["boost"] += policy["b"] + mentor_bonus
        state["mood"]["U"] += policy["U"]
        state["mood"]["R"] += policy["R"]
        state["flash"] = f"Enacted: {policy['label']}. Helps: {policy['win']}; trade-off: {policy['lose']}."
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
    state["boost"] += effect.get("b", 0)
    state["money"] += effect.get("m", 0)
    state["cap"] = min(20, state["cap"] + effect.get("c", 0))
    state["mood"]["U"] += effect.get("U", 0)
    state["mood"]["R"] += effect.get("R", 0)
    state["event"] = None
    return state


def op_mentor(data):
    state = deepcopy(data["state"])
    mentor = data.get("mentor")
    if mentor not in MENTORS:
        raise ValueError("Choose a known mentor.")
    state["mentor"] = mentor
    state["flash"] = f"Mentor selected: {MENTORS[mentor]['n']}."
    return state
