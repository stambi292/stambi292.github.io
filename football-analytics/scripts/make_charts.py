"""
LinkedIn charts (1080 x 1350 px) for the football analytics posts.

Usage:
    python make_charts.py <data_dir> <out_dir> ["Your Name"]
The optional name is printed in each chart's footer, so shared images stay credited to you.
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mplsoccer import Pitch, VerticalPitch

D = Path(sys.argv[1])
OUT = Path(sys.argv[2])
AUTHOR = sys.argv[3] if len(sys.argv) > 3 else ""
OUT.mkdir(parents=True, exist_ok=True)

BG = "#fbfbf9"
INK = "#111312"
INK2 = "#4f5451"
MUTED = "#8a8f8a"
GRID = "#e4e5e0"
CONTEXT = "#c9ccc5"
ACCENT = "#2a78d6"
HOT = "#e34948"
PITCH = "#f1f2ee"
LINES = "#c3c6bf"

plt.rcParams.update({
    "font.family": "Inter",
    "axes.edgecolor": CONTEXT,
    "axes.labelcolor": INK2,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "font.size": 11,
})


def frame(title, subtitle, source):
    fig = plt.figure(figsize=(7.2, 9), dpi=150, facecolor=BG)
    fig.text(0.07, 0.955, title, fontsize=21, fontweight="bold", color=INK, va="top",
             family="Inter Display", linespacing=1.15)
    fig.text(0.07, 0.83, subtitle, fontsize=11.5, color=INK2, va="top", linespacing=1.45)
    foot = f"Data: {source}" + (f"   ·   {AUTHOR}" if AUTHOR else "")
    fig.text(0.07, 0.03, foot, fontsize=9, color=MUTED, va="bottom")
    return fig


def clean(ax, grid_axis="x"):
    ax.set_facecolor(BG)
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0, labelsize=10.5)
    if grid_axis:
        ax.grid(axis=grid_axis, color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)


def save(fig, name):
    fig.savefig(OUT / name, dpi=150, facecolor=BG)
    plt.close(fig)
    print("  wrote", name)


# ---------------------------------------------------------------- 1. Arsenal's start
def arsenal_start():
    seasons = json.load(open(D / "epl_seasons.json"))
    now = json.load(open(D / "epl_table_now.json"))
    ars = next(t for t in now["table"] if t["team"].startswith("Arsenal"))
    played = ars["wins"] + ars["draws"] + ars["losses"]
    assert played == 10, played
    avg = sum(s["champ_after10"] for s in seasons) / len(seasons)

    labels = [f"Arsenal {now['season']}"] + [f"{s['champ']} {s['season']}" for s in reversed(seasons)]
    vals = [ars["points"]] + [s["champ_after10"] for s in reversed(seasons)]
    colors = [ACCENT] + [CONTEXT] * len(seasons)

    fig = frame("Arsenal's start beats\n12 of the last 15 champions",
                f"Points after 10 Premier League games. Grey bars are each season's\n"
                f"eventual champion. Only three champions started better (28 points);\n"
                f"the average champion had {avg:.1f}.",
                f"openfootball results 2010-11 to 2024-25; Premier League table, {now['as_of']}")
    ax = fig.add_axes([0.42, 0.11, 0.5, 0.63])
    clean(ax)
    y = list(range(len(vals)))[::-1]
    ax.barh(y, vals, color=colors, height=0.68)
    for yy, v, c in zip(y, vals, colors):
        ax.text(v + 0.4, yy, str(v), va="center", fontsize=10.5, color=INK if c == ACCENT else INK2,
                fontweight="bold" if c == ACCENT else "normal")
    ax.set_yticks(y, labels)
    for t, c in zip(ax.get_yticklabels(), colors):
        t.set_color(INK if c == ACCENT else INK2)
        t.set_fontweight("bold" if c == ACCENT else "normal")
        t.set_fontsize(10.5)
    ax.set_xlim(0, 31)
    ax.set_ylim(-0.6, len(vals) - 0.4)
    ax.set_xticks([0, 10, 20, 30])
    fig.text(0.07, 0.065, "Arsenal also had 27 points after 10 games in 2022-23, and finished 2nd.",
             fontsize=10, color=INK, fontweight="bold")
    save(fig, "01_arsenal_start.png")


# ---------------------------------------------------------------- 2. Leverkusen late goals
def leverkusen():
    games = json.load(open(D / "leverkusen.json"))
    minutes = [m for g in games for m in g["goal_minutes"]]
    periods = [p for g in games for p in g["goal_periods"]]
    bins = ["1-15", "16-30", "31-45+", "46-60", "61-75", "76-90", "90+"]
    # StatsBomb minutes are elapsed minutes (minute 0 = 1st minute); stoppage time keeps counting
    # past 45 / 90, so the period decides which half a goal belongs to.
    counts = Counter()
    for m, p in zip(minutes, periods):
        if p == 1:
            counts[min(m // 15, 2)] += 1
        else:
            counts[6 if m >= 90 else 3 + (m - 45) // 15] += 1
    vals = [counts[i] for i in range(7)]
    swings = [g for g in games if g["points"] != g["points_if_ended_85"]]
    saved = sum(g["points"] - g["points_if_ended_85"] for g in swings)
    late = sum(m >= 85 for m in minutes)

    fig = frame("Leverkusen's unbeaten season\nwas saved in the last minutes",
                f"Bundesliga 2023/24: 28 wins, 6 draws, 0 defeats. {late} of their {len(minutes)} goals\n"
                f"came after the 85th minute, and those goals were worth {saved} points.",
                "StatsBomb open data, Bundesliga 2023/24")
    ax = fig.add_axes([0.1, 0.43, 0.84, 0.33])
    clean(ax, "y")
    colors = [CONTEXT] * 5 + [ACCENT, ACCENT]
    bars = ax.bar(bins, vals, color=colors, width=0.66)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.4, str(v), ha="center", fontsize=11, color=INK)
    ax.set_ylim(0, 23)
    ax.set_yticks([0, 5, 10, 15, 20])
    ax.set_xlabel("Goals scored, by minute of the match", fontsize=10.5, color=INK2, labelpad=8)

    fig.text(0.07, 0.345, "Matches decided after the 85th minute", fontsize=12.5, fontweight="bold", color=INK)
    names = {"Borussia Dortmund": "Dortmund", "VfB Stuttgart": "Stuttgart", "RB Leipzig": "RB Leipzig",
             "Hoffenheim": "Hoffenheim", "Augsburg": "Augsburg"}
    res = {0: "defeat", 1: "draw", 3: "win"}
    y0 = 0.305
    fig.text(0.07, y0, "Opponent", fontsize=9.5, color=MUTED)
    fig.text(0.38, y0, "Before the late goal", fontsize=9.5, color=MUTED)
    fig.text(0.65, y0, "Final result", fontsize=9.5, color=MUTED)
    for i, g in enumerate(swings):
        y = y0 - 0.037 * (i + 1)
        venue = "(home)" if g["venue"] == "H" else "(away)"
        fig.text(0.07, y, f"{names.get(g['opponent'], g['opponent'])} {venue}", fontsize=11, color=INK)
        before = res[g["points_if_ended_85"]]
        fig.text(0.38, y, before, fontsize=11, color=HOT if before == "defeat" else INK2)
        scorer = g["late_scorers"][-1]
        fig.text(0.65, y, f"{res[g['points']]} {g['score']}  ({scorer[0] + 1}')", fontsize=11,
                 color=ACCENT, fontweight="bold")
    save(fig, "02_leverkusen_late_goals.png")


# ---------------------------------------------------------------- 3. Spain shot map
def spain_shots():
    eu = json.load(open(D / "sb/euro24.json"))
    shots = []
    for m in eu:
        if "Spain" not in (m["home_team"]["home_team_name"], m["away_team"]["away_team_name"]):
            continue
        for e in json.load(open(D / f"sb/events/{m['match_id']}.json")):
            if e["type"]["name"] == "Shot" and e["team"]["name"] == "Spain" and e["period"] <= 4:
                shots.append((e["location"][0], e["location"][1], e["shot"]["statsbomb_xg"],
                              e["shot"]["outcome"]["name"] == "Goal"))
    goals = sum(s[3] for s in shots)
    xg = sum(s[2] for s in shots)
    fig = frame("Spain at Euro 2024:\nthe chances behind the title",
                f"All {len(shots)} Spain shots in 7 matches. Bigger circle = better chance (xG).\n"
                f"The chances were worth {xg:.1f} goals. Spain scored {goals} (plus 1 own goal).",
                "StatsBomb open data, UEFA Euro 2024")
    pitch = VerticalPitch(pitch_type="statsbomb", half=True, pitch_color=PITCH, line_color=LINES,
                          linewidth=1.2)
    ax = fig.add_axes([0.04, 0.08, 0.92, 0.7])
    pitch.draw(ax=ax)
    miss = [s for s in shots if not s[3]]
    hit = [s for s in shots if s[3]]
    pitch.scatter([s[0] for s in miss], [s[1] for s in miss], s=[s[2] * 900 + 25 for s in miss],
                  ax=ax, facecolor="none", edgecolor=MUTED, linewidth=1.1, alpha=0.9, zorder=2)
    pitch.scatter([s[0] for s in hit], [s[1] for s in hit], s=[s[2] * 900 + 25 for s in hit],
                  ax=ax, facecolor=ACCENT, edgecolor=BG, linewidth=1.5, zorder=3)
    ax.scatter([], [], s=90, facecolor=ACCENT, edgecolor=BG, label=f"Goal ({goals})")
    ax.scatter([], [], s=90, facecolor="none", edgecolor=MUTED, label=f"No goal ({len(miss)})")
    leg = ax.legend(loc="lower left", frameon=False, fontsize=10.5, labelcolor=INK2,
                    bbox_to_anchor=(0.03, 0.03))
    save(fig, "03_spain_shot_map.png")


# ---------------------------------------------------------------- 4. Home advantage
def home_advantage():
    seasons = json.load(open(D / "epl_seasons.json"))
    x = list(range(len(seasons)))
    hw = [s["home_win"] for s in seasons]
    aw = [s["away_win"] for s in seasons]
    covid = next(i for i, s in enumerate(seasons) if s["season"] == "2020-21")
    fig = frame("Without fans, home advantage\nin the Premier League vanished",
                f"Share of matches won by the home team and by the away team.\n"
                f"In 2020-21, played almost entirely in empty stadiums, away teams\n"
                f"won more often than home teams: {aw[covid]:.0f}% vs {hw[covid]:.0f}%.",
                "openfootball results, Premier League 2010-11 to 2024-25")
    ax = fig.add_axes([0.1, 0.12, 0.74, 0.6])
    clean(ax, "y")
    ax.axvspan(covid - 0.5, covid + 0.5, color=GRID, zorder=0)
    ax.text(covid, 52.3, "no fans", ha="center", fontsize=9.5, color=INK2)
    ax.plot(x, hw, color=ACCENT, linewidth=2.4)
    ax.plot(x, aw, color=HOT, linewidth=2.4)
    for xs, ys, c in ((x, hw, ACCENT), (x, aw, HOT)):
        ax.scatter([xs[-1]], [ys[-1]], color=c, s=28, zorder=3)
        ax.scatter([covid], [ys[covid]], color=c, s=40, zorder=3, edgecolor=BG, linewidth=1.5)
    ax.text(x[-1] + 0.35, hw[-1], f"Home wins\n{hw[-1]:.0f}%", va="center", fontsize=10.5, color=ACCENT,
            fontweight="bold")
    ax.text(x[-1] + 0.35, aw[-1], f"Away wins\n{aw[-1]:.0f}%", va="center", fontsize=10.5, color=HOT,
            fontweight="bold")
    ax.set_xticks(x[::2], [s["season"] for s in seasons][::2], rotation=0, fontsize=9.5)
    ax.set_ylim(15, 55)
    ax.set_yticks([20, 30, 40, 50], ["20%", "30%", "40%", "50%"])
    ax.set_xlim(-0.6, len(x) - 0.4)
    save(fig, "04_home_advantage.png")


# ---------------------------------------------------------------- 5. Goals per game
def goals_per_game():
    seasons = json.load(open(D / "epl_seasons.json"))
    vals = [s["goals_per_game"] for s in seasons]
    top = max(range(len(vals)), key=vals.__getitem__)
    low = min(range(len(vals)), key=vals.__getitem__)
    fig = frame(f"{seasons[top]['season']} broke the\nPremier League goal curve",
                f"Average goals per match. For a decade the league sat between\n"
                f"{vals[low]:.2f} and 2.85. Then {seasons[top]['season']} jumped to {vals[top]:.2f}, "
                f"{seasons[top]['goals']:,} goals in total.\nThe next season fell back, but stayed above the old normal.",
                "openfootball results, Premier League 2010-11 to 2024-25")
    ax = fig.add_axes([0.1, 0.12, 0.84, 0.6])
    clean(ax, "y")
    colors = [ACCENT if i == top else CONTEXT for i in range(len(vals))]
    bars = ax.bar(range(len(vals)), vals, color=colors, width=0.66)
    for i in (top, low, len(vals) - 1):
        b = bars[i]
        ax.text(b.get_x() + b.get_width() / 2, vals[i] + 0.03, f"{vals[i]:.2f}", ha="center",
                fontsize=10, color=INK, fontweight="bold" if i == top else "normal")
    ax.set_xticks(range(0, len(vals), 2), [s["season"] for s in seasons][::2], fontsize=9.5)
    ax.set_ylim(0, 3.6)
    ax.set_yticks([0, 1, 2, 3])
    ax.set_ylabel("Goals per match", fontsize=10.5)
    save(fig, "05_goals_per_game.png")


# ---------------------------------------------------------------- 6. Spain pass network, Euro final
def spain_pass_network():
    eu = json.load(open(D / "sb/euro24.json"))
    final = next(m for m in eu if m["competition_stage"]["name"] == "Final")
    ev = json.load(open(D / f"sb/events/{final['match_id']}.json"))
    subs = [e for e in ev if e["type"]["name"] == "Substitution" and e["team"]["name"] == "Spain"]
    first_sub = min((e["minute"] * 60 + e["second"], e["period"]) for e in subs) if subs else (10 ** 6, 9)
    cutoff_period, cutoff_sec = first_sub[1], first_sub[0]

    def before_sub(e):
        return (e["period"], e["minute"] * 60 + e["second"]) < (cutoff_period, cutoff_sec)

    lineup = next(e for e in ev if e["type"]["name"] == "Starting XI" and e["team"]["name"] == "Spain")
    shirt = {p["player"]["name"]: p["jersey_number"] for p in lineup["tactics"]["lineup"]}
    short = {p["player"]["name"]: p["player"]["name"].split()[-1] for p in lineup["tactics"]["lineup"]}
    known = {"Lamine Yamal Nasraoui Ebana": "Yamal", "Rodrigo Hernández Cascante": "Rodri",
             "Daniel Olmo Carvajal": "Olmo", "Fabián Ruiz Peña": "Fabián", "Nicholas Williams Arthuer": "N. Williams",
             "Álvaro Borja Morata Martín": "Morata", "Unai Simón Mendibil": "Simón", "Daniel Carvajal Ramos": "Carvajal",
             "Aymeric Laporte": "Laporte", "Robin Aime Robert Le Normand": "Le Normand",
             "Marc Cucurella Saseta": "Cucurella", "Pedro González López": "Pedri"}
    for k, v in known.items():
        if k in short:
            short[k] = v

    passes = [e for e in ev if e["type"]["name"] == "Pass" and e["team"]["name"] == "Spain" and before_sub(e)
              and "outcome" not in e["pass"] and "recipient" in e["pass"]]
    loc = defaultdict(list)
    for p in passes:
        loc[p["player"]["name"]].append(p["location"])
        loc[p["pass"]["recipient"]["name"]].append(p["pass"]["end_location"])
    avg = {k: (sum(x for x, _ in v) / len(v), sum(y for _, y in v) / len(v), len(v)) for k, v in loc.items()
           if k in shirt}
    pairs = Counter()
    for p in passes:
        a, b = p["player"]["name"], p["pass"]["recipient"]["name"]
        pairs[tuple(sorted((a, b)))] += 1
    top_pair = pairs.most_common(1)[0]
    first_off = next(e for e in subs if (e["minute"] * 60 + e["second"], e["period"]) == first_sub)
    off_name = first_off["player"]["name"]

    fig = frame("How Spain moved the ball\nin the Euro 2024 final",
                f"Spain's first half vs England, before {short[off_name]} went off at half-time.\n"
                f"Circles are average positions; thicker lines = more passes between\n"
                f"two players. Busiest link: {short[top_pair[0][0]]} – {short[top_pair[0][1]]} ({top_pair[1]} passes).",
                "StatsBomb open data, Euro 2024 final, Spain 2-1 England")
    pitch = Pitch(pitch_type="statsbomb", pitch_color=PITCH, line_color=LINES, linewidth=1.2)
    ax = fig.add_axes([0.04, 0.1, 0.92, 0.66])
    pitch.draw(ax=ax)
    mx = max(pairs.values())
    for (a, b), n in pairs.items():
        if n < 4 or a not in avg or b not in avg:
            continue
        pitch.lines(avg[a][0], avg[a][1], avg[b][0], avg[b][1], lw=1 + 7 * n / mx, color=ACCENT,
                    alpha=0.25 + 0.55 * n / mx, ax=ax, zorder=1)
    placed = []
    for k, (x, y, n) in sorted(avg.items(), key=lambda kv: -kv[1][2]):
        pitch.scatter(x, y, s=260 + n * 6, color=BG, edgecolors=ACCENT, linewidth=2, ax=ax, zorder=2)
        pitch.annotate(str(shirt[k]), (x, y), ax=ax, ha="center", va="center", fontsize=9.5, color=INK,
                       fontweight="bold", zorder=3)
        # name below the circle; above it if another player's circle sits right underneath
        crowded = any(abs(px - x) < 8 and 0 < py - y < 9 for px, py in placed)
        dy = -5.2 if crowded else 5.2
        pitch.annotate(short[k], (x, y + dy), ax=ax, ha="center", va="center", fontsize=8.5, color=INK2,
                       zorder=4, bbox=dict(boxstyle="round,pad=0.15", fc=PITCH, ec="none", alpha=0.85))
        placed.append((x, y))
    ax.annotate("", xy=(0.62, -0.035), xytext=(0.38, -0.035), xycoords="axes fraction",
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.2))
    ax.text(0.5, -0.07, "Attacking direction", transform=ax.transAxes, ha="center", fontsize=9.5, color=MUTED)
    save(fig, "06_spain_pass_network.png")
    return dict(first_off=off_name, passes=len(passes), top_pair=[short[top_pair[0][0]], short[top_pair[0][1]], top_pair[1]])


if __name__ == "__main__":
    arsenal_start()
    leverkusen()
    spain_shots()
    home_advantage()
    goals_per_game()
    print(spain_pass_network())
