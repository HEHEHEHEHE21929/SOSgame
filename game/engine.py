"""Stateless simulation rules for Magyar Politika."""
import random
from copy import deepcopy
from .data import CAMPAIGN, COUNTIES, DIFFICULTIES, EVENTS, LEADERS, MENTORS, PARTIES, POLICIES

END = 479
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
    for (y0, v0), (y1, v1) in zip(frames, frames[1:]):
        if current_year <= y1:
            return v0 + (v1-v0) * (current_year-y0) / (y1-y0)
    return frames[-1][1]


def vote_shares(state, noise=0):
    raw = {}
    for party, details in PARTIES.items():
        if party == "CUSTOM" and state["party"] != party:
            continue
        value = (max(baseline(party, state["m"]), 3) + state["boost"] if party == state["party"] else
                 baseline(party, state["m"]) if year(state["m"]) >= details["founded"] and baseline(party, state["m"]) > .3 else None)
        if value is not None:
            raw[party] = max(.1, value) * random.uniform(1-noise, 1+noise)
    total = sum(raw.values()) or 1
    return {p: v*100/total for p, v in raw.items()}


def meta():
    return {"parties": {k: {"n": v["n"], "c": v["c"], "f": v["founded"]} for k,v in PARTIES.items()},
            "campaign": CAMPAIGN, "policies": POLICIES, "mentors": MENTORS, "leaders": LEADERS,
            "counties": COUNTIES, "difficulties": DIFFICULTIES}


def op_new(data):
    party = str(data.get("party", "MDF"))
    if party not in PARTIES: raise ValueError("Choose a known party.")
    difficulty = str(data.get("difficulty", "normal"))
    if difficulty not in DIFFICULTIES: difficulty = "normal"
    settings = DIFFICULTIES[difficulty]
    mentor = data.get("mentor", "magyar")
    if mentor not in MENTORS: mentor = "magyar"
    leader = str(data.get("leader") or LEADERS.get(party, ["Party founder"])[0]).strip()[:60]
    pname = str(data.get("pname") or PARTIES[party]["n"]).strip()[:40] or "My Party"
    state = {"m":0,"party":party,"pname":pname,"leader":leader,"mentor":mentor,"difficulty":difficulty,
        "money":settings["money"],"cap":settings["capital"],"boost":0.0,"mood":{"U":0.0,"R":0.0,"M":0.0},
        "spent":{},"reg":False,"polls":0,"inpower":False,"seats":0,"wins":[],"hist":[],"below":0,
        "years_power":0.0,"log":["January 1991: the democratic era begins."],"event":None,"over":None,
        "result":None,"poll":{},"flash":None,"score":0,"founded_seen":[],"county_mps":{},
        "county_support":{},"policy_history":[]}
    state["poll"] = {p:round(v,1) for p,v in vote_shares(state,settings["noise"]).items()}
    return state


def largest_remainder(values, total):
    denominator=sum(values.values()) or 1
    exact={k:v*total/denominator for k,v in values.items()}
    allocated={k:int(v) for k,v in exact.items()}
    remaining=total-sum(allocated.values())
    for key in sorted(exact,key=lambda k:exact[k]-allocated[k],reverse=True)[:remaining]: allocated[key]+=1
    return allocated


