# One process, 11,963 paths: purchase-to-pay process mining

**Live page:** https://stambi292.github.io/process-mining/

On paper, buying works in five steps: order, receive, get the invoice, record it, pay. I mined 1.6 million real events from a multinational's purchasing system to see what actually happens, where invoices get stuck, and what fixing it is worth.

## Findings (251,352 purchase order items created in 2018)
- **11,963 different paths.** The most common covers only 20% of items; 45 paths cover 80%.
- **77.6 days** median from order to payment; 38.5% of paid items take over 90 days.
- The longest wait: **42 days** between recording an invoice and paying it.
- **22.2%** of items hit a payment block and take 87 days to pay, against 71 for clean items.
- **18%** of items are changed, cancelled or deleted after ordering (93.9 days to pay).
- **3,601** items got their purchase order only after the vendor had invoiced.
- **65%** of all steps are done by hand: 4.1 manual steps per item.

## Recommendations
1. Find out why invoices get blocked, by vendor and reason.
2. Fix orders before they are sent (catalogue prices, approvals).
3. Flag purchase orders created after the invoice.
4. Automate invoice matching for clean three-way matches.

## How to run
```
pip install pandas lxml pyarrow
python scripts/xes_to_parquet.py data/BPI_Challenge_2019.xes.gz data/events.parquet
python scripts/analyse.py data/events.parquet   # writes data/results.json
python scripts/build_page.py                    # writes index.html
```

## Data
BPI Challenge 2019, van Dongen, B.F., 4TU.ResearchData: the purchase-to-pay event log of a large multinational in coatings and paints operating from the Netherlands, anonymised. Not included here.

Independent analysis by Stephen tAMBI. Not affiliated with the company or any software vendor.
