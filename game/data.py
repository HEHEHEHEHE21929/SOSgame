"""Simplified, classroom-friendly game data."""
DIFFICULTIES={"easy":{"name":"Easy","money":150.0,"capital":5.0,"noise":.03},"normal":{"name":"Normal","money":100.0,"capital":3.0,"noise":.07},"hard":{"name":"Hard","money":75.0,"capital":2.0,"noise":.12}}


def policy(i,label,cap,cost,boost,urban,rural,helps,tradeoff):
    return {"id":i,"label":label,"cap":cap,"cost":cost,"b":boost,"U":urban,"R":rural,"win":helps,"lose":tradeoff}


def event(i,y,month,title,text,*choices):
    return {"id":i,"y":y,"mo":month,"title":title,"text":text,"choices":[list(choice) for choice in choices]}

PARTIES={
"MDF":{"n":"MDF","c":"#00aa00","founded":1988,"lean":(1,1.1),"support":[(1991,25),(1994,12),(1998,3),(2002,0)]},
"SZDSZ":{"n":"SZDSZ","c":"#ff55ff","founded":1988,"lean":(1.5,.6),"support":[(1991,20),(1994,19),(1998,8),(2006,6),(2010,0)]},
"MSZP":{"n":"MSZP","c":"#ff5555","founded":1989,"lean":(1,1),"support":[(1991,12),(1994,33),(1998,32),(2002,42),(2010,19),(2018,12),(2022,10),(2026,2)]},
"FKGP":{"n":"FKGP","c":"#aa5500","founded":1988,"lean":(.6,1.5),"support":[(1991,10),(1994,9),(1998,3),(2002,0)]},
"KDNP":{"n":"KDNP","c":"#aa00aa","founded":1989,"lean":(.8,1.2),"support":[(1991,7),(1994,7),(1998,3),(2002,0)]},
"FIDESZ":{"n":"Fidesz","c":"#ff9922","founded":1988,"lean":(.9,1.15),"support":[(1991,6),(1994,7),(1998,29),(2002,41),(2010,53),(2018,49),(2022,54),(2026,39)]},
"DK":{"n":"DK","c":"#5555ff","founded":2011,"lean":(1.4,.6),"support":[(2011,3),(2018,6),(2022,12),(2026,4)]},
"MKKP":{"n":"MKKP","c":"#ffff55","founded":2006,"lean":(1.6,.5),"support":[(2006,.5),(2018,1.7),(2022,3.2),(2026,2)]},
"MIHAZANK":{"n":"Mi Hazánk","c":"#888888","founded":2018,"lean":(.7,1.3),"support":[(2018,1),(2022,6),(2026,6)]},
"TISZA":{"n":"Tisza","c":"#00aaaa","founded":2024,"lean":(1.2,.95),"support":[(2024,10),(2025,30),(2026,53),(2028,48)]},
"CUSTOM":{"n":"My Party","c":"#ffffff","founded":1991,"lean":(1,1),"support":[(1991,3)]}}

LEADERS={
"MDF":["Antall József — MDF leader and prime minister"],"SZDSZ":["Kis János — SZDSZ founding leader"],
"MSZP":["Horn Gyula — MSZP leader"],"FKGP":["Torgyán József — FKGP leader"],
"KDNP":["Surján László — KDNP leader"],"FIDESZ":["Orbán Viktor — Fidesz founding-generation leader"],"CUSTOM":["Party founder"]}

COUNTIES=[
("Budapest","U",16),("Pest","U",12),("Győr-Moson-Sopron","M",6),("Komárom-Esztergom","M",4),("Fejér","M",5),("Veszprém","M",5),("Vas","R",3),("Zala","R",3),("Somogy","R",4),("Tolna","R",3),("Baranya","M",4),("Bács-Kiskun","R",6),("Csongrád-Csanád","M",4),("Békés","R",4),("Jász-Nagykun-Szolnok","R",4),("Heves","M",3),("Nógrád","R",2),("Borsod-Abaúj-Zemplén","R",8),("Hajdú-Bihar","M",5),("Szabolcs-Szatmár-Bereg","R",5)]

