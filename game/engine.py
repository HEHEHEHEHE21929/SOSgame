"""Stateless simulation for Magyar Politika. The browser sends and stores game state."""
import random
from .data import PARTIES, COUNTIES, CAMPAIGN, POLICIES, EVENTS, MENTORS

END = 480
ELECTIONS = {39 + 36 * k for k in range(13)}


def year(month):
    return 1991 + month // 12


def lean(party, county_type):
    urban, rural = PARTIES[party]["lean"]
    return {"U": urban, "R": rural, "M": (urban + rural) / 2}[county_type]


def baseline(party, month):
    frames = PARTIES[party]["support"]
    current_year = 1991 + month / 12
    if current_year <= frames[0][0]:
        return frames[0][1]
    for (y0, v0), (y1, v1) in zip(frames, frames[1:]):
        if current_year <= y1:
            return v0 + (v1 - v0) * (current_year - y0) / (y1 - y0)
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
    from .data import LEADERS
    return {
        "parties": {key: {"n": value["n"], "c": value["c"], "f": value["founded"]}
                    for key, value in PARTIES.items()},
        "campaign": CAMPAIGN, "policies": POLICIES, "mentors": MENTORS,
        "leaders": LEADERS, "counties": COUNTIES,
    }


def op_new(data):
    party = data.get("party", "MDF")
    if party not in PARTIES:
        raise ValueError("Choose a known party.")
    leader = str(data.get("leader") or "Party leader")[:60]
    pname = str(data.get("pname") or PARTIES[party]["n"])[:40]
    mentor = data.get("mentor", "magyar")
    if mentor not in MENTORS:
        mentor = "magyar"
    state = {
        "m": 0, "party": party, "pname": pname, "leader": leader, "mentor": mentor,
        "money": 100.0, "cap": 3.0, "boost": 0.0,
        "mood": {"U": 0.0, "R": 0.0, "M": 0.0}, "spent": {}, "reg": False,
        "polls": 0, "inpower": False, "seats": 0, "wins": [], "hist": [],
        "below": 0, "years_power": 0.0,
        "log": ["January 1991: the democratic era begins."],
        "event": None, "over": None, "result": None, "poll": {}, "flash": None, "score": 0,
    }
    state["poll"] = {p: round(v, 1) for p, v in vote_shares(state, .03).items()}
    return state


def op_tick(data):
    state = data["state"]
    if state.get("over") or state.get("event"):
        return state
    state["result"] = state["flash"] = None
    state["m"] = min(state["m"] + 1, END)
    month = state["m"]
    current_year = year(month)
    month_number = month % 12 + 1
    mentor_bonus = MENTORS[state["mentor"]]["bonus"]

    state["money"] += 1.5 + state["poll"].get(state["party"], 0) * .25 + state["seats"] * .05 - 2
    state["cap"] = min(state["cap"] + (1 if state["inpower"] else .3) + mentor_bonus.get("cap", 0), 20)
    state["boost"] *= .975 if not state["inpower"] else .965
    for group in "UR":
        state["mood"][group] *= .98
    state["mood"]["M"] = (state["mood"]["U"] + state["mood"]["R"]) / 2
    if state["money"] < 0:
        state["boost"] -= .08
    if state["inpower"]:
        state["years_power"] += 1 / 12
    state["polls"] = max(0, state["polls"] - 1)
    state["poll"] = {p: round(v, 1) for p, v in vote_shares(state, .02 if state["polls"] else .12).items()}

    if month_number == 1:
        for party, info in PARTIES.items():
            if info["founded"] == current_year and current_year > 1991 and party != "CUSTOM":
                state["event"] = {"id": "new-" + party, "title": "New party founded!",
                                  "text": f"{info['n']} enters the political landscape in this game year.",
                                  "choices": [["Continue", {}]]}
                state["log"].append(f"{current_year}: {info['n']} founded in the simulation.")
    for event in EVENTS:
        if event["y"] == current_year and event["mo"] == month_number:
            state["event"] = dict(event)
    if month in ELECTIONS:
        run_election(state)
    if month >= END:
        finish(state)
    return state


def largest_remainder(values, total):
    exact = {key: value * total / sum(values.values()) for key, value in values.items()}
    allocated = {key: int(value) for key, value in exact.items()}
    remaining = total - sum(allocated.values())
    for key in sorted(exact, key=lambda item: exact[item] - allocated[item], reverse=True)[:remaining]:
        allocated[key] += 1
    return allocated


