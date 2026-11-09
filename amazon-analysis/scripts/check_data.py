"""Check the hand-collected Amazon dataset against Amazon's reported totals.

Every breakdown (segments, revenue streams, countries) must add up to the consolidated
net sales Amazon reported for that year, and segment operating income must add up to
consolidated operating income. Usage:  python scripts/check_data.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Consolidated figures as reported in the 10-K / Q4 releases (USD millions)
REPORTED_SALES = {2018: 232887, 2019: 280522, 2020: 386064, 2021: 469822,
                  2022: 513983, 2023: 574785, 2024: 637959, 2025: 716924}
REPORTED_OPINC = {2018: 12421, 2019: 14541, 2020: 22899, 2021: 24879,
                  2022: 12248, 2023: 36852, 2024: 68593, 2025: 79975}


def main():
    d = json.loads((ROOT / "data" / "amazon_data.json").read_text(encoding="utf-8"))
    problems = 0
    seg = d["segments"]
    for i, year in enumerate(seg["years"]):
        sales = sum(v[i] for v in seg["sales"].values())
        opinc = sum(v[i] for v in seg["opinc"].values())
        if sales != REPORTED_SALES[year] or opinc != REPORTED_OPINC[year]:
            print(f"{year}: segments {sales:,}/{opinc:,} vs reported {REPORTED_SALES[year]:,}/{REPORTED_OPINC[year]:,}")
            problems += 1
    for block in ("streams", "countries"):
        b = d[block]
        for i, year in enumerate(b["years"]):
            total = sum(v[i] for k, v in b.items() if k != "years")
            if total != REPORTED_SALES[year]:
                print(f"{block} {year}: {total:,} vs reported {REPORTED_SALES[year]:,}")
                problems += 1
    print("All checks passed" if problems == 0 else f"{problems} problem(s) found")
    return problems


if __name__ == "__main__":
    raise SystemExit(main())
