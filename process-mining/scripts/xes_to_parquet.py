"""Convert the BPI Challenge 2019 XES log to a flat events table (one row per event, case attributes included)."""
import gzip, sys, pandas as pd
from lxml import etree
src, dst = sys.argv[1], sys.argv[2]
rows, case = [], {}
TAGS = {'string', 'date', 'float', 'int', 'boolean'}
for ev, el in etree.iterparse(gzip.open(src), events=('end',), huge_tree=True):
    tag = etree.QName(el).localname
    if tag == 'event':
        e = {'case:' + k: v for k, v in case.items()}
        for c in el:
            if etree.QName(c).localname in TAGS: e[c.get('key')] = c.get('value')
        rows.append(e); el.clear()
    elif tag == 'trace':
        case = {}; el.clear()
    elif tag in TAGS and el.getparent() is not None and etree.QName(el.getparent()).localname == 'trace':
        case[el.get('key')] = el.get('value')
# trace attributes come before events in XES, but iterparse 'end' fires for them first too, so case is filled in time
df = pd.DataFrame(rows)
df.to_parquet(dst)
print(df.shape); print(df.columns.tolist()); print(df.head(3).T)
