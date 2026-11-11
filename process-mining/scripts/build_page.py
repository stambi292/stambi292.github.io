"""Build process-mining/index.html from template.html and data/results.json."""
import json, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
d = json.loads((root / 'data' / 'results.json').read_text())
c, a = d['cycle'], d['afterTheFact']
d['recs'] = [
    {'tag': 'Payment blocks', 'h': 'Find out why invoices get blocked',
     'p': f"{d['blockShare']}% of items hit a payment block and then take {c['blocked']['median']} days to pay, against {c['clean']['median']} for clean items. Group blocks by vendor and reason: if a few vendors cause most of them, fix their price and quantity data instead of checking every invoice by hand."},
    {'tag': 'Rework', 'h': 'Fix orders before they are sent',
     'p': f"{d['reworkShare']}% of items are changed or cancelled after ordering, and quantity changes alone touch {d['rework'][0]['share']}% of items. Better catalogue prices and approval checks at the requisition stage stop the rework that slows payment down."},
    {'tag': 'Compliance', 'h': 'Stop orders created after the invoice',
     'p': f"{a['cases']:,} items ({a['share']}%) got their purchase order only after the vendor had already invoiced. That is buying outside the process. Flag these automatically and follow up with the departments that cause them."},
    {'tag': 'Automation', 'h': 'Automate the invoice steps first',
     'p': "Recording invoices and clearing payments are the most frequent manual steps after ordering and receiving goods. Automatic invoice matching for clean three-way matches is the quickest win and frees staff for the exceptions."},
]
html = (root / 'scripts' / 'template.html').read_text().replace('/*__DATA__*/null', json.dumps(d, separators=(',', ':')))
(root / 'index.html').write_text(html)
print('ok', len(html))