def run_election(state):
    player=state["party"]
    difficulty=DIFFICULTIES.get(state.get("difficulty","normal"),DIFFICULTIES["normal"])
    shares=vote_shares(state,difficulty["noise"])
    if not state["reg"]:
        shares[player]*=.6
        total=sum(shares.values()) or 1
        shares={p:v*100/total for p,v in shares.items()}
    eligible={p:v for p,v in shares.items() if v>=5}
    if not eligible:
        p=max(shares,key=shares.get); eligible={p:shares[p]}
    seats=dict.fromkeys(eligible,0); winners=[]
    difficulty_bonus={"easy":1.12,"normal":1.0,"hard":.90}.get(state.get("difficulty"),1.0)
    for i,(_name,county_type,constituency_seats) in enumerate(COUNTIES):
        scores={p:share*lean(p,county_type)*random.uniform(.92,1.08)+(state["mood"][county_type]*2 if p==player and state["inpower"] else 0) for p,share in eligible.items()}
        if player in scores:
            scores[player] *= difficulty_bonus + min(.12,state.get("county_support",{}).get(str(i),0)*.02)
            if str(i) in state.get("county_mps",{}): scores[player] *= 1.03
        winner=max(scores,key=scores.get); seats[winner]+=constituency_seats; winners.append(winner)
    for p,n in largest_remainder(eligible,93).items(): seats[p]+=n
    majority=100; ranked=sorted(seats,key=seats.get,reverse=True); government=ranked[0]
    coalition=ranked[1] if seats[government]<majority and len(ranked)>1 else None
    if coalition and seats[government]+seats[coalition]<majority: coalition=None
    state["inpower"] = government==player or coalition==player
    state["seats"]=seats.get(player,0); state["wins"]=winners
    share=shares.get(player,0); state["below"]=state["below"]+1 if share<5 else 0
    state["result"]={"year":year(state["m"]),"shares":{p:round(v,1) for p,v in shares.items()},"seats":seats,
        "gov":government,"coalition":coalition,"maj":majority,"supermaj":seats[government]*3>=199*2}
    state["hist"].append({"year":year(state["m"]),"seats":state["seats"],"gov":government,"share":round(share,1)})
    state["log"].append(f"{year(state['m'])} election: your party won {state['seats']} simplified seats.")
    state["reg"]=False; state["spent"]={}; state["county_support"]={}
    if state["inpower"]: state["cap"]=min(20,state["cap"]+3)
    if state["below"]>=2: state["over"]="dissolved"; finish(state)


def finish(state):
    state["over"]=state.get("over") or "end"
    state["score"]=sum(x["seats"] for x in state["hist"])+round(state["years_power"]*8)+max(0,round(state["money"]/10))


def op_tick(data):
    state=deepcopy(data["state"])
    if state.get("over") or state.get("event"): return state
    state["result"]=None; state["flash"]=None; state["m"]=min(state["m"]+1,END)
    current_year=year(state["m"]); month_number=state["m"]%12+1
    mentor=MENTORS.get(state["mentor"],MENTORS["magyar"])["bonus"]
    state["money"]+=1.5+state["poll"].get(state["party"],0)*.25+state["seats"]*.05-2
    state["cap"]=min(20,state["cap"]+(1 if state["inpower"] else .3)+mentor.get("cap",0))
    state["boost"]*=.975 if not state["inpower"] else .965
    for group in "UR": state["mood"][group]*=.98
    state["mood"]["M"]=(state["mood"]["U"]+state["mood"]["R"])/2
    if state["money"]<0: state["boost"]-=.08
    if state["inpower"]: state["years_power"]+=1/12
    state["polls"]=max(0,state["polls"]-1)
    settings=DIFFICULTIES.get(state.get("difficulty","normal"),DIFFICULTIES["normal"])
    state["poll"]={p:round(v,1) for p,v in vote_shares(state,.02 if state["polls"] else settings["noise"]).items()}
    if month_number==1:
        for p,info in PARTIES.items():
            if info["founded"]==current_year and current_year>1991 and p!="CUSTOM" and p not in state["founded_seen"]:
                state["founded_seen"].append(p); state["event"]={"id":"new-"+p,"title":"New party founded!","text":f"{info['n']} enters the political landscape in this game year.","choices":[["Continue",{}]]}; break
    if not state.get("event"):
        for event in EVENTS:
            if event["y"]==current_year and event["mo"]==month_number: state["event"]=deepcopy(event); break
    if state["m"] in ELECTIONS: run_election(state)
    if state["m"]>=END: finish(state)
    return state


