# Build the Olist dashboard in Power BI

You will rebuild the Olist analysis as a Power BI report: one page with KPI cards, a revenue trend,
delivery vs. reviews, categories and regions, plus filters. Expect 1–2 hours the first time.

**What's in this folder**

| File | What it is |
|---|---|
| `data/fact_orders.csv` | One row per order (97,910 orders, Jan 2017 – Aug 2018) |
| `data/dim_customers.csv` | One row per customer (94,707) |
| `data/dim_date.csv` | One row per day, 2017–2018 (calendar table) |
| `measures.dax` | All DAX measures, ready to paste |
| `olist_theme.json` | Power BI theme in Olist's colours |

**Check numbers.** When you're done, your report should show the same totals as the web dashboard:
revenue **R$15.69M**, **97,910** orders, average review **4.12**, late deliveries **6.8%**.
If yours differ, something went wrong in steps 2–4.

---

## 1. Install Power BI Desktop

Install it free from the Microsoft Store (search "Power BI Desktop"). Open it and close the start screen.

## 2. Important for German Windows: set the number format

The CSV files use a dot for decimals (`18.62`). German Windows settings expect a comma, which would turn
`18.62` into `1862`. Fix this once before importing:

**File → Options and settings → Options → Current file → Regional settings →
Locale for import → English (United States)** → OK.

## 3. Import the three tables

1. **Home → Get data → Text/CSV** → choose `fact_orders.csv` → **Load**.
2. Repeat for `dim_customers.csv` and `dim_date.csv`.
3. Open **Table view** (left sidebar, table icon) and check that `revenue` shows values like `18.62`
   and `order_date` shows dates. If not, go back to step 2.

## 4. Build the data model

1. Open **Model view** (left sidebar, the third icon).
2. Drag `dim_date[date]` onto `fact_orders[order_date]`. Power BI creates a one-to-many relationship.
3. Drag `dim_customers[customer_unique_id]` onto `fact_orders[customer_unique_id]`.
4. Right-click the `dim_date` table → **Mark as date table** → choose the `date` column.
5. In `dim_date`, select `month_name` → **Column tools → Sort by column → month_number**,
   so months sort Jan–Dec instead of alphabetically.

This is the same star schema as in the dbt project: facts in the middle, dimensions around it.

## 5. Add the measures

1. Select the `fact_orders` table in the **Data** pane.
2. **Home → New measure**, paste one measure from `measures.dax` (one line like
   `Total Revenue = SUM ( fact_orders[revenue] )`), press Enter.
3. Repeat for every measure.
4. Format them: select a measure, then in **Measure tools**:
   - Total Revenue, Avg Order Value: currency, 0 decimals
   - Late Delivery %, Bad Review %, Freight Share %, Revenue MoM %, Repeat Customer %: percentage, 1 decimal
   - Avg Review, Avg Delivery Days: 2 and 1 decimals

## 6. Apply the Olist theme

**View → Themes → Browse for themes** → choose `olist_theme.json`.

## 7. Build the page

Suggested layout (16:9 page):

```
┌───────────────────────────────────────────────────────────────┐
│ Title: Olist Marketplace Analytics                            │
│ [Slicer: customer_region] [Slicer: main_category] [Slicer: date]│
├──────────┬──────────┬──────────┬──────────┬──────────┬────────┤
│ Revenue  │ Orders   │ Avg order│ Avg      │ Late     │ Avg    │
│          │          │ value    │ review   │ delivery │ days   │
├──────────┴──────────┴──────────┼──────────┴──────────┴────────┤
│ Line chart: revenue by month   │ Bar chart: top 10 categories │
├────────────────────────────────┼──────────────────────────────┤
│ Column chart: bad review % by  │ Table: regions               │
│ days late                      │                              │
└────────────────────────────────┴──────────────────────────────┘
```

**KPI cards.** Insert a **Card** visual for each of: Total Revenue, Orders, Avg Order Value, Avg Review,
Late Delivery %, Avg Delivery Days.

**Revenue trend.** **Line chart**: X-axis `dim_date[year_month]`, Y-axis `Total Revenue`.
Add `Orders` to the tooltips.

**Top categories.** **Clustered bar chart**: Y-axis `fact_orders[main_category]`, X-axis `Total Revenue`.
In the Filters pane, set main_category to **Top N → 10 by Total Revenue**.

**Delivery vs. reviews.** This needs one extra column. Select `fact_orders` → **Table tools → New column**:

```
Delivery Timing =
SWITCH (
    TRUE (),
    ISBLANK ( fact_orders[days_late] ), "Not delivered",
    fact_orders[days_late] <= -10, "1. 10+ days early",
    fact_orders[days_late] <= -1, "2. 1-9 days early",
    fact_orders[days_late] = 0, "3. On the day",
    fact_orders[days_late] <= 3, "4. 1-3 days late",
    fact_orders[days_late] <= 7, "5. 4-7 days late",
    "6. 8+ days late"
)
```

Then a **Clustered column chart**: X-axis `Delivery Timing`, Y-axis `Bad Review %`.
Filter out "Not delivered". You should see about 9–12% for on-time orders and about 79% for 8+ days late.

**Regions.** **Table** visual with `customer_region`, `Orders`, `Total Revenue`, `Avg Delivery Days`,
`Late Delivery %`, `Avg Review`. Add **conditional formatting** to Late Delivery %
(Format → Cell elements → Background color) so the worst regions stand out.

**Filters.** Add three **Slicer** visuals: `customer_region`, `main_category` and `dim_date[date]`
(as a "Between" date range).

## 8. Check, save and share

1. Compare your cards with the check numbers at the top.
2. Click a region in the table: every visual should filter to that region.
3. Save as `olist_dashboard.pbix`.
4. Take a screenshot of the page for your GitHub README and your Lemon.io project images.

**Note:** `Repeat Customer %` reacts to filters on the `dim_customers` table, not to the region or category
slicers, because filters flow from dimension tables to the fact table, not back. That's normal
star-schema behaviour, and a good thing to be able to explain in an interview.

## Next steps once it works

- Add a second page for customers: repeat rate and lifetime revenue by state.
- Add a **What-if parameter** (Modeling → New parameter) for "extra repeat customers %" and calculate the
  revenue it would add, like the calculator idea in the web dashboard.
- Publish to Power BI Service if you have a work or university account.
