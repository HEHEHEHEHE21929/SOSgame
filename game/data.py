"""Game data. Support numbers are simplified game values, not exact election history."""


def P(i, label, cap, cost, b, U, R, win, lose):
    return dict(id=i, label=label, cap=cap, cost=cost, b=b, U=U, R=R, win=win, lose=lose)


def E(i, y, mo, title, text, *ch):
    return dict(id=i, y=y, mo=mo, title=title, text=text, choices=[list(c) for c in ch])


# n=name, c=colour, f=founded, l=(city lean, rural lean), t=(year, support %) keyframes
PARTIES = {
    "MDF": dict(n="MDF", c="#00aa00", f=1988, l=(1, 1.1), t=[(1991, 25), (1994, 12), (1998, 3), (2002, 0)]),
    "SZDSZ": dict(n="SZDSZ", c="#ff55ff", f=1988, l=(1.5, .6), t=[(1991, 20), (1994, 19), (1998, 8), (2006, 6), (2010, 0)]),
    "MSZP": dict(n="MSZP", c="#ff5555", f=1989, l=(1, 1), t=[(1991, 12), (1994, 33), (1998, 32), (2002, 42), (2010, 19), (2018, 12), (2022, 10), (2026, 2)]),
    "FKGP": dict(n="FKGP", c="#aa5500", f=1988, l=(.6, 1.5), t=[(1991, 10), (1994, 9), (1998, 3), (2002, 0)]),
    "KDNP": dict(n="KDNP", c="#aa00aa", f=1989, l=(.8, 1.2), t=[(1991, 7), (1994, 7), (1998, 3), (2002, 0)]),
    "FIDESZ": dict(n="Fidesz", c="#ff9922", f=1988, l=(.9, 1.15), t=[(1991, 6), (1994, 7), (1998, 29), (2002, 41), (2010, 53), (2018, 49), (2022, 54), (2026, 39)]),
    "DK": dict(n="DK", c="#5555ff", f=2011, l=(1.4, .6), t=[(2011, 3), (2018, 6), (2022, 20), (2026, 3)]),
    "MKKP": dict(n="MKKP", c="#ffff55", f=2006, l=(1.6, .5), t=[(2006, .5), (2018, 1.7), (2022, 3.2), (2026, 2)]),
    "MIHAZANK": dict(n="Mi Hazánk", c="#888888", f=2018, l=(.7, 1.3), t=[(2018, 1), (2022, 6), (2026, 6)]),
    "TISZA": dict(n="Tisza", c="#00aaaa", f=2024, l=(1.2, .95), t=[(2024, 10), (2025, 30), (2026, 53)]),
    "CUSTOM": dict(n="My Party", c="#ffffff", f=1991, l=(1, 1), t=[(1991, 3)]),
}

LEADERS = {
    "MDF": ["Antall József"], "SZDSZ": ["Kis János"], "MSZP": ["Horn Gyula"],
    "FKGP": ["Torgyán József"], "KDNP": ["Surján László"], "FIDESZ": ["Orbán Viktor"],
}

# 19 counties + Budapest: (name, type U=city R=rural M=mixed, constituency seats; total 106)
COUNTIES = [
    ("Budapest", "U", 16), ("Pest", "U", 12), ("Győr-Moson-Sopron", "M", 6),
    ("Komárom-Esztergom", "M", 4), ("Fejér", "M", 5), ("Veszprém", "M", 5),
    ("Vas", "R", 3), ("Zala", "R", 3), ("Somogy", "R", 4), ("Tolna", "R", 3),
    ("Baranya", "M", 4), ("Bács-Kiskun", "R", 6), ("Csongrád-Csanád", "M", 4),
    ("Békés", "R", 4), ("Jász-Nagykun-Szolnok", "R", 4), ("Heves", "M", 3),
    ("Nógrád", "R", 2), ("Borsod-Abaúj-Zemplén", "R", 8), ("Hajdú-Bihar", "M", 5),
    ("Szabolcs-Szatmár-Bereg", "R", 5),
]

# id: (label, cost in M Ft, support gain)
CAMPAIGN = {
    "posters": ("Posters", 5, .4), "tv": ("TV ads", 20, 1.6),
    "social": ("Social media", 10, .9), "rally": ("Rallies", 8, .8),
    "vol": ("Volunteers", 3, .5), "reg": ("Register candidates", 30, 0),
    "poll": ("Accurate polling", 4, 0),
}

