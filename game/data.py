"""Game engine. Stateless: the browser sends the game state, we return the new one."""
import random
from .data import PARTIES, COUNTIES, CAMPAIGN, POLICIES, EVENTS, MENTORS, LEADERS

END = 480                                       # months from Jan 1991 to end of 2030
ELECTIONS = {39 + 36 * k for k in range(13)}    # April 1994, then every 3 years to 2030

def year(m): return 1991 + m // 12
def lean(p, ty):
    u, r = PARTIES[p]["l"]
    return {"U": u, "R": r, "M": (u + r) / 2}[ty]

def base(p, m):
    """Baseline support (%) of a party, interpolated between its keyframes."""
    t, y = PARTIES[p]["t"], 1991 + m / 12
    if y <= t[0][0]: return t[0][1]
    for (y0, v0), (y1, v1) in zip(t, t[1:]):
        if y <= y1: return v0 + (v1 - v0) * (y - y0) / (y1 - y0)
    return t[-1][1]

def shares(s, noise):
    """Vote shares (%) of every active party. The player's party gets its 'boost' from campaigning."""
    raw = {}
    for p in PARTIES:
        if p == "CUSTOM" and s["party"] != p: continue
        if p == s["party"]: v = max(base(p, s["m"]), 3) + s["boost"]
        elif year(s["m"]) >= PARTIES[p]["f"] and base(p, s["m"]) > .3: v = base(p, s["m"])
        else: continue
        raw[p] = max(v, .1) * random.uniform(1 - noise, 1 + noise)
    tot = sum(raw.values())
    return {p: v * 100 / tot for p, v in raw.items()}

def meta():
    return dict(parties={k: dict(n=v["n"], c=v["c"], f=v["f"]) for k, v in PARTIES.items()},
                campaign=CAMPAIGN, policies=POLICIES, mentors=MENTORS, leaders=LEADERS, counties=COUNTIES)

def op_new(d):
    s = dict(m=0, party=d["party"], pname=d.get("pname") or PARTIES[d["party"]]["n"], leader=d["leader"],
             mentor=d.get("mentor", "magyar"), money=100.0, cap=3.0, boost=0.0, mood={"U": 0, "R": 0, "M": 0},
             spent={}, reg=False, polls=0, inpower=False, seats=0, wins=[], hist=[], below=0, years_power=0.0,
             log=["January 1991: the democratic era begins."], event=None, over=None, result=None,
             poll={}, flash=None, score=0)
    s["poll"] = {p: round(v, 1) for p, v in shares(s, .05).items()}
    return s

def op_tick(d):
    """Advance one month: money, support, new parties, historical events, elections."""
    s = d["state"]
    if s["over"] or s["event"]: return s
    s["result"] = s["flash"] = None
    s["m"] += 1; m = s["m"]; y = year(m); mo = m % 12 + 1
    mb = MENTORS[s["mentor"]]["bonus"]
    s["money"] += 1.5 + s["poll"].get(s["party"], 0) * .25 + s["seats"] * .05 - 2   # dues + funding - staff
    s["cap"] = min(s["cap"] + (1 if s["inpower"] else .3) + mb.get("cap", 0), 20)
    s["boost"] *= .985 - (.01 if s["inpower"] else 0)
    for k in "UR": s["mood"][k] *= .98
    s["mood"]["M"] = (s["mood"]["U"] + s["mood"]["R"]) / 2
    if s["money"] < 0: s["boost"] -= .08                                              # debt hurts
    if s["inpower"]: s["years_power"] += 1 / 12
    s["polls"] = max(0, s["polls"] - 1)
    s["poll"] = {p: round(v, 1) for p, v in shares(s, .02 if s["polls"] else .15).items()}
    if mo == 1:
        for p, q in PARTIES.items():
            if q["f"] == y and y > 1991 and p != "CUSTOM":
                s["event"] = dict(id="new", title="New party founded!", choices=[["OK", {}]],
                                  text=f"{q['n']} is founded this year and will compete for votes.")
                s["log"].append(f"{y}: {q['n']} founded.")
    for e in EVENTS:
        if e["y"] == y and e["mo"] == mo: s["event"] = dict(e)
    if m in ELECTIONS: election(s)
    if m >= END - 1: finish(s)
    return s