CAMPAIGN={"posters":("Posters",5,.4),"tv":("TV ads",20,1.6),"social":("Social media",10,.9),"rally":("Rallies",8,.8),"vol":("Volunteers",3,.5),"reg":("Register candidates",30,0),"poll":("Accurate polling",4,0)}

POLICIES=[
policy("tax","Cut income tax",2,15,.5,.4,.2,"Workers","Public services"),policy("health","Fund hospitals",2,20,.7,.2,.6,"Patients and rural towns","Taxpayers"),policy("edu","Raise teacher pay",2,15,.5,.4,.3,"Teachers and families","The budget"),policy("eu","Seek an EU funds deal",3,5,.6,.6,-.2,"Cities and business","Sovereignty-minded voters"),policy("energy","Invest in energy",3,25,.4,.2,.3,"Industry","Short-term bills"),policy("media","Reform public media",3,5,.3,.5,-.4,"Pluralism supporters","Fans of existing coverage"),policy("anti","Anti-corruption office",3,10,.6,.5,.2,"Taxpayers","People concerned about disruption"),policy("immig","Tighten border rules",2,5,.4,-.3,.6,"Security-minded voters","Employers needing workers"),policy("house","Build affordable housing",3,25,.6,.7,-.1,"Young renters","Property owners and taxpayers"),policy("fuel","Cap fuel prices",2,15,.5,-.2,.6,"Drivers","Climate goals and the budget")]

EVENTS=[
 event("transition",1993,1,"Economic transition","Hungary continues its transition to a market economy.",("Support faster reforms",{"b":-.3,"U":.3,"c":2}),("Favor a gradual approach",{"b":.3,"R":.3})),
 event("nato",1999,3,"Hungary joins NATO","A significant change in Hungary's security relationships.",("Welcome the membership",{"b":.5}),("Debate the costs",{"m":10,"R":.2})),
 event("eu",2004,5,"Hungary joins the European Union","EU membership brings new opportunities and policy debates.",("Focus on EU cooperation",{"b":.6,"U":.3}),("Emphasize national decision-making",{"b":.4,"R":.3})),
 event("crisis",2008,10,"Global financial crisis","The global crisis puts pressure on households and public finances.",("Prioritize spending restraint",{"b":-.4,"c":2}),("Support an economic stimulus",{"m":-15,"b":.5})),
 event("migration",2015,9,"Migration crisis","Migration becomes a major subject of public debate.",("Emphasize border security",{"R":.5,"U":-.3}),("Emphasize humanitarian support",{"U":.4,"R":-.4})),
 event("covid",2020,3,"COVID-19","The pandemic creates difficult public health and economic choices.",("Support stricter public-health rules",{"b":.3}),("Emphasize individual choice",{"b":.3,"R":.2})),
 event("ukraine",2022,2,"War in Ukraine","The war next door creates difficult security and foreign-policy choices.",("Support stronger sanctions",{"U":.4,"R":-.2}),("Prioritize diplomacy",{"R":.4,"U":-.2}))]

MENTORS={"magyar":{"n":"Magyar Péter","bonus":{"anti":.6,"vol":.4},"facts":["Resigned from Fidesz in 2024","Founded Tisza in 2024","Led Tisza to a two-thirds majority in April 2026","Became prime minister in May 2026"],"learn":"Supporters admire his anti-corruption message and challenge to a long-ruling government. Critics note his years as a Fidesz insider and question how different his government will be."},"antall":{"n":"Antall József","bonus":{"cap":.2},"facts":["First prime minister after the 1990 free elections","Led the MDF"],"learn":"Supporters admire his leadership through the post-communist transition. Critics point to economic difficulties and the pace of reform during the period."},"horn":{"n":"Horn Gyula","bonus":{"tv":.3},"facts":["Prime minister from 1994 to 1998","Led the MSZP"],"learn":"Supporters credit him with economic stabilization and Hungary's path toward NATO and EU membership. Critics point to the unpopular austerity package of 1995."},"orban":{"n":"Orbán Viktor","bonus":{"vol":.2,"tv":.2},"facts":["Prime minister during 1998–2002 and 2010–2026","Leader of Fidesz"],"learn":"Supporters value his emphasis on national sovereignty and family policy. Critics argue that his governments weakened checks and balances and tolerated corruption."}}
