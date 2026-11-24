"""Small, simplified data set for the game."""

COUNTIES = [
    {"name": "Budapest", "kind": "city", "x": 4, "y": 2},
    {"name": "Pest", "kind": "mixed", "x": 5, "y": 2},
    {"name": "Fejér", "kind": "mixed", "x": 4, "y": 3},
    {"name": "Komárom-Esztergom", "kind": "mixed", "x": 3, "y": 2},
    {"name": "Veszprém", "kind": "mixed", "x": 3, "y": 3},
    {"name": "Győr-Moson-Sopron", "kind": "mixed", "x": 2, "y": 2},
    {"name": "Vas", "kind": "rural", "x": 1, "y": 3},
    {"name": "Zala", "kind": "rural", "x": 2, "y": 4},
    {"name": "Somogy", "kind": "rural", "x": 3, "y": 4},
    {"name": "Baranya", "kind": "mixed", "x": 4, "y": 5},
    {"name": "Tolna", "kind": "rural", "x": 4, "y": 4},
    {"name": "Bács-Kiskun", "kind": "mixed", "x": 5, "y": 4},
    {"name": "Csongrád-Csanád", "kind": "city", "x": 6, "y": 5},
    {"name": "Békés", "kind": "rural", "x": 7, "y": 5},
    {"name": "Jász-Nagykun-Szolnok", "kind": "mixed", "x": 6, "y": 3},
    {"name": "Hajdú-Bihar", "kind": "mixed", "x": 7, "y": 3},
    {"name": "Szabolcs-Szatmár-Bereg", "kind": "rural", "x": 8, "y": 2},
    {"name": "Borsod-Abaúj-Zemplén", "kind": "mixed", "x": 7, "y": 1},
    {"name": "Heves", "kind": "rural", "x": 6, "y": 1},
    {"name": "Nógrád", "kind": "rural", "x": 5, "y": 1},
]

PARTIES = [
    {"name": "MDF", "founded": 1987, "color": "#aa3333"},
    {"name": "SZDSZ", "founded": 1988, "color": "#3366aa"},
    {"name": "MSZP", "founded": 1989, "color": "#cc5555"},
    {"name": "FKGP", "founded": 1930, "color": "#338844"},
    {"name": "KDNP", "founded": 1944, "color": "#886633"},
    {"name": "Fidesz", "founded": 1988, "color": "#447744"},
    {"name": "MKKP", "founded": 2006, "color": "#aa66aa"},
    {"name": "DK", "founded": 2011, "color": "#4477bb"},
    {"name": "Mi Hazánk", "founded": 2018, "color": "#775533"},
    {"name": "Tisza", "founded": 2024, "color": "#22aabb"},
]

LEADERS = {
    "MDF": ["József Antall — MDF, prime minister"],
    "SZDSZ": ["János Kis — SZDSZ, party leader"],
    "MSZP": ["Gyula Horn — MSZP, party leader"],
    "FKGP": ["József Torgyán — FKGP, party leader"],
    "KDNP": ["László Surján — KDNP, party leader"],
    "Fidesz": ["Viktor Orbán — Fidesz, party leader"],
}

CAMPAIGNS = [
    {"id": "posters", "name": "Posters", "cost": 8, "effect": 1.0, "target": "rural"},
    {"id": "tv", "name": "TV campaign", "cost": 20, "effect": 1.8, "target": "mixed"},
    {"id": "social", "name": "Social media", "cost": 12, "effect": 1.7, "target": "city"},
    {"id": "rallies", "name": "Rallies", "cost": 15, "effect": 1.5, "target": "mixed"},
    {"id": "volunteers", "name": "Volunteers", "cost": 10, "effect": 1.4, "target": "rural"},
    {"id": "candidates", "name": "Candidate registration", "cost": 16, "effect": 1.2, "target": "mixed"},
    {"id": "polling", "name": "Polling", "cost": 9, "effect": 0.6, "target": "city"},
]

POLICIES = [
    {"id": "economy", "name": "Economic investment", "cost": 20, "capital": 2, "effects": {"support": 1, "budget": -12}},
    {"id": "healthcare", "name": "Healthcare", "cost": 18, "capital": 2, "effects": {"support": 2, "budget": -10}},
    {"id": "education", "name": "Education", "cost": 16, "capital": 2, "effects": {"support": 1, "budget": -9}},
    {"id": "eu", "name": "EU relations", "cost": 12, "capital": 1, "effects": {"support": 1, "budget": -5}},
    {"id": "energy", "name": "Energy transition", "cost": 18, "capital": 2, "effects": {"support": 1, "budget": -11}},
    {"id": "media", "name": "Media standards", "cost": 10, "capital": 2, "effects": {"support": 1, "budget": -4}},
    {"id": "anticorruption", "name": "Anti-corruption measures", "cost": 14, "capital": 2, "effects": {"support": 2, "budget": -6}},
    {"id": "immigration", "name": "Migration policy", "cost": 10, "capital": 1, "effects": {"support": 1, "budget": -3}},
    {"id": "housing", "name": "Housing", "cost": 17, "capital": 2, "effects": {"support": 2, "budget": -10}},
    {"id": "taxes", "name": "Tax reform", "cost": 8, "capital": 2, "effects": {"support": 1, "budget": 3}},
]

MENTORS = [
    {"name": "Magyar Péter", "bonus": "Small bonus to anti-corruption and volunteer actions.",
     "facts": "Resigned from Fidesz in 2024 and founded Tisza in 2024. The supplied brief says he led it to a two-thirds majority in April 2026 and became prime minister in May 2026."},
    {"name": "József Antall", "bonus": "Small bonus to education and policy actions.",
     "facts": "Supporters admire his role in the democratic transition. Critics discuss the challenges and policy choices of his government."},
    {"name": "Gyula Horn", "bonus": "Small bonus to coalition and campaign actions.",
     "facts": "Supporters admire his political experience. Critics debate the decisions and legacy of his public career."},
]