def election(s):
    me = s["party"]; sh = shares(s, .08)
    if not s["reg"]:                                   # unregistered candidates lose votes
        sh[me] *= .6; t = sum(sh.values()); sh = {p: v * 100 / t for p, v in sh.items()}
    ok = {p: v for p, v in sh.items() if v >= 5}       # 5% threshold
    seats = dict.fromkeys(ok, 0); wins = []
    for n, ty, k in COUNTIES:                          # 106 constituency seats: county winner takes all
        sc = {p: v * lean(p, ty) * random.uniform(.9, 1.1) + (s["mood"][ty] * 2 if p == me and s["inpower"] else 0)
              for p, v in ok.items()}
        w = max(sc, key=sc.get); seats[w] += k; wins.append(w)
    tot = sum(ok.values())
    for p, v in ok.items(): seats[p] += round(93 * v / tot)   # 93 list seats
    total = sum(seats.values()); maj = total // 2 + 1
    order = sorted(seats, key=seats.get, reverse=True); gov = order[0]
    coal = order[1] if seats[gov] < maj and len(order) > 1 else None
    s["inpower"] = gov == me; s["seats"] = seats.get(me, 0); s["wins"] = wins
    s["below"] = s["below"] + 1 if sh[me] < 5 else 0
    s["result"] = dict(year=year(s["m"]), shares={p: round(v, 1) for p, v in sh.items()}, seats=seats,
                       gov=gov, coalition=coal, maj=maj, supermaj=seats[gov] * 3 >= total * 2)
    s["hist"].append(dict(year=year(s["m"]), seats=s["seats"], gov=gov, share=round(sh[me], 1)))
    s["log"].append(f"{year(s['m'])} election: you won {s['seats']} seats.")
    s["reg"] = False; s["spent"] = {}
    if s["inpower"]: s["cap"] += 3
    if s["below"] >= 2: s["over"] = "dissolved"; finish(s)

def finish(s):
    s["over"] = s["over"] or "end"
    s["score"] = sum(h["seats"] for h in s["hist"]) + round(s["years_power"] * 8) + max(0, round(s["money"] / 10))

def op_campaign(d):
    s, a = d["state"], d["action"]; label, cost, b = CAMPAIGN[a]; mb = MENTORS[s["mentor"]]["bonus"]
    if s["money"] < cost: s["flash"] = "Not enough money!"; return s
    s["money"] -= cost
    if a == "reg": s["reg"] = True; s["flash"] = "Candidates registered."; return s
    if a == "poll": s["polls"] = 6; s["flash"] = "Accurate polls for 6 months."; return s
    if a in ("tv", "social"): b *= 1 + mb.get("tv", 0)
    if a == "vol": b *= 1 + mb.get("vol", 0)
    if a == "social" and year(s["m"]) >= 2010: b *= 1.5          # social media matters more later
    gain = b / (1 + s["spent"].get(a, 0) / 60)                   # diminishing returns
    s["spent"][a] = s["spent"].get(a, 0) + cost; s["boost"] += gain
    s["flash"] = f"{label}: +{gain:.2f} support"
    return s

def op_policy(d):
    s = d["state"]; p = next(x for x in POLICIES if x["id"] == d["id"])
    if not s["inpower"]: s["flash"] = "You are not in government."; return s
    if s["cap"] < p["cap"] or s["money"] < p["cost"]: s["flash"] = "Not enough political capital or money."; return s
    s["cap"] -= p["cap"]; s["money"] -= p["cost"]
    s["boost"] += p["b"] + (MENTORS[s["mentor"]]["bonus"].get("anti", 0) if p["id"] == "anti" else 0)
    s["mood"]["U"] += p["U"]; s["mood"]["R"] += p["R"]
    s["flash"] = f"Enacted: {p['label']}. Helps: {p['win']}. Hurts: {p['lose']}."
    return s

