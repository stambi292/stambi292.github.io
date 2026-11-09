"""Leverkusen 2023/24 Bundesliga: goals by minute, late goals and points they saved (StatsBomb open data)."""
import json, sys, collections
D = sys.argv[1]
matches = json.load(open(f"{D}/sb/bl2324.json"))
TEAM = "Bayer Leverkusen"
out = []
for m in sorted(matches, key=lambda m: m["match_date"]):
    home = m["home_team"]["home_team_name"]; away = m["away_team"]["away_team_name"]
    if TEAM not in (home, away):
        continue
    ev = json.load(open(f"{D}/sb/events/{m['match_id']}.json"))
    goals = []  # (minute, scorer_team)
    xg = collections.Counter()
    for e in ev:
        t = e["type"]["name"]; team = e["team"]["name"]
        if e["period"] > 2:
            continue
        if t == "Shot":
            xg[team] += e["shot"].get("statsbomb_xg", 0)
            if e["shot"]["outcome"]["name"] == "Goal":
                goals.append((e["minute"], team, e["player"]["name"], e["period"]))
        elif t == "Own Goal For":
            goals.append((e["minute"], team, "own goal", e["period"]))
    opp = away if home == TEAM else home
    lev = [g for g in goals if g[1] == TEAM]; vs = [g for g in goals if g[1] != TEAM]
    def pts(a, b): return 3 if a > b else 1 if a == b else 0
    full = pts(len(lev), len(vs))
    before90 = pts(len([g for g in lev if g[0] < 90]), len([g for g in vs if g[0] < 90]))
    before85 = pts(len([g for g in lev if g[0] < 85]), len([g for g in vs if g[0] < 85]))
    sm = (m["home_score"], m["away_score"]) if home == TEAM else (m["away_score"], m["home_score"])
    out.append(dict(date=m["match_date"], opponent=opp, venue="H" if home == TEAM else "A",
                    score=f"{len(lev)}-{len(vs)}", official=f"{sm[0]}-{sm[1]}",
                    goal_minutes=[g[0] for g in lev], goal_periods=[g[3] for g in lev], late_scorers=[(g[0], g[2]) for g in lev if g[0] >= 85],
                    conceded_minutes=[g[0] for g in vs],
                    xg_for=round(xg[TEAM], 2), xg_against=round(xg[opp], 2),
                    points=full, points_if_ended_85=before85, points_if_ended_90=before90))
json.dump(out, open(f"{D}/leverkusen.json", "w"), indent=1)
mism = [o for o in out if o["score"] != o["official"]]
print("matches", len(out), "score mismatches", [(o["opponent"], o["score"], o["official"]) for o in mism])
W = sum(o["points"] == 3 for o in out); Dr = sum(o["points"] == 1 for o in out)
print("W D L", W, Dr, len(out) - W - Dr, "pts", sum(o["points"] for o in out))
allg = [mm for o in out for mm in o["goal_minutes"]]; con = [mm for o in out for mm in o["conceded_minutes"]]
print("goals", len(allg), "conceded", len(con))
print("goals 85+", sum(mm >= 85 for mm in allg), "goals 90+", sum(mm >= 90 for mm in allg))
print("pts if ended 85", sum(o["points_if_ended_85"] for o in out), "if ended 90", sum(o["points_if_ended_90"] for o in out))
print("xG for/against", round(sum(o["xg_for"] for o in out), 1), round(sum(o["xg_against"] for o in out), 1))
b = collections.Counter(min(mm // 15, 6) for mm in allg); print("by 15-min", sorted(b.items()))
for o in out:
    if o["points"] != o["points_if_ended_85"]:
        print(" late swing:", o["date"], o["venue"], o["opponent"], o["score"], o["late_scorers"], o["points_if_ended_85"], "->", o["points"])
