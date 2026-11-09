"""Data for the interactive Premier League page: every team's cumulative points by game, per season."""
import json, glob, sys, collections
D = sys.argv[1]
seasons = []
for f in sorted(glob.glob(D + "/epl-20*.json")):
    s = f.split("epl-")[1][:7]; Y = int(s[:4])
    m = [x for x in json.load(open(f))["matches"] if isinstance(x.get("score"), dict) and x["score"].get("ft")]
    if len(m) < 380:
        continue
    for x in m:  # 2019-20 restart games are dated a year early in the source
        if x["date"] < f"{Y}-08-01":
            x["date"] = str(Y + 1) + x["date"][4:]
    m.sort(key=lambda x: (x["date"], x.get("time") or ""))
    cum = collections.defaultdict(list); gf = collections.Counter(); ga = collections.Counter()
    hw = dw = aw = goals = 0
    for x in m:
        h, a = x["team1"], x["team2"]; g1, g2 = x["score"]["ft"]; goals += g1 + g2
        hw += g1 > g2; dw += g1 == g2; aw += g1 < g2
        for t, p, f_, a_ in ((h, 3 if g1 > g2 else 1 if g1 == g2 else 0, g1, g2), (a, 3 if g2 > g1 else 1 if g1 == g2 else 0, g2, g1)):
            cum[t].append((cum[t][-1] if cum[t] else 0) + p); gf[t] += f_; ga[t] += a_
    teams = sorted(cum, key=lambda t: (-cum[t][-1], -(gf[t] - ga[t]), -gf[t]))
    seasons.append(dict(season=s, home=round(hw / 3.8, 1), draw=round(dw / 3.8, 1), away=round(aw / 3.8, 1),
                        goals=goals, gpg=round(goals / 380, 2),
                        teams=[dict(name=t.replace(" FC", "").replace("AFC ", ""), pts=cum[t], gd=gf[t] - ga[t]) for t in teams]))
json.dump(dict(seasons=seasons, now=json.load(open(D + "/epl_table_now.json"))), open(D + "/epl_web.json", "w"), separators=(",", ":"))
for s in seasons:
    print(s["season"], s["teams"][0]["name"], s["teams"][0]["pts"][-1], s["teams"][0]["pts"][9], "|", s["teams"][1]["name"], s["teams"][1]["pts"][-1])
