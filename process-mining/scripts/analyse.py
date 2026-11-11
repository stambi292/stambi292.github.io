"""Purchase-to-pay process mining on the BPI Challenge 2019 event log.

    python scripts/xes_to_parquet.py data/BPI_Challenge_2019.xes.gz data/events.parquet
    python scripts/analyse.py data/events.parquet
Writes data/results.json. Scope: purchase order items created in 2018.
"""
import json, sys, pathlib
import numpy as np, pandas as pd
out = pathlib.Path(__file__).resolve().parents[1] / 'data' / 'results.json'
df = pd.read_parquet(sys.argv[1]).rename(columns={'case:concept:name': 'case', 'concept:name': 'act'})
df['ts'] = pd.to_datetime(df['time:timestamp'], utc=True, format='ISO8601')
df['amt'] = df['Cumulative net worth (EUR)'].astype(float)
df = df.sort_values(['case', 'ts'], kind='stable')
created = df[df.act == 'Create Purchase Order Item'].groupby('case').ts.min()
cases = created[(created >= '2018-01-01') & (created < '2019-01-01')].index
df = df[df.case.isin(cases)]
N = len(cases)
value = df.groupby('case').amt.max()
first = lambda a, f='min': df[df.act == a].groupby('case').ts.agg(f)
days = lambda s: s.dt.total_seconds() / 86400

# Paths (variants)
var = df.groupby('case').act.agg(tuple)
vc = var.value_counts()
cum = vc.cumsum() / N
SHORT = {'Create Purchase Order Item': 'Create PO', 'Vendor creates invoice': 'Vendor invoice', 'Record Goods Receipt': 'Goods received',
         'Record Invoice Receipt': 'Invoice recorded', 'Clear Invoice': 'Paid', 'Remove Payment Block': 'Unblock payment',
         'Receive Order Confirmation': 'Order confirmed', 'Create Purchase Requisition Item': 'Requisition', 'Record Service Entry Sheet': 'Service entry',
         'Change Quantity': 'Change quantity', 'Change Price': 'Change price', 'Cancel Invoice Receipt': 'Cancel invoice'}
variants = [{'steps': [SHORT.get(a, a) for a in v], 'share': round(c / N * 100, 2), 'cases': int(c)} for v, c in vc.head(8).items()]

# Cycle time: PO created to invoice cleared
paid = first('Clear Invoice', 'max')
ct = days(paid - created.reindex(paid.index))
ct = ct[ct >= 0]
blocked = set(df[df.act == 'Remove Payment Block'].case)
REWORK = ['Change Price', 'Change Quantity', 'Change Approval for Purchase Order', 'Cancel Invoice Receipt', 'Delete Purchase Order Item',
          'Cancel Goods Receipt', 'Change Delivery Indicator', 'Cancel Subsequent Invoice', 'Block Purchase Order Item',
          'Reactivate Purchase Order Item', 'Change Currency', 'Change payment term']
rework = set(df[df.act.isin(REWORK)].case)
groups = {'all': ct, 'blocked': ct[ct.index.isin(blocked)], 'clean': ct[~ct.index.isin(blocked) & ~ct.index.isin(rework)], 'rework': ct[ct.index.isin(rework)]}
bins = np.arange(0, 211, 10)
hist = {k: {'median': round(float(v.median()), 1), 'over90': round(float((v > 90).mean()) * 100, 1), 'n': int(len(v)),
            'pct': [round(float(x), 2) for x in np.histogram(v.clip(upper=209.9), bins=bins)[0] / len(v) * 100]} for k, v in groups.items()}

def wait(a, b):
    A, B = first(a), first(b)
    d = days(B - A.reindex(B.index)).dropna(); d = d[d >= 0]
    return round(float(d.median()), 1)
flow = [
    {'from': 'Create PO', 'to': 'Goods received', 'days': wait('Create Purchase Order Item', 'Record Goods Receipt')},
    {'from': 'Goods received', 'to': 'Invoice recorded', 'days': wait('Record Goods Receipt', 'Record Invoice Receipt')},
    {'from': 'Invoice recorded', 'to': 'Paid', 'days': wait('Record Invoice Receipt', 'Clear Invoice')},
]
vi = first('Vendor creates invoice')
flow_extra = {'invoiceToRecorded': wait('Vendor creates invoice', 'Record Invoice Receipt'), 'unblockToPaid': wait('Remove Payment Block', 'Clear Invoice')}

rework_rows = []
for a in ['Change Quantity', 'Change Price', 'Delete Purchase Order Item', 'Cancel Invoice Receipt', 'Change Approval for Purchase Order', 'Change Delivery Indicator', 'Cancel Goods Receipt']:
    s = set(df[df.act == a].case)
    rework_rows.append({'act': a, 'share': round(len(s) / N * 100, 2), 'median': round(float(ct[ct.index.isin(s)].median()), 1)})

after = (vi < created.reindex(vi.index))
after_cases = after[after].index

res_kind = np.where(df['org:resource'].str.startswith('user'), 'People', np.where(df['org:resource'].str.startswith('batch'), 'Automated jobs', 'Vendor or system'))
kind = pd.Series(res_kind).value_counts()
manual = df[res_kind == 'People']
manual_by_act = manual.act.value_counts()
users = manual['org:resource'].value_counts()

res = {
    'scope': {'cases': int(N), 'events': int(len(df)), 'activities': int(df.act.nunique()), 'value': round(float(value.sum())),
              'medianValue': round(float(value.median())), 'vendors': int(df['case:Vendor'].nunique()), 'companies': int(df['case:Company'].nunique()),
              'paid': int(len(ct))},
    'variants': {'count': int(len(vc)), 'topShare': round(float(vc.iloc[0] / N) * 100, 1), 'for80': int((cum < 0.8).sum() + 1),
                 'once': int((vc == 1).sum()), 'top': variants},
    'cycle': hist, 'flow': flow, 'flowExtra': flow_extra,
    'blockShare': round(len(blocked) / N * 100, 1), 'reworkShare': round(len(rework) / N * 100, 1),
    'rework': rework_rows, 'reworkEvents': int(df.act.isin(REWORK).sum()),
    'afterTheFact': {'cases': int(len(after_cases)), 'share': round(len(after_cases) / N * 100, 2), 'value': round(float(value[after_cases].sum()))},
    'work': {'kinds': {k: round(v / len(df) * 100, 1) for k, v in kind.items()}, 'manualEvents': int(len(manual)),
             'manualPerCase': round(len(manual) / N, 2), 'users': int(len(users)), 'topUserShare': round(float(users.iloc[0] / len(manual)) * 100, 1),
             'manualTop': [{'act': SHORT.get(a, a), 'n': int(n)} for a, n in manual_by_act.head(6).items()],
             'invoiceSteps': int(manual_by_act.reindex(['Record Invoice Receipt', 'Clear Invoice', 'Remove Payment Block']).sum())},
}
out.write_text(json.dumps(res, indent=1))
print(json.dumps({k: v for k, v in res.items() if k not in ('cycle', 'variants')}, indent=1))
print(res['variants']['count'], res['variants']['topShare'], res['variants']['for80'], {k: (v['median'], v['over90'], v['n']) for k, v in hist.items()})
