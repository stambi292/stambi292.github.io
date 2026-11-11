"""Fashion returns: what drives them and what they cost.

Data: Data Mining Cup 2016 (prudsys AG), order lines of a German online fashion retailer, Jan 2014 to Sep 2015.
    python scripts/analyse.py data/orders_train.txt
Writes data/results.json.
"""
import json, sys, pathlib
import numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, average_precision_score

out = pathlib.Path(__file__).resolve().parents[1] / 'data' / 'results.json'
df = pd.read_csv(sys.argv[1], sep=';')
df = df[(df.quantity > 0) & (df.price > 0) & df.rrp.notna() & df.productGroup.notna()].copy()
df['orderDate'] = pd.to_datetime(df.orderDate)
df['retVal'] = df.price * df.returnQuantity / df.quantity
items, rets = df.quantity.sum(), df.returnQuantity.sum()

def table(col, labels=None):
    g = df.groupby(col, observed=True).agg(q=('quantity', 'sum'), r=('returnQuantity', 'sum'))
    return [{'label': (labels or {}).get(k, str(k)), 'share': round(v.q / items * 100, 1), 'rate': round(v.r / v.q * 100, 1)} for k, v in g.iterrows()]

# Features known at the moment of ordering
df['sizes'] = np.minimum(df.groupby(['orderID', 'articleID', 'colorCode']).sizeCode.transform('nunique'), 3)
df['colors'] = np.minimum(df.groupby(['orderID', 'articleID']).colorCode.transform('nunique'), 3)
df['orderItems'] = df.groupby('orderID').quantity.transform('sum')
df['disc'] = 1 - df.price / df.rrp
df['payLater'] = df.paymentMethod.isin(['BPRG', 'RG', 'KGRG', 'BPPL'])

# Customer history: returns and items from earlier days only
day = df.groupby(['customerID', 'orderDate']).agg(q=('quantity', 'sum'), r=('returnQuantity', 'sum')).reset_index().sort_values(['customerID', 'orderDate'])
day['histQ'] = day.groupby('customerID').q.cumsum() - day.q
day['histR'] = day.groupby('customerID').r.cumsum() - day.r
df = df.merge(day[['customerID', 'orderDate', 'histQ', 'histR']], on=['customerID', 'orderDate'])
df['histRate'] = np.where(df.histQ > 0, df.histR / df.histQ.clip(lower=1), np.nan)

drivers = {
    'sizes': table('sizes', {1: 'One size', 2: 'Two sizes', 3: 'Three or more'}),
    'orderItems': table(np.minimum(df.orderItems, 6).rename('o'), {6: '6+'}),
    'price': table(pd.cut(df.price, [0, 15, 30, 50, 80, 1e5]).rename('p'), None),
    'payment': table(df.payLater.map({True: 'Pay later (invoice)', False: 'Paid upfront'}).rename('pay')),
    'discount': table(pd.cut(df.disc, [-1, 0.001, 0.4, 0.6, 1], labels=['Full price', 'Up to 40% off', '40-60% off', 'Over 60% off']).rename('d')),
}
drivers['price'] = [dict(d, label=l) for d, l in zip(drivers['price'], ['Under €15', '€15–30', '€30–50', '€50–80', 'Over €80'])]

cust = df.groupby('customerID').agg(q=('quantity', 'sum'), r=('returnQuantity', 'sum')).sort_values('r', ascending=False)
cum = cust.r.cumsum() / cust.r.sum()
customers = {'n': int(len(cust)), 'top10share': round(float(cum.iloc[int(len(cust) * .1)]) * 100, 1),
             'top1share': round(float(cum.iloc[int(len(cust) * .01)]) * 100, 1), 'neverReturn': round(float((cust.r == 0).mean()) * 100, 1)}

# Model: will this item come back? Train on 2014 to Mar 2015, test on Apr to Sep 2015.
feats = ['price', 'rrp', 'disc', 'sizes', 'colors', 'orderItems', 'payLater', 'deviceID', 'productGroup', 'voucherAmount', 'histQ', 'histRate']
X = df[feats].astype(float); y = (df.returnQuantity > 0).astype(int)
tr, te = df.orderDate < '2015-04-01', df.orderDate >= '2015-04-01'
m = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.08, max_leaf_nodes=63, random_state=42).fit(X[tr], y[tr])
p = m.predict_proba(X[te])[:, 1]
yt, val = y[te].to_numpy(), df.loc[te, 'price'].to_numpy()
deciles = []
order = np.argsort(-p)
for i, chunk in enumerate(np.array_split(order, 10)):
    deciles.append({'decile': i + 1, 'rate': round(float(yt[chunk].mean()) * 100, 1), 'avgScore': round(float(p[chunk].mean()) * 100, 1)})
model = {'auc': round(roc_auc_score(yt, p), 3), 'ap': round(average_precision_score(yt, p), 3), 'base': round(float(yt.mean()) * 100, 1),
         'testLines': int(te.sum()), 'deciles': deciles}

months = (df.orderDate.max() - df.orderDate.min()).days / 30.44
res = {
    'dataset': {'lines': int(len(df)), 'items': int(items), 'orders': int(df.orderID.nunique()), 'customers': customers['n'],
                'from': '2014-01', 'to': '2015-09', 'months': round(months, 1), 'sales': round(float(df.price.sum())),
                'returnRate': round(rets / items * 100, 1), 'returnedValue': round(float(df.retVal.sum())),
                'returnedValueShare': round(float(df.retVal.sum() / df.price.sum()) * 100, 1), 'returnedItems': int(rets),
                'avgPrice': round(float(df.price.sum() / items), 2)},
    'drivers': drivers, 'customers': customers, 'model': model,
}
out.write_text(json.dumps(res, indent=1))
print(json.dumps({k: v for k, v in res.items() if k != 'drivers'}, indent=1))
print(json.dumps(drivers))
