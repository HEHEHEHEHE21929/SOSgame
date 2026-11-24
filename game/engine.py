"""Game engine. Stateless: the browser sends the game state, we return the new one."""
import random
from .data import PARTIES, COUNTIES, CAMPAIGN, POLICIES, EVENTS, MENTORS, LEADERS

END = 480                                       # months from Jan 1991 to end of 2030
ELECTIONS = {39 + 36 * k for k in range(13)}    # April 1994, then every 3 years to 2030


def year(m):
    return 1991 + m // 12


def lean(p, ty):
    u, r = PARTIES[p]["l"]
    return {"U": u, "R": r, "M": (u + r) / 2}[ty]


def base(p, m):
    """Baseline support (%) of a party, interpolated between its keyframes."""
    t, y = PARTIES[p]["t"], 1991 + m / 12
    if y <= t[0][0]:
        return t[0][1]
    for (y0, v0), (y1, v1) in zip(t, t[1:]):
        if y <= y1:
            return v0 + (v1 - v0) * (y - y0) / (y1 - y0)
    return t[-1][1]


def shares(s, noise):
    """Vote shares (%) of every active party. The player's party gets its campaign boost."""
    raw = {}
    for p in PARTIES:
        if p == "CUSTOM" and s["party"] != p:
            continue
        if p == s["party"]:
            v = max(base(p, s["m"]), 3) + s["boost"]
        elif year(s["m"]) >= PARTIES[p]["f"] and base(p, s["m"]) > .3:
            v = base(p, s["m"])
        else:
            continue
        raw[p] = max(v, .1) * random.uniform(1 - noise, 1 + noise)
    tot = sum(raw.values())
    return {p: v * 100 / tot for p, v in raw.items()}


def meta():
    return dict(parties={k: dict(n=v["n"], c=v["c"], f=v["f"]) for k, v in PARTIES.items()},
                campaign=CAMPAIGN, policies=POLICIES, mentors=MENTORS, leaders=LEADERS, counties=COUNTIES)


def op_new(d):
    s = dict(m=0, party=d["party"], pname=d.get("pname") or PARTIES[d["party"]]["n"], leader=d["leader"],
             mentor=d.get("mentor", "magyar"), money=100.0, cap=3.0, boost=0.0,
             mood={"U": 0, "R": 0, "M": 0}, spent={}, reg=False, polls=0, inpower=False,
             seats=0, wins=[], hist=[], below=0, years_power=0.0,
             log=["January 1991: the democratic era begins."], event=None, over=None, result=None,
             poll={}, flash=None, score=0)
    s["poll"] = {p: round(v, 1) for p, v in shares(s, .05).items()}
    return s


def op_tick(d):
    """Advance one month: money, support, new parties, historical events, elections."""
    s = d["state"]
    if s["over"] or s["event"]:
        return s
    s["result"] = s["flash"] = None
    s["m"] += 1
    m = s["m"]
    y = year(m)
    mo = m % 12 + 1
    mb = MENTORS[s["mentor"]]["bonus"]
    s["money"] += 1.5 + s["poll"].get(s["party"], 0) * .25 + s["seats"] * .05 - 2
    s["cap"] = min(s["cap"] + (1 if s["inpower"] else .3) + mb.get("cap", 0), 20)
    s["boost"] *= .985 - (.01 if s["inpower"] else 0)
    for k in "UR":
        s["mood"][k] *= .98
    s["mood"]["M"] = (s["mood"]["U"] + s["mood"]["R"]) / 2
    if s["money"] < 0:
        s["boost"] -= .08
    if s["inpower"]:
        s["years_power"] += 1 / 12
    s["polls"] = max(0, s["polls"] - 1)
    s["poll"] = {p: round(v, 1) for p, v in shares(s, .02 if s["polls"] else .15).items()}
    if mo == 1:
        for p, q in PARTIES.items():
            if q["f"] == y and y > 1991 and p != "CUSTOM":
                s["event"] = dict(id="new", title="New party founded!", choices=[["OK", {}]],
                                  text=f"{q['n']} is founded this year and will compete for votes.")
                s["log"].append(f"{y}: {q['n']} founded.")
    for e in EVENTS:
        if e["y"] == y and e["mo"] == mo:
            s["event"] = dict(e)
    if m in ELECTIONS:
        election(s)
    if m >= END - 1:
        finish(s)
    return s


