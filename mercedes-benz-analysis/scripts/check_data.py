"""Check the Mercedes-Benz dataset for internal consistency.

Reported adjusted return on sales must match adjusted EBIT / revenue (to 0.1 point),
and the 2025 regional unit sales must add up to the reported total of about 1.8 million.
Usage:  python scripts/check_data.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    d = json.loads((ROOT / "data" / "mercedes_data.json").read_text(encoding="utf-8"))
    problems = 0
    cars = d["cars"]
    for i, year in enumerate(d["years"]):
        calc = round(cars["adj_ebit"][i] / cars["revenue"][i] * 100, 1)
        if abs(calc - cars["adj_ros"][i]) > 0.1:
            print(f"{year}: return on sales {calc}% vs reported {cars['adj_ros'][i]}%")
            problems += 1
        print(f"{year}: revenue per car EUR {cars['revenue'][i] * 1e6 / cars['units'][i]:,.0f}, "
              f"profit per car EUR {cars['adj_ebit'][i] * 1e6 / cars['units'][i]:,.0f}")
    regions = sum(r[1] for r in d["regions_2025"]["rows"] if not r[0].startswith("of which"))
    if abs(regions - 1_800_800) > 500:
        print(f"2025 regions add up to {regions:,}, reported total about 1,800,800")
        problems += 1
    print("All checks passed" if problems == 0 else f"{problems} problem(s) found")
    return problems


if __name__ == "__main__":
    raise SystemExit(main())