def op_choice(d):
    s = d["state"]; fx = s["event"]["choices"][d["i"]][1]
    s["boost"] += fx.get("b", 0); s["money"] += fx.get("m", 0); s["cap"] += fx.get("c", 0)
    s["mood"]["U"] += fx.get("U", 0); s["mood"]["R"] += fx.get("R", 0); s["event"] = None
    return s

"""Game data. Support numbers are simplified game values, not exact election history."""
def P(i, label, cap, cost, b, U, R, win, lose):
    return dict(id=i, label=label, cap=cap, cost=cost, b=b, U=U, R=R, win=win, lose=lose)
def E(i, y, mo, title, text, *ch):
    return dict(id=i, y=y, mo=mo, title=title, text=text, choices=[list(c) for c in ch])

# n=name, c=colour, f=founded, l=(city lean, rural lean), t=(year, support %) keyframes
PARTIES = {
 "MDF":    dict(n="MDF",    c="#00aa00", f=1988, l=(1, 1.1),   t=[(1991,25),(1994,12),(1998,3),(2002,0)]),
 "SZDSZ":  dict(n="SZDSZ",  c="#ff55ff", f=1988, l=(1.5, .6),  t=[(1991,20),(1994,19),(1998,8),(2006,6),(2010,0)]),
 "MSZP":   dict(n="MSZP",   c="#ff5555", f=1989, l=(1, 1),     t=[(1991,12),(1994,33),(1998,32),(2002,42),(2010,19),(2018,12),(2022,10),(2026,2)]),
 "FKGP":   dict(n="FKGP",   c="#aa5500", f=1988, l=(.6, 1.5),  t=[(1991,10),(1994,9),(1998,3),(2002,0)]),
 "KDNP":   dict(n="KDNP",   c="#aa00aa", f=1989, l=(.8, 1.2),  t=[(1991,7),(1994,7),(1998,3),(2002,0)]),
 "FIDESZ": dict(n="Fidesz", c="#ff9922", f=1988, l=(.9, 1.15), t=[(1991,6),(1994,7),(1998,29),(2002,41),(2010,53),(2018,49),(2022,54),(2026,39)]),
 "DK":     dict(n="DK",     c="#5555ff", f=2011, l=(1.4, .6),  t=[(2011,3),(2018,6),(2022,20),(2026,3)]),
 "MKKP":   dict(n="MKKP",   c="#ffff55", f=2006, l=(1.6, .5),  t=[(2006,.5),(2018,1.7),(2022,3.2),(2026,2)]),
 "MIHAZANK": dict(n="Mi Hazánk", c="#888888", f=2018, l=(.7, 1.3), t=[(2018,1),(2022,6),(2026,6)]),
 "TISZA":  dict(n="Tisza",  c="#00aaaa", f=2024, l=(1.2, .95), t=[(2024,10),(2025,30),(2026,53)]),
 "CUSTOM": dict(n="My Party", c="#ffffff", f=1991, l=(1, 1),   t=[(1991,3)]),
}
LEADERS = {"MDF": ["Antall József"], "SZDSZ": ["Kis János"], "MSZP": ["Horn Gyula"],
           "FKGP": ["Torgyán József"], "KDNP": ["Surján László"], "FIDESZ": ["Orbán Viktor"]}

# 19 counties + Budapest: (name, type U=city R=rural M=mixed, constituency seats; total 106)
COUNTIES = [("Budapest","U",16),("Pest","U",12),("Győr-Moson-Sopron","M",6),("Komárom-Esztergom","M",4),
 ("Fejér","M",5),("Veszprém","M",5),("Vas","R",3),("Zala","R",3),("Somogy","R",4),("Tolna","R",3),
 ("Baranya","M",4),("Bács-Kiskun","R",6),("Csongrád-Csanád","M",4),("Békés","R",4),
 ("Jász-Nagykun-Szolnok","R",4),("Heves","M",3),("Nógrád","R",2),("Borsod-Abaúj-Zemplén","R",8),
 ("Hajdú-Bihar","M",5),("Szabolcs-Szatmár-Bereg","R",5)]