def run_election(state):
    player = state["party"]
    shares = vote_shares(state, .07)
    if not state["reg"]:
        shares[player] *= .6
        total = sum(shares.values())
        shares = {p: v * 100 / total for p, v in shares.items()}
    eligible = {p: v for p, v in shares.items() if v >= 5}
    if not eligible:
        eligible = {max(shares, key=shares.get): max(shares.values())}

    seats = dict.fromkeys(eligible, 0)
    winners = []
    for _name, county_type, constituency_seats in COUNTIES:
        scores = {p: share * lean(p, county_type) * random.uniform(.92, 1.08)
                  + (state["mood"][county_type] * 2 if p == player and state["inpower"] else 0)
                  for p, share in eligible.items()}
        winner = max(scores, key=scores.get)
        seats[winner] += constituency_seats
        winners.append(winner)
    list_seats = largest_remainder(eligible, 93)
    for party, number in list_seats.items():
        seats[party] += number

    total_seats = sum(seats.values())
    majority = total_seats // 2 + 1
    ranked = sorted(seats, key=seats.get, reverse=True)
    government = ranked[0]
    coalition = ranked[1] if seats[government] < majority and len(ranked) > 1 else None
    if coalition is not None and seats[government] + seats[coalition] < majority:
        coalition = None

    state["inpower"] = government == player
    state["seats"] = seats.get(player, 0)
    state["wins"] = winners
    state["below"] = state["below"] + 1 if shares.get(player, 0) < 5 else 0
    state["result"] = {"year": year(state["m"]), "shares": {p: round(v, 1) for p, v in shares.items()},
                       "seats": seats, "gov": government, "coalition": coalition,
                       "maj": majority, "supermaj": seats[government] * 3 >= total_seats * 2}
    state["hist"].append({"year": year(state["m"]), "seats": state["seats"],
                          "gov": government, "share": round(shares.get(player, 0), 1)})
    state["log"].append(f"{year(state['m'])} election: your party won {state['seats']} seats.")
    state["reg"] = False
    state["spent"] = {}
    if state["inpower"]:
        state["cap"] = min(20, state["cap"] + 3)
    if state["below"] >= 2:
        state["over"] = "dissolved"
        finish(state)


def finish(state):
    state["over"] = state["over"] or "end"
    state["score"] = (sum(item["seats"] for item in state["hist"])
                      + round(state["years_power"] * 8)
                      + max(0, round(state["money"] / 10)))


def op_campaign(data):
    state, action = data["state"], data["action"]
    if action not in CAMPAIGN:
        raise ValueError("Unknown campaign action.")
    label, cost, gain = CAMPAIGN[action]
    bonus = MENTORS[state["mentor"]]["bonus"]
    if state["money"] < cost:
        state["flash"] = "Not enough money for that action."
        return state
    state["money"] -= cost
    if action == "reg":
        state["reg"] = True
        state["flash"] = "Candidates registered."
        return state
    if action == "poll":
        state["polls"] = 6
        state["flash"] = "More accurate polls for six months."
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
    state["flash"] = f"{label}: +{actual_gain:.2f} support"
    return state


def op_policy(data):
    state = data["state"]
    policy = next((p for p in POLICIES if p["id"] == data.get("id")), None)
    if policy is None:
        raise ValueError("Unknown policy.")
    if not state["inpower"]:
        state["flash"] = "Your party is not leading the government."
    elif state["cap"] < policy["cap"] or state["money"] < policy["cost"]:
        state["flash"] = "Not enough political capital or money."
    else:
        state["cap"] -= policy["cap"]
        state["money"] -= policy["cost"]
        state["boost"] += policy["b"] + (MENTORS[state["mentor"]]["bonus"].get("anti", 0)
                                         if policy["id"] == "anti" else 0)
        state["mood"]["U"] += policy["U"]
        state["mood"]["R"] += policy["R"]
        state["flash"] = f"Enacted: {policy['label']}. Helps: {policy['win']}; trade-off: {policy['lose']}."
    return state


def op_choice(data):
    state = data["state"]
    if not state.get("event"):
        raise ValueError("There is no event waiting for a choice.")
    choices = state["event"].get("choices", [])
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
    state = data["state"]
    mentor = data.get("mentor")
    if mentor not in MENTORS:
        raise ValueError("Choose a known mentor.")
    state["mentor"] = mentor
    state["flash"] = f"Mentor selected: {MENTORS[mentor]['n']}."
    return state
