import json
TR, CA, ME = "travertino", "canale", "memoria"
def V(clip, a, b, look, speed="slow", nat=None):
    d = {"t": "video", "clip": clip, "a": a, "b": b, "look": look, "speed": speed}
    if nat: d["nat"] = nat
    return d
def Ph(src, look, dur, c0=(.5,.5), c1=(.5,.5), z0=1.0, z1=1.08, nat=None):
    d = {"t": "photo", "src": src, "look": look, "dur": dur, "c0": c0, "c1": c1, "z0": z0, "z1": z1}
    if nat: d["nat"] = nat
    return d
def E(src, look, quote, dur=4.6, sub=None, nat=None):
    d = {"t": "end", "src": src, "look": look, "dur": dur, "quote": quote}
    if sub: d["sub"] = sub
    if nat: d["nat"] = nat
    return d
def F(inner, ground, label, nat=None):
    d = {"t": "frame", "inner": inner, "ground": ground, "label": label}
    if nat: d["nat"] = nat
    return d
P1 = dict(c0=(.32,.45), c1=(.62,.45))
P2a = dict(c0=(.28,.5), c1=(.5,.5)); P2b = dict(c0=(.72,.5), c1=(.5,.5))
P4 = dict(c0=(.24,.5), c1=(.5,.5))
jobs = [
 {"id":"01-someday","title":"Someday","kind":"Compilation · music","sound":"music","music":"dolce","card":"twilight","end":"twilight",
  "kicker":"ITALIA","hook":"How long have you\nbeen saying\n“someday”?",
  "segs":[V("rome",12.0,17.5,TR), Ph("2",TR,4.6,**P2a), F(V("venice",0.0,2.55,CA),"teal","VENEZIA"), Ph("5",TR,4.2,c0=(.5,.42),c1=(.5,.36)), E("2",TR,"Someday is not a date.\nChoose one.")],
  "cards":[{"seg":1,"text":"Someday never\nbooks the flight."},{"seg":3,"text":"You do."}]},
 {"id":"02-venice-unhurried","title":"Venice, Unhurried","kind":"B-roll · natural sound","sound":"natural","music":"dolce","bed":0.12,"card":"teal","end":"teal",
  "kicker":"VENEZIA","hook":"When did you last\nlet yourself\nslow down?",
  "segs":[Ph("10",CA,4.4,c0=(.36,.5),c1=(.52,.5),z0=1.0,z1=1.06,nat=["venice","amb"]), V("venice",0.0,1.9,CA,"rt",nat=["venice","sync"]),
          F(Ph("6",CA,4.6,c0=(.5,.45),c1=(.5,.45),z0=1.0,z1=1.12),"twilight","VENEZIA · TORRE DELL'OROLOGIO",nat=["venice","amb",0.8]),
          Ph("7",TR,4.8,c0=(.6,.45),c1=(.6,.45),z0=1.0,z1=1.1,nat=["venice","amb",0.8]),
          F(Ph("8",TR,4.0,c0=(.45,.4),c1=(.5,.5),z0=1.05,z1=1.0),"lagoon","BASILICA DI SAN MARCO",nat=["venice","amb",0.8]),
          Ph("9",CA,3.6,c0=(.55,.62),c1=(.55,.42),z0=1.18,z1=1.18,nat=["venice","amb",0.8]),
          E("10",CA,"Slow is not behind.\nSlow is how you\ncome back to yourself.",nat=["venice","amb",0.6])],
  "cards":[{"seg":2,"text":"Venice doesn't rush."},{"seg":3,"text":"Neither should\nyour healing.","cy":560}]},
 {"id":"03-still-standing","title":"Still Standing","kind":"Photo compilation · music","sound":"music","music":"memoria","card":"terracotta","end":"terracotta",
  "kicker":"POMPEII","hook":"Buried for nearly\n1,700 years.\nStill standing.",
  "segs":[Ph("2",TR,5.0,**P2a), F(Ph("1",TR,4.4,**P1),"travertine","POMPEII · CAMPANIA"), Ph("5",TR,4.4,c0=(.5,.45),c1=(.5,.35)), Ph("4",TR,4.4,**P4), E("5",TR,"You are not ruined.\nYou are being uncovered.")],
  "cards":[{"seg":1,"text":"What got buried in you\nisn't gone."},{"seg":3,"text":"It's waiting\nto be uncovered."}]},
 {"id":"04-more-time","title":"They Thought There Was More Time","kind":"Photo compilation · music","sound":"music","music":"memoria","music_start":8,"card":"twilight","end":"twilight",
  "kicker":"POMPEII · 79 AD","hook":"They thought\nthere would be\nmore time.",
  "segs":[Ph("2",ME,4.2,**P2b), Ph("3",ME,6.0,c0=(.47,.56),c1=(.47,.56),z0=1.0,z1=1.14), F(Ph("4",ME,4.4,**P4),"travertine","POMPEII"), E("2",ME,"Your life is happening now.\nNot after.")],
  "cards":[{"seg":1,"text":"So do we."},{"seg":2,"text":"What are you\nstill postponing?"}]},
 {"id":"05-next-step","title":"Just the Next Step","kind":"B-roll · natural sound","sound":"natural","music":"dolce","bed":0.14,"card":"terracotta","end":"cream",
  "kicker":"ROMA","hook":"You don't need to\nsee the whole road.",
  "segs":[V("rome",0.0,3.9,TR,"rt",nat=["rome","sync"]), V("rome",4.0,8.2,TR,"rt",nat=["rome","sync"]), F(V("rome",18.0,24.5,TR),"clay","ROMA · VIA DEI FORI IMPERIALI",nat=["rome","amb"]), E("rome@7.6",TR,"Keep walking.\nIt gets closer.",nat=["rome","amb",0.6])],
  "cards":[{"seg":1,"text":"Just the next step."},{"seg":2,"text":"It looks far from here.\nIt always does at the start."}]},
 {"id":"06-observer","title":"Living or Watching","kind":"B-roll · music","sound":"music","music":"dolce","music_start":12,"card":"teal","end":"teal",
  "kicker":"VENEZIA · ROMA · POMPEII","hook":"Are you living\nyour life, or\njust watching it?",
  "segs":[V("venice",2.6,5.8,CA), V("rome",0.0,2.7,TR), F(Ph("4",TR,4.6,**P4),"travertine","POMPEII"), Ph("7",TR,4.8,c0=(.6,.45),c1=(.6,.45),z0=1.0,z1=1.1), E("7",TR,"Step out of\nthe background.")],
  "cards":[{"seg":2,"text":"Watching feels safe.\nNo one can see you there."},{"seg":3,"text":"But you didn't come\nthis far to stay invisible.","cy":560}]},
 {"id":"07-under-construction","title":"Under Construction","kind":"B-roll · music","sound":"music","music":"memoria","music_start":16,"card":"terracotta","end":"cream",
  "kicker":"VENEZIA · POMPEII","hook":"The cracks didn't\nmake it less\nbeautiful.",
  "segs":[V("venice",6.0,9.2,CA), Ph("1",TR,5.0,**P1), F(Ph("5",TR,4.6,c0=(.5,.42),c1=(.5,.34)),"golden","POMPEII"), E("1",TR,"Cracked is not finished.\nKeep building.")],
  "cards":[{"seg":1,"text":"Even ancient things\nget restored.","a":3.6},{"seg":2,"text":"You're allowed to be\nunder construction."}]},
 {"id":"08-seven-places","title":"Seven Places","kind":"Compilation · natural sound","sound":"natural","music":"passeggiata","bed":0.2,"end":"twilight",
  "kicker":"ITALIA · NOVEMBER 2026","hook":"Seven places.\nOne trip.\nOne decision:\nI was worth it.","hook_end":3.6,
  "segs":[V("venice",0.0,1.9,CA,"rt",nat=["venice","sync"]), V("rome",4.0,8.2,TR,"rt",nat=["rome","sync"]), V("rome",0.0,3.9,TR,"rt",nat=["rome","sync"]), Ph("2",TR,4.2,**P2a,nat=["rome","amb",0.5]), F(Ph("4",TR,3.6,**P4),"clay","POMPEII",nat=["rome","amb",0.5]),
          E("2",TR,"What would you see\nif you decided\nyou were worth it?",dur=5.2,sub="VENICE · FLORENCE · TUSCANY · ASSISI\nROME · THE VATICAN · POMPEII")],
  "cards":[{"seg":1,"text":"ROMA","place":True,"a":3.75},{"seg":3,"text":"POMPEII","place":True}]},
 {"id":"09-whats-possible","title":"What's Possible","kind":"Fast montage · music","sound":"music","music":"passeggiata","card":"teal","end":"terracotta",
  "kicker":"ITALIA","hook":"This is what's possible\nwhen you stop\nshrinking.",
  "segs":[V("venice",0.0,2.55,CA), V("rome",13.0,16.0,TR), Ph("2",TR,2.6,**P2a), F(Ph("5",TR,2.4,c0=(.5,.4),c1=(.5,.35)),"golden","POMPEII"), V("venice",6.2,8.6,CA), F(Ph("1",TR,2.6,**P1),"lagoon","POMPEII"), Ph("7",TR,3.0,c0=(.6,.45),c1=(.6,.45),z0=1.0,z1=1.08), Ph("10",CA,2.6,c0=(.36,.5),c1=(.52,.5)), E("2",TR,"Where would you go\nif you stopped\nasking permission?")],
  "cards":[{"seg":4,"text":"You were never\ntoo much.","b":None},{"seg":6,"text":"You were meant\nfor more.","cy":560}]},
 {"id":"10-temporary","title":"This Too Is Temporary","kind":"Photo B-roll · music","sound":"music","music":"dolce","music_start":24,"card":"twilight","end":"cream",
  "kicker":"IL FORO · POMPEII","hook":"Thousands walked here,\nsure their worries\nwere permanent.",
  "segs":[Ph("2",TR,5.4,c0=(.25,.5),c1=(.45,.5),z0=1.0,z1=1.1), Ph("2",TR,4.6,c0=(.78,.48),c1=(.62,.5),z0=1.12,z1=1.0), F(Ph("5",TR,4.4,c0=(.5,.45),c1=(.5,.36)),"travertine","POMPEII"), E("2",TR,"This too is temporary.\nYou are not stuck.")],
  "cards":[{"seg":1,"text":"They weren't."},{"seg":2,"text":"Neither are yours."}]},
]
jobs.append({"id":"A01-adventure","title":"Italia, Come With Me","kind":"Adventure montage · natural sound + music","sound":"natural","music":"passeggiata","bed":0.32,"card":"teal","end":"twilight",
  "kicker":"ITALIA · NOVEMBER 2026","hook":"This is what it\nlooks like when\nyou finally go.",
  "segs":[Ph("10",CA,4.2,c0=(.34,.5),c1=(.5,.5),nat=["venice","amb"]), V("venice",0.0,1.9,CA,"rt",nat=["venice","sync"]),
          F(Ph("6",CA,3.6,z0=1.0,z1=1.1),"twilight","VENEZIA · TORRE DELL'OROLOGIO",nat=["venice","amb",0.8]),
          Ph("8",TR,3.2,c0=(.45,.35),c1=(.5,.5),z0=1.08,z1=1.0,nat=["venice","amb",0.8]),
          Ph("7",TR,3.6,c0=(.6,.45),c1=(.6,.45),z0=1.0,z1=1.08,nat=["venice","amb",0.8]),
          Ph("9",CA,3.0,c0=(.55,.62),c1=(.55,.45),z0=1.18,z1=1.18,nat=["venice","amb",0.8]),
          V("rome",0.0,3.9,TR,"rt",nat=["rome","sync"]), V("rome",4.0,8.2,TR,"rt",nat=["rome","sync"]),
          F(V("rome",18.0,22.5,TR),"clay","ROMA · VIA DEI FORI IMPERIALI",nat=["rome","amb"]),
          Ph("2",TR,4.0,**P2a,nat=["rome","amb",0.5]), F(Ph("1",TR,3.6,**P1),"travertine","POMPEII · CAMPANIA",nat=["rome","amb",0.4]),
          Ph("5",TR,3.2,c0=(.5,.45),c1=(.5,.35),nat=["rome","amb",0.4]), F(Ph("4",TR,3.4,**P4),"golden","POMPEII",nat=["rome","amb",0.4]),
          E("10",CA,"The trip you keep\npostponing is\nwaiting for you.",dur=5.0,sub="VENICE · FLORENCE · TUSCANY · ASSISI\nROME · THE VATICAN · POMPEII")],
  "cards":[{"seg":1,"text":"VENEZIA","place":True,"a":3.75},{"seg":6,"text":"ROMA","place":True},{"seg":9,"text":"POMPEII","place":True}]})
for j in jobs:
    for c in j.get("cards", []):
        if c.get("b", 0) is None: del c["b"]
json.dump(jobs, open("jobs.json","w"), indent=1)
print(len(jobs))
