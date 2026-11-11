"""Predictive maintenance on NASA C-MAPSS FD001: predict remaining useful life (RUL) and price maintenance policies.

    python scripts/train_model.py data
Writes data/results.json.
"""
import json, sys, pathlib
import numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GroupKFold

d = pathlib.Path(sys.argv[1]); out = pathlib.Path(__file__).resolve().parents[1] / 'data' / 'results.json'
cols = ['unit', 'cycle', 'os1', 'os2', 'os3'] + [f's{i}' for i in range(1, 22)]
read = lambda f: pd.read_csv(d / f, sep=r'\s+', header=None, names=cols)
tr, te = read('train_FD001.txt'), read('test_FD001.txt')
rul_te = pd.read_csv(d / 'RUL_FD001.txt', header=None, names=['rul']).rul.to_numpy()
CAP = 125
tr['life'] = tr.groupby('unit').cycle.transform('max'); tr['rul'] = tr.life - tr.cycle
SENS = [c for c in cols[5:] if tr[c].std() > 1e-6 and c not in ('s1', 's5', 's10', 's16', 's18', 's19')]

def features(df):
    df = df.sort_values(['unit', 'cycle']).copy()
    g = df.groupby('unit')
    f = df[['unit', 'cycle']].copy()
    for s in SENS:
        f[s] = df[s]
        f[s + '_m10'] = g[s].transform(lambda x: x.rolling(10, min_periods=1).mean())
        f[s + '_sl20'] = g[s].transform(lambda x: x.rolling(20, min_periods=3).apply(lambda v: np.polyfit(np.arange(len(v)), v, 1)[0], raw=True)).fillna(0)
    return f
Ftr, Fte = features(tr), features(te)
X = [c for c in Ftr.columns if c != 'unit']
y = tr.sort_values(['unit', 'cycle']).rul.clip(upper=CAP).to_numpy()
last = Fte.groupby('unit').tail(1)

models = {
    'Linear regression': make_pipeline(StandardScaler(), Ridge(alpha=1.0)),
    'Random forest': RandomForestRegressor(n_estimators=300, min_samples_leaf=5, n_jobs=-1, random_state=42),
    'Gradient boosting': HistGradientBoostingRegressor(max_iter=400, learning_rate=0.05, max_leaf_nodes=31, random_state=42),
}
rmse = lambda a, b: float(np.sqrt(np.mean((a - b) ** 2)))
scores = {'Average engine (no model)': {'rmse': round(rmse(np.full(100, np.mean(np.minimum(rul_te, CAP))), np.minimum(rul_te, CAP)), 1)}}
preds = {}
for n, m in models.items():
    m.fit(Ftr[X], y); p = np.clip(m.predict(last[X]), 0, None); preds[n] = p
    scores[n] = {'rmse': round(rmse(p, np.minimum(rul_te, CAP)), 1), 'mae': round(float(np.mean(np.abs(p - np.minimum(rul_te, CAP)))), 1)}
best = min(models, key=lambda n: scores[n]['rmse'])
print(scores, best)

# Out-of-fold predictions along every training engine's life (engines never seen by the model that scores them)
oof = np.zeros(len(Ftr))
for trn, val in GroupKFold(5).split(Ftr, y, Ftr.unit):
    m = HistGradientBoostingRegressor(max_iter=400, learning_rate=0.05, max_leaf_nodes=31, random_state=42) if best == 'Gradient boosting' else models[best].__class__(**models[best].get_params())
    m.fit(Ftr.iloc[trn][X], y[trn]); oof[val] = m.predict(Ftr.iloc[val][X])
Ftr['pred'] = np.clip(oof, 0, None); Ftr['rul'] = tr.sort_values(['unit', 'cycle']).rul.to_numpy()
lives = tr.groupby('unit').life.first()

# Policies: for each engine, a run ends at planned service (cycle t) or failure (end of life)
def predictive(th):
    rows = []
    for u, g in Ftr.groupby('unit'):
        hit = g[(g.pred <= th) & (g.cycle >= 30)]
        if len(hit): rows.append((int(hit.cycle.iloc[0]), False, int(hit.rul.iloc[0])))
        else: rows.append((int(lives[u]), True, 0))
    return rows
def fixed(n):
    return [(n, False, int(L - n)) if n < L else (int(L), True, 0) for L in lives]
def summary(rows):
    cyc = sum(r[0] for r in rows); fail = sum(r[1] for r in rows); waste = sum(r[2] for r in rows if not r[1])
    return {'cycles': cyc, 'failures': int(fail), 'services': int(len(rows) - fail), 'wasted': int(waste)}
pred_pol = [{'th': th, **summary(predictive(th))} for th in range(0, 61, 2)]
fix_pol = [{'n': n, **summary(fixed(n))} for n in range(100, 301, 5)]

# Example engine trace for the chart
ex_units = [int(u) for u in lives.sort_values().index[[10, 50, 90]]]
traces = {str(u): [{'c': int(c), 'rul': int(r), 'pred': round(float(p), 1)} for c, r, p in zip(g.cycle, g.rul, g.pred)] for u, g in Ftr[Ftr.unit.isin(ex_units)].groupby('unit')}
test_rows = [{'unit': int(i + 1), 'true': int(rul_te[i]), 'pred': round(float(preds[best][i]), 1)} for i in range(100)]
res = {
    'data': {'trainEngines': int(tr.unit.nunique()), 'testEngines': 100, 'rows': int(len(tr) + len(te)), 'sensors': len(SENS),
             'lifeMin': int(lives.min()), 'lifeMax': int(lives.max()), 'lifeMedian': int(lives.median())},
    'scores': scores, 'best': best, 'cap': CAP, 'test': test_rows, 'traces': traces,
    'predictive': pred_pol, 'fixed': fix_pol,
}
out.write_text(json.dumps(res))
print(json.dumps(res['data']), pred_pol[::5], fix_pol[::8])