POLICIES = [
    P("tax", "Cut income tax", 2, 15, .5, .4, .2, "Workers", "Public services"),
    P("health", "Fund hospitals", 2, 20, .7, .2, .6, "Patients, rural towns", "Taxpayers"),
    P("edu", "Raise teacher pay", 2, 15, .5, .4, .3, "Teachers, families", "The budget"),
    P("eu", "Seek EU funds deal", 3, 5, .6, .6, -.2, "Cities, business", "Sovereignty-minded voters"),
    P("energy", "Invest in energy", 3, 25, .4, .2, .3, "Industry", "Short-term bills"),
    P("media", "Reform public media", 3, 5, .3, .5, -.4, "Pluralism supporters", "Fans of old coverage"),
    P("anti", "Anti-corruption office", 3, 10, .6, .5, .2, "Taxpayers", "People under investigation"),
    P("immig", "Tighten border rules", 2, 5, .4, -.3, .6, "Security-minded voters", "Employers needing workers"),
    P("house", "Build cheap housing", 3, 25, .6, .7, -.1, "Young renters", "Property owners"),
    P("fuel", "Cap fuel prices", 2, 15, .5, -.2, .6, "Drivers", "Climate goals"),
]

EVENTS = [
    E("trans", 1993, 1, "Economic transition", "Factories close as the economy moves to the market.",
      ("Back fast reforms", {"b": -.3, "U": .3, "c": 2}), ("Back slower reform", {"b": .3, "R": .3})),
    E("nato", 1999, 3, "Hungary joins NATO", "A historic change in Hungary's security.",
      ("Celebrate", {"b": .5}), ("Ask about the cost", {"m": 10, "R": .2})),
    E("eu", 2004, 5, "Hungary joins the EU", "Borders open and EU funds start to flow.",
      ("Welcome EU funds", {"b": .6, "U": .3}), ("Warn about sovereignty", {"b": .4, "R": .3})),
    E("crisis", 2008, 10, "Global financial crisis", "Banks wobble and loans become costly.",
      ("Support austerity", {"b": -.4, "c": 2}), ("Support stimulus", {"m": -15, "b": .5})),
    E("migr", 2015, 9, "Migration crisis", "Thousands of people cross Hungary's borders.",
      ("Stress border security", {"R": .5, "U": -.3}), ("Stress humanitarian aid", {"U": .4, "R": -.4})),
    E("covid", 2020, 3, "COVID-19", "The pandemic reaches Hungary.",
      ("Back strict rules", {"b": .3}), ("Back more freedom", {"b": .3, "R": .2})),
    E("ukr", 2022, 2, "War in Ukraine", "War begins next door.",
      ("Back strong sanctions", {"U": .4, "R": -.2}), ("Call for peace talks first", {"R": .4, "U": -.2})),
]

MENTORS = {
    "magyar": dict(n="Magyar Péter", bonus={"anti": .6, "vol": .4},
                    facts=["Resigned from Fidesz in 2024", "Founded Tisza in 2024",
                           "Led Tisza to a two-thirds majority in April 2026",
                           "Became prime minister in May 2026"],
                    learn="Supporters admire his anti-corruption message and his challenge to a long-ruling government. Critics note his years as a Fidesz insider and question how different his government will be."),
    "antall": dict(n="Antall József", bonus={"cap": .2},
                   facts=["First prime minister after the 1990 free elections", "Led the MDF"],
                   learn="Supporters admire his steady leadership through the post-communist transition. Critics say the economy suffered and reforms felt slow to many voters."),
    "horn": dict(n="Horn Gyula", bonus={"tv": .3},
                 facts=["Prime minister 1994–1998", "Led the MSZP"],
                 learn="Supporters credit him with stabilising the economy and steering Hungary toward NATO and the EU. Critics point to the unpopular austerity package of 1995."),
    "orban": dict(n="Orbán Viktor", bonus={"vol": .2, "tv": .2},
                  facts=["Prime minister 1998–2002 and 2010–2026", "Leader of Fidesz"],
                  learn="Supporters credit him with a strong focus on national sovereignty and family support. Critics say his governments weakened checks and balances and tolerated corruption."),
}
