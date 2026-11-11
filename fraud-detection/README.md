# Catching card fraud, priced in euros

**Live page:** https://stambi292.github.io/fraud-detection/

A card issuer wants to stop fraud without blocking honest customers. I trained machine learning models on 284,807 real card transactions (only 0.17% fraud) and turned the model's scores into the decision a bank actually makes: which payments to stop or review, and what that is worth in euros.

## Results (test period: last 30% of the time window, 108 frauds worth €14,567)

| Model | PR-AUC | ROC-AUC |
|---|---|---|
| Logistic regression | 0.768 | 0.980 |
| Gradient boosting | 0.782 | 0.959 |
| **Random forest (used)** | **0.820** | 0.968 |

At a €5 review cost per alert, the best threshold is 0.18: it stops **€12,028 of €14,567 in fraud (83%)**, flags 96 payments of which 84 are fraud, and saves €11,548 after review costs.

## Recommendations
1. Two tiers: decline automatically above a score of 0.50, review 0.18 to 0.50.
2. Set the threshold from the review cost, not from accuracy.
3. Add simple rules for the frauds the model misses.
4. Retrain on recent data and monitor the share of alerts that are fraud.

## How to run
```
pip install pandas scikit-learn
python scripts/train_model.py data/creditcard.csv   # writes data/results.json
python scripts/build_page.py                       # writes index.html
```
The notebook in `notebooks/` walks through the same steps with outputs.

## Data
Credit Card Fraud Detection dataset, Machine Learning Group, Université Libre de Bruxelles (Dal Pozzolo et al.), available on Kaggle. The file is not included here; download `creditcard.csv` into `data/`.

Independent analysis by Stephen tAMBI. Not affiliated with any bank or payment company.
