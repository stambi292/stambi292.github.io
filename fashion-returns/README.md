# Half of it comes back: fashion returns

**Live page:** https://stambi292.github.io/fashion-returns/

Online fashion retailers like Zalando say about half of the items customers order are returned. I analysed 2.3 million order lines from a German online fashion retailer to find what drives returns, built a model that predicts them at checkout, and priced what cutting them is worth.

## Findings
- **52.7%** of items were returned, **€46.8m of €82.3m** in sales.
- Items ordered in **two sizes** (bracketing) come back **75.9%** of the time vs 49.0% for one size.
- Baskets of 6+ items: 62.8% returned; single-item orders: 36.1%.
- Items over €80: 63.4% returned; under €15: 40.1%.
- **10% of customers make 53.5% of returns**; 31.3% never return anything.
- A gradient boosting model (ROC-AUC 0.73, tested on six later months) separates the riskiest 10% of items (81.8% returned) from the safest 10% (15.3%).

## Recommendations
1. Size advice when a second size of the same item goes into the basket.
2. Show extra fit information only for high-risk items.
3. Target extreme, persistent returners rather than everyone.
4. Keep invoice payment, use it as a model signal.

## How to run
```
pip install pandas scikit-learn
python scripts/analyse.py data/orders_train.txt   # writes data/results.json
python scripts/build_page.py                     # writes index.html
```

## Data
Data Mining Cup 2016 (prudsys AG): order data of an unnamed German online fashion retailer, Jan 2014 to Sep 2015. Not included here. Zalando figures from its corporate website; return cost range from the University of Bamberg Research Group Returns Management (2022).

Independent analysis by Stephen tAMBI. Not affiliated with Zalando or any retailer.
