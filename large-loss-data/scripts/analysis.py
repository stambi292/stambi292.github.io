"""Large-loss data prototype: validate and summarise NOAA's US billion-dollar disaster events, 1980-2024 (CPI-adjusted, $m)."""
import pandas as pd, json, pathlib, numpy as np
root = pathlib.Path(__file__).resolve().parents[1]
raw = pd.read_csv(root / 'data/noaa_billion_dollar_events_1980_2024.csv')
df = raw.copy()
df['begin'] = pd.to_datetime(df['Begin Date'].astype(str), format='%Y%m%d', errors='coerce')
df['end'] = pd.to_datetime(df['End Date'].astype(str), format='%Y%m%d', errors='coerce')
df['year'] = df.begin.dt.year
checks = [
 ('Every event has a name and a peril', int(df.Name.isna().sum() + df.Disaster.isna().sum()) == 0),
 ('Every begin and end date is a valid date', bool(df.begin.notna().all() and df.end.notna().all())),
 ('No event ends before it begins', bool((df.end >= df.begin).all())),
 ('Every loss is positive', bool((df['CPI-Adjusted Cost'] > 0).all() and (df['Unadjusted Cost'] > 0).all())),
 ('Inflation-adjusted loss is never below the original loss', bool((df['CPI-Adjusted Cost'] >= df['Unadjusted Cost'] - 0.5).all())),
 ('No duplicate events (same name and dates)', bool(not df.duplicated(['Name', 'Begin Date', 'End Date']).any())),
 ('Deaths are whole numbers, zero or more', bool((df.Deaths >= 0).all())),
 ('Every event costs at least $1bn after inflation (the dataset rule)', bool((df['CPI-Adjusted Cost'] >= 1000).all())),
]
ev = [{'n': r.Name.strip(), 'p': r.Disaster, 'y': int(r.year), 'b': r.begin.strftime('%Y-%m-%d'), 'e': r.end.strftime('%Y-%m-%d'),
       'l': round(float(r['CPI-Adjusted Cost']), 1), 'u': round(float(r['Unadjusted Cost']), 1), 'd': int(r.Deaths)} for _, r in df.iterrows()]
out = {'events': ev, 'checks': [{'t': t, 'ok': ok} for t, ok in checks], 'rows': len(raw),
       'years': [int(df.year.min()), int(df.year.max())], 'total': round(df['CPI-Adjusted Cost'].sum() / 1000, 1)}
(root / 'data/large_losses.json').write_text(json.dumps(out, ensure_ascii=False))
a = df.groupby('year')['CPI-Adjusted Cost'].agg(['sum', 'count'])
print(len(df), out['total'], df.Disaster.value_counts().to_dict())
print(df.groupby('Disaster')['CPI-Adjusted Cost'].sum().sort_values(ascending=False).div(1000).round(1).to_dict())
print('1980s avg events', a.loc[1980:1989,'count'].mean(), '2015-24 avg', a.loc[2015:2024,'count'].mean())
print('1980s avg $bn', a.loc[1980:1989,'sum'].mean()/1000, '2015-24', a.loc[2015:2024,'sum'].mean()/1000)
print(df.sort_values('CPI-Adjusted Cost',ascending=False)[['Name','CPI-Adjusted Cost']].head(5).to_string())
print([c for c in checks if not c[1]])