def election(s):
    me = s["party"]
    sh = shares(s, .08)
    if not s["reg"]:
        sh[me] *= .6
        t = sum(sh.values())
        sh = {p: v * 100 / t for p, v in sh.items()}
    ok = {p: v for p, v in sh.items() if v >= 5}
    seats = dict.fromkeys(ok, 0)
    wins = []
    for n, ty, k in COUNTIES:
        sc = {p: v * lean(p, ty) * random.uniform(.9, 1.1) +
              (s["mood"][ty] * 2 if p == me and s["inpower"] else 0)
              for p, v in ok.items()}
        w = max(sc, key=sc.get)
        seats[w] += k
        wins.append(w)
    tot = sum(ok.values())
    for p, v in ok.items():
        seats[p] += round(93 * v / tot)
    total = sum(seats.values())
    maj = total // 2 + 1
    order = sorted(seats, key=seats.get, reverse=True)
    gov = order[0]
    coal = order[1] if seats[gov] < maj and len(order) > 1 else None
    s["inpower"] = gov == me
    s["seats"] = seats.get(me, 0)
    s["wins"] = wins
    s["below"] = s["below"] + 1 if sh[me] < 5 else 0
    s["result"] = dict(year=year(s["m"]), shares={p: round(v, 1) for p, v in sh.items()},
                       seats=seats, gov=gov, coalition=coal, maj=maj,
                       supermaj=seats[gov] * 3 >= total * 2)
    s["hist"].append(dict(year=year(s["m"]), seats=s["seats"], gov=gov, share=round(sh[me], 1)))
    s["log"].append(f"{year(s['m'])} election: you won {s['seats']} seats.")
    s["reg"] = False
    s["spent"] = {}
    if s["inpower"]:
        s["cap"] += 3
    if s["below"] >= 2:
        s["over"] = "dissolved"
        finish(s)


def finish(s):
    s["over"] = s["over"] or "end"
    s["score"] = (sum(h["seats"] for h in s["hist"]) + round(s["years_power"] * 8)
                  + max(0, round(s["money"] / 10)))


def op_campaign(d):
    s, a = d["state"], d["action"]
    label, cost, b = CAMPAIGN[a]
    mb = MENTORS[s["mentor"]]["bonus"]
    if s["money"] < cost:
        s["flash"] = "Not enough money!"
        return s
    s["money"] -= cost
    if a == "reg":
        s["reg"] = True
        s["flash"] = "Candidates registered."
        return s
    if a == "poll":
        s["polls"] = 6
        s["flash"] = "Accurate polls for 6 months."
        return s
    if a in ("tv", "social"):
        b *= 1 + mb.get("tv", 0)
    if a == "vol":
        b *= 1 + mb.get("vol", 0)
    if a == "social" and year(s["m"]) >= 2010:
        b *= 1.5
    gain = b / (1 + s["spent"].get(a, 0) / 60)
    s["spent"][a] = s["spent"].get(a, 0) + cost
    s["boost"] += gain
    s["flash"] = f"{label}: +{gain:.2f} support"
    return s


def op_policy(d):
    s = d["state"]
    p = next(x for x in POLICIES if x["id"] == d["id"])
    if not s["inpower"]:
        s["flash"] = "You are not in government."
        return s
    if s["cap"] < p["cap"] or s["money"] < p["cost"]:
        s["flash"] = "Not enough political capital or money."
        return s
    s["cap"] -= p["cap"]
    s["money"] -= p["cost"]
    s["boost"] += p["b"] + (MENTORS[s["mentor"]]["bonus"].get("anti", 0) if p["id"] == "anti" else 0)
    s["mood"]["U"] += p["U"]
    s["mood"]["R"] += p["R"]
    s["flash"] = f"Enacted: {p['label']}. Helps: {p['win']}. Hurts: {p['lose']}."
    return s


def op_choice(d):
    s = d["state"]
    fx = s["event"]["choices"][d["i"]][1]
    s["boost"] += fx.get("b", 0)
    s["money"] += fx.get("m", 0)
    s["cap"] += fx.get("c", 0)
    s["mood"]["U"] += fx.get("U", 0)
    s["mood"]["R"] += fx.get("R", 0)
    s["event"] = None
    return s
