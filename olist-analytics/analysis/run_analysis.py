"""
Runs every query in analysis/queries against the dbt-built DuckDB database,
saves the results as CSVs, draws the README charts, and builds the dashboard.

Usage (from the project root, after `dbt build`):
    python analysis/run_analysis.py
"""
import json
from pathlib import Path

import duckdb
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.colors import LinearSegmentedColormap

ROOT = Path(__file__).resolve().parents[1]
QUERIES = ROOT / "analysis" / "queries"
OUTPUT = ROOT / "analysis" / "output"
IMAGES = ROOT / "docs" / "images"
DASHBOARD = ROOT / "dashboard"

# Palette (light mode)
BLUE, RED = "#0a4ee4", "#d97a00"
INK, INK2, MUTED, GRID, AXIS = "#001647", "#4d5c7e", "#8590a8", "#dfe5f3", "#c2cbe0"
SURFACE = "#ffffff"
BLUE_RAMP = ["#eef2fc", "#cfdcfb", "#9fb9f6", "#6b93ef", "#3a6fe9", "#0a4ee4", "#0a1f9c", "#001647"]


def run_queries(con):
    results = {}
    for path in sorted(QUERIES.glob("*.sql")):
        df = con.sql(path.read_text()).df()
        df.to_csv(OUTPUT / f"{path.stem}.csv", index=False)
        results[path.stem] = df
        print(f"  {path.stem}: {len(df)} rows")
    return results


def style(ax, title, subtitle=None):
    ax.set_facecolor(SURFACE)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(AXIS)
    ax.tick_params(colors=MUTED, labelsize=9, length=0)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_title(title, loc="left", fontsize=13, color=INK, fontweight="bold", pad=24)
    if subtitle:
        ax.text(0, 1.03, subtitle, transform=ax.transAxes, fontsize=9.5, color=INK2)


def save(fig, name):
    fig.patch.set_facecolor(SURFACE)
    fig.tight_layout()
    fig.savefig(IMAGES / name, dpi=160, facecolor=SURFACE)
    plt.close(fig)


def chart_revenue(df):
    fig, ax = plt.subplots(figsize=(9, 4.2))
    x = df["order_month"]
    y = df["revenue_brl"] / 1e6
    ax.plot(x, y, color=BLUE, linewidth=2)
    ax.scatter(x, y, color=BLUE, s=18, zorder=3, edgecolor=SURFACE, linewidth=1.5)
    peak = df["revenue_brl"].idxmax()
    ax.annotate("Black Friday peak (Nov 2017)", (x[peak], y[peak]), xytext=(10, 6),
                textcoords="offset points", fontsize=9, color=INK2)
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"R${v:.1f}M"))
    ax.set_ylim(0, 1.35)
    style(ax, "Monthly revenue", "Revenue grew fast through 2017, then flattened at ~R$1.1M/month in 2018")
    save(fig, "revenue_trend.png")


def chart_delivery(df):
    fig, ax = plt.subplots(figsize=(9, 4.2))
    labels = [b.split(". ", 1)[1] for b in df["delivery_bucket"]]
    colors = [RED if "late" in l else BLUE for l in labels]
    bars = ax.bar(labels, df["pct_bad_reviews"], color=colors, width=0.62)
    for b, v in zip(bars, df["pct_bad_reviews"]):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.5, f"{v:.0f}%", ha="center", fontsize=9, color=INK)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax.set_ylim(0, 90)
    style(ax, "Share of 1–2 star reviews, by delivery timing",
          "Blue = arrived on/before the promised date · Red = arrived late")
    save(fig, "delivery_vs_reviews.png")


def chart_cohorts(df):
    pivot = df.pivot(index="cohort_month", columns="months_since_first", values="retention_pct")
    pivot = pivot.reindex(columns=range(1, 13))
    # A missing cell means 0% if that month had already happened (data ends Aug 2018), else unknown.
    last = pd.Timestamp("2018-08-01")
    for cohort in pivot.index:
        for m in pivot.columns:
            observable = cohort + pd.DateOffset(months=m) <= last
            if observable and pd.isna(pivot.at[cohort, m]):
                pivot.at[cohort, m] = 0.0
    pivot.index = [d.strftime("%b %Y") for d in pivot.index]
    fig, ax = plt.subplots(figsize=(9, 6))
    cmap = LinearSegmentedColormap.from_list("blue", BLUE_RAMP)
    im = ax.imshow(pivot.values, cmap=cmap, vmin=0, vmax=0.5, aspect="auto")
    ax.set_xticks(range(len(pivot.columns)), [f"M{c}" for c in pivot.columns])
    ax.set_yticks(range(len(pivot.index)), pivot.index)
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            v = pivot.values[i, j]
            if v == v:  # not NaN
                ax.text(j, i, f"{v:.1f}", ha="center", va="center", fontsize=7,
                        color="white" if v > 0.3 else INK2)
    style(ax, "Monthly cohort retention (%)",
          "Share of each month's new customers who ordered again N months later")
    ax.grid(False)
    ax.spines["bottom"].set_visible(False)
    cb = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cb.outline.set_visible(False)
    cb.ax.tick_params(colors=MUTED, labelsize=8, length=0)
    save(fig, "cohort_retention.png")


def chart_regions(df):
    df = df.sort_values("late_pct")
    fig, ax = plt.subplots(figsize=(9, 3.8))
    bars = ax.barh(df["region"], df["late_pct"], color=BLUE, height=0.6)
    for b, v, d in zip(bars, df["late_pct"], df["avg_delivery_days"]):
        ax.text(v + 0.25, b.get_y() + b.get_height() / 2, f"{v:.1f}%  ·  {d:.0f} days avg",
                va="center", fontsize=9, color=INK2)
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax.set_xlim(0, 17)
    style(ax, "Late deliveries by customer region",
          "Northeast customers wait more than twice as long as São Paulo and are 3x as likely to get a late order")
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    save(fig, "region_late_deliveries.png")


def to_records(df):
    out = df.copy()
    for col in out.columns:
        if str(out[col].dtype).startswith("datetime"):
            out[col] = out[col].dt.strftime("%Y-%m")
    return json.loads(out.to_json(orient="records"))


def build_dashboard(results):
    data = {name: to_records(df) for name, df in results.items() if name != "10_dashboard_cube"}
    cube = results["10_dashboard_cube"].astype(object).where(results["10_dashboard_cube"].notna(), None)
    data["cube"] = {"columns": list(cube.columns), "rows": cube.values.tolist()}
    template = (DASHBOARD / "template.html").read_text()
    html = template.replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":")))
    (DASHBOARD / "index.html").write_text(html)
    print("  dashboard/index.html written")


def main():
    for d in (OUTPUT, IMAGES):
        d.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(ROOT / "olist.duckdb"), read_only=True)
    print("Running queries...")
    results = run_queries(con)
    print("Drawing charts...")
    chart_revenue(results["02_monthly_revenue"])
    chart_delivery(results["05_delivery_vs_reviews"])
    chart_cohorts(results["03_cohort_retention"])
    chart_regions(results["06_region_delivery"])
    if (DASHBOARD / "template.html").exists():
        print("Building dashboard...")
        build_dashboard(results)
    print("Done.")


if __name__ == "__main__":
    main()
