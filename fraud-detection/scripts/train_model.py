"""Card fraud detection: train models on a time-based split and price every decision threshold.

Data: the public ULB credit card fraud dataset (284,807 transactions over two days, 492 frauds).
Download creditcard.csv yourself and pass its path, for example:
    python scripts/train_model.py data/creditcard.csv
"""
import json, sys, pathlib
import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import average_precision_score, roc_auc_score

csv = pathlib.Path(sys.argv[1])
out = pathlib.Path(__file__).resolve().parents[1] / 'data' / 'results.json'
df = pd.read_csv(csv)
features = [c for c in df.columns if c not in ('Class',)]

# Time-based split: train on the first 70% of the time window, test on the last 30%.
cut = df['Time'].quantile(0.70)
train, test = df[df['Time'] <= cut], df[df['Time'] > cut]
Xtr, ytr, Xte, yte = train[features], train['Class'], test[features], test['Class']

models = {
    'Logistic regression': make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, class_weight='balanced')),
    'Gradient boosting': HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=31, class_weight='balanced', random_state=42),
    'Random forest': RandomForestClassifier(n_estimators=300, min_samples_leaf=2, class_weight='balanced_subsample', n_jobs=-1, random_state=42),
}
scores, summary = {}, {}
for name, m in models.items():
    m.fit(Xtr, ytr)
    p = m.predict_proba(Xte)[:, 1]
    scores[name] = p
    summary[name] = {'pr_auc': round(average_precision_score(yte, p), 3), 'roc_auc': round(roc_auc_score(yte, p), 3)}
print(summary)

best = max(summary, key=lambda k: summary[k]['pr_auc'])
p = scores[best]
amt = test['Amount'].to_numpy(); y = yte.to_numpy()
hours = (test['Time'].max() - test['Time'].min()) / 3600

# Price every threshold: flag transactions with score >= t.
thresholds = np.round(np.linspace(0, 1, 101), 2)
curve = []
for t in thresholds:
    f = p >= t
    tp, fp = int((f & (y == 1)).sum()), int((f & (y == 0)).sum())
    curve.append({'t': round(float(t), 3), 'flagged': int(f.sum()), 'caught': tp, 'falseAlarms': fp,
                  'missed': int(((~f) & (y == 1)).sum()), 'caughtEur': round(float(amt[f & (y == 1)].sum()), 2),
                  'missedEur': round(float(amt[(~f) & (y == 1)].sum()), 2)})

# Size of frauds, for context
fr = test[test['Class'] == 1]['Amount']
res = {
    'dataset': {'transactions': int(len(df)), 'frauds': int(df['Class'].sum()), 'fraudRate': round(df['Class'].mean() * 100, 3),
                'fraudEur': round(float(df.loc[df['Class'] == 1, 'Amount'].sum()), 2), 'hours': round(df['Time'].max() / 3600, 1)},
    'test': {'transactions': int(len(test)), 'frauds': int(y.sum()), 'fraudEur': round(float(amt[y == 1].sum()), 2), 'hours': round(hours, 1),
             'medianFraud': round(float(fr.median()), 2), 'maxFraud': round(float(fr.max()), 2)},
    'models': summary, 'best': best, 'curve': curve,
}
# Recommended setting: the threshold with the highest net saving at a EUR 5 review cost.
res['recommended'] = max(curve, key=lambda c: c['caughtEur'] - 5 * c['flagged'])
out.write_text(json.dumps(res, indent=1))
print('best', best, 'test frauds', int(y.sum()), 'fraud EUR', res['test']['fraudEur'], 'hours', round(hours, 1))
for c in curve:
    if c['t'] in (0.1, 0.3, 0.5, 0.7, 0.9):
        print(c)