def op_campaign(data):
    state=deepcopy(data["state"]); action=data.get("action")
    if action not in CAMPAIGN: raise ValueError("Unknown campaign action.")
    label,cost,gain=CAMPAIGN[action]; bonus=MENTORS.get(state["mentor"],MENTORS["magyar"])["bonus"]
    if state["money"]<cost: state["flash"]="Not enough money for that action."; return state
    state["money"]-=cost
    if action=="reg": state["reg"]=True; state["flash"]="Candidates registered for the next election."; return state
    if action=="poll": state["polls"]=6; state["flash"]="More accurate polling is active for six months."; return state
    if action in ("tv","social"): gain*=1+bonus.get("tv",0)
    if action=="vol": gain*=1+bonus.get("vol",0)
    if action=="social" and year(state["m"])>=2010: gain*=1.5
    index=data.get("county")
    if index is not None:
        if not isinstance(index,int) or not 0<=index<len(COUNTIES): raise ValueError("Choose a county on the map first.")
        key=str(index); state["county_support"][key]=state["county_support"].get(key,0)+gain
        state["flash"]=f"{label} campaign held in {COUNTIES[index][0]}; local support improved."
    else:
        actual=gain/(1+state["spent"].get(action,0)/60); state["spent"][action]=state["spent"].get(action,0)+cost
        state["boost"]+=actual; state["flash"]=f"{label}: support increased by {actual:.2f}."
    return state


def op_policy(data):
    state=deepcopy(data["state"]); policy=next((x for x in POLICIES if x["id"]==data.get("id")),None)
    if policy is None: raise ValueError("Unknown policy.")
    if not state["inpower"]: state["flash"]="Policy not enacted: your party must lead the government."
    elif state["cap"]<policy["cap"] or state["money"]<policy["cost"]: state["flash"]="Policy not enacted: insufficient political capital or funds."
    else:
        state["cap"]-=policy["cap"]; state["money"]-=policy["cost"]
        mentor_bonus=MENTORS.get(state["mentor"],MENTORS["magyar"])["bonus"].get("anti",0) if policy["id"]=="anti" else 0
        state["boost"]+=policy["b"]+mentor_bonus; state["mood"]["U"]+=policy["U"]; state["mood"]["R"]+=policy["R"]
        state.setdefault("policy_history",[]).append({"id":policy["id"],"label":policy["label"],"year":year(state["m"]),"status":"enacted"})
        state["flash"]=f"✓ POLICY ENACTED: {policy['label']}. Helps {policy['win']}; trade-off {policy['lose']}."
        state["log"].append(state["flash"])
    return state


def op_appoint(data):
    state=deepcopy(data["state"]); index=data.get("county"); name=str(data.get("name","")).strip()[:60]
    if not isinstance(index,int) or not 0<=index<len(COUNTIES): raise ValueError("Select a county first.")
    if not name: raise ValueError("Enter an MP name.")
    if state["money"]<2: state["flash"]="Not appointed: you need 2 M Ft for local organizing."; return state
    state["money"]-=2; state.setdefault("county_mps",{})[str(index)]=name
    state["flash"]=f"{name} appointed as your local MP candidate for {COUNTIES[index][0]} (2 M Ft)."
    state["log"].append(state["flash"]); return state


def op_choice(data):
    state=deepcopy(data["state"]); event=state.get("event")
    if not event: raise ValueError("There is no event waiting for a choice.")
    choices=event.get("choices",[]); index=data.get("i")
    if not isinstance(index,int) or not 0<=index<len(choices): raise ValueError("Choose one of the displayed event options.")
    effect=choices[index][1]; state["boost"]+=effect.get("b",0); state["money"]+=effect.get("m",0)
    state["cap"]=min(20,state["cap"]+effect.get("c",0)); state["mood"]["U"]+=effect.get("U",0); state["mood"]["R"]+=effect.get("R",0); state["event"]=None
    state["flash"]=f"Decision recorded: {choices[index][0]}. {event.get('text','')}"; return state


def op_mentor(data):
    state=deepcopy(data["state"]); mentor=data.get("mentor")
    if mentor not in MENTORS: raise ValueError("Choose a known mentor.")
    state["mentor"]=mentor; state["flash"]=f"Mentor selected: {MENTORS[mentor]['n']}."; return state
