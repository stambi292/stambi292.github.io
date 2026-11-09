"""Season-level Premier League stats from openfootball results (2010-11 to 2024-25)."""
import json, glob, collections, sys
rows = []
for f in sorted(glob.glob(sys.argv[1] + "/epl-20*.json")):
    s = f.split("epl-")[1][:7]; Y = int(s[:4])
    m = [x for x in json.load(open(f))["matches"] if isinstance(x.get("score"), dict) and x["score"].get("ft")]
    if len(m) < 380:
        continue
    fixed = 0
    for x in m:  # some 2019-20 restart games are dated a year too early in the source
        if x["date"] < f"{Y}-08-01":
            x["date"] = str(Y + 1) + x["date"][4:]; fixed += 1
    m.sort(key=lambda x: (x["date"], x.get("time") or ""))
    pts, gp, gd, after10 = collections.Counter(), collections.Counter(), collections.Counter(), {}
    hw = dw = aw = goals = 0
    for x in m:
        h, a = x["team1"], x["team2"]; g1, g2 = x["score"]["ft"]; goals += g1 + g2
        ph, pa = (3, 0) if g1 > g2 else (1, 1) if g1 == g2 else (0, 3)
        hw += g1 > g2; dw += g1 == g2; aw += g1 < g2
        for t, p, d in ((h, ph, g1 - g2), (a, pa, g2 - g1)):
            pts[t] += p; gp[t] += 1; gd[t] += d
            if gp[t] == 10:
                after10[t] = pts[t]
    champ = max(pts, key=lambda t: (pts[t], gd[t]))
    best = max(after10.values())
    rows.append(dict(season=s, champ=champ.replace(" FC", ""), champ_pts=pts[champ], champ_after10=after10[champ],
                     best_after10=best, best_teams=[t.replace(" FC", "") for t in after10 if after10[t] == best],
                     home_win=round(hw / 3.8, 1), draw=round(dw / 3.8, 1), away_win=round(aw / 3.8, 1),
                     goals_per_game=round(goals / 380, 2), goals=goals, dates_fixed=fixed))
json.dump(rows, open(sys.argv[1] + "/epl_seasons.json", "w"), indent=1)
for r in rows: print(r)