# id: (label, cost in M Ft, support gain)
CAMPAIGN = {"posters": ("Posters", 5, .4), "tv": ("TV ads", 20, 1.6), "social": ("Social media", 10, .9),
            "rally": ("Rallies", 8, .8), "vol": ("Volunteers", 3, .5),
            "reg": ("Register candidates", 30, 0), "poll": ("Accurate polling", 4, 0)}

POLICIES = [
 P("tax","Cut income tax",2,15,.5,.4,.2,"Workers","Public services"),
 P("health","Fund hospitals",2,20,.7,.2,.6,"Patients, rural towns","Taxpayers"),
 P("edu","Raise teacher pay",2,15,.5,.4,.3,"Teachers, families","The budget"),
 P("eu","Seek EU funds deal",3,5,.6,.6,-.2,"Cities, business","Sovereignty-minded voters"),
 P("energy","Invest in energy",3,25,.4,.2,.3,"Industry","Short-term bills"),
 P("media","Reform public media",3,5,.3,.5,-.4,"Pluralism supporters","Fans of old coverage"),
 P("anti","Anti-corruption office",3,10,.6,.5,.2,"Taxpayers","People under investigation"),
 P("immig","Tighten border rules",2,5,.4,-.3,.6,"Security-minded voters","Employers needing workers"),
 P("house","Build cheap housing",3,25,.6,.7,-.1,"Young renters","Property owners"),
 P("fuel","Cap fuel prices",2,15,.5,-.2,.6,"Drivers","Climate goals"),
]

EVENTS = [
 E("trans",1993,1,"Economic transition","Factories close as the economy moves to the market.",
   ("Back fast reforms",{"b":-.3,"U":.3,"c":2}),("Back slower reform",{"b":.3,"R":.3})),
 E("nato",1999,3,"Hungary joins NATO","A historic change in Hungary's security.",
   ("Celebrate",{"b":.5}),("Ask about the cost",{"m":10,"R":.2})),
 E("eu",2004,5,"Hungary joins the EU","Borders open and EU funds start to flow.",
   ("Welcome EU funds",{"b":.6,"U":.3}),("Warn about sovereignty",{"b":.4,"R":.3})),
 E("crisis",2008,10,"Global financial crisis","Banks wobble and loans become costly.",
   ("Support austerity",{"b":-.4,"c":2}),("Support stimulus",{"m":-15,"b":.5})),
 E("migr",2015,9,"Migration crisis","Thousands of people cross Hungary's borders.",
   ("Stress border security",{"R":.5,"U":-.3}),("Stress humanitarian aid",{"U":.4,"R":-.4})),
 E("covid",2020,3,"COVID-19","The pandemic reaches Hungary.",
   ("Back strict rules",{"b":.3}),("Back more freedom",{"b":.3,"R":.2})),
 E("ukr",2022,2,"War in Ukraine","War begins next door.",
   ("Back strong sanctions",{"U":.4,"R":-.2}),("Call for peace talks first",{"R":.4,"U":-.2})),
]

MENTORS = {
 "magyar": dict(n="Magyar Péter", bonus={"anti": .6, "vol": .4},
   facts=["Resigned from Fidesz in 2024","Founded Tisza in 2024","Led Tisza to a two-thirds majority in April 2026","Became prime minister in May 2026"],
   learn="Supporters admire his anti-corruption message and his challenge to a long-ruling government. Critics note his years as a Fidesz insider and question how different his government will be."),
 "antall": dict(n="Antall József", bonus={"cap": .2},
   facts=["First prime minister after the 1990 free elections","Led the MDF"],
   learn="Supporters admire his steady leadership through the post-communist transition. Critics say the economy suffered and reforms felt slow to many voters."),
 "horn": dict(n="Horn Gyula", bonus={"tv": .3},
   facts=["Prime minister 1994–1998","Led the MSZP"],
   learn="Supporters credit him with stabilising the economy and steering Hungary toward NATO and the EU. Critics point to the unpopular austerity package of 1995."),
 "orban": dict(n="Orbán Viktor", bonus={"vol": .2, "tv": .2},
   facts=["Prime minister 1998–2002 and 2010–2026","Leader of Fidesz"],
   learn="Supporters credit him with a strong focus on national sovereignty and family support. Critics say his governments weakened checks and balances and tolerated corruption."),
}

