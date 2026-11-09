"""Check the HelloFresh dataset for internal consistency.

Reported AEBITDA margins must match AEBITDA / revenue, and the North America and
International segments must add up to group orders and revenue.
Usage:  python scripts/check_data.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    d = json.loads((ROOT / "data" / "hellofresh_data.json").read_text(encoding="utf-8"))
    g, problems = d["group"], 0
    for i, year in enumerate(d["years"]):
        calc = round(g["aebitda"][i] / g["revenue"][i] * 100, 1)
        if abs(calc - g["aebitda_margin"][i]) > 0.1:
            print(f"{year}: margin {calc}% vs reported {g['aebitda_margin'][i]}%")
            problems += 1
        print(f"{year}: revenue per order EUR {g['revenue'][i] / g['orders'][i]:.2f}")
    s = d["segments"]
    for i, year in enumerate(s["years"]):
        gi = d["years"].index(year)
        orders = s["North America"]["orders"][i] + s["International"]["orders"][i]
        revenue = s["North America"]["revenue"][i] + s["International"]["revenue"][i]
        if abs(orders - g["orders"][gi]) > 0.05 or abs(revenue - g["revenue"][gi]) > 1:
            print(f"{year}: segments {orders:.2f}m / EUR {revenue:,.1f}m vs group {g['orders'][gi]}m / EUR {g['revenue'][gi]:,.1f}m")
            problems += 1
    print("All checks passed" if problems == 0 else f"{problems} problem(s) found")
    return problems


if __name__ == "__main__":
    raise SystemExit(main())
