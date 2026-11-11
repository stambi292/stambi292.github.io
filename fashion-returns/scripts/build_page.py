"""Build fashion-returns/index.html from template.html and data/results.json."""
import json, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
d = json.loads((root / 'data' / 'results.json').read_text())
sz, dec, c = d['drivers']['sizes'], d['model']['deciles'], d['customers']
d['recs'] = [
    {'tag': 'Size advice', 'h': 'Step in when a second size goes in the basket',
     'p': f"Bracketed items come back {sz[1]['rate']}% of the time. The moment a customer adds the same item in a second size is the best time to show a size recommendation or fit notes from other buyers. Zalando reports its Size & Fit tools already prevented 8% of size-related returns in 2025."},
    {'tag': 'Targeting', 'h': 'Use the risk score to help, not to punish',
     'p': f"The riskiest tenth of items comes back {dec[0]['rate']}% of the time. Show those items extra fit information, model measurements and reviews before checkout, and leave low-risk items alone so the shopping stays easy."},
    {'tag': 'Customers', 'h': 'Deal with the few, not the many',
     'p': f"{c['top10share']}% of returns come from 10% of customers, and {c['neverReturn']}% never return anything. Rules should target extreme, persistent returners, as Zalando did in 2025 for about 0.02% of its customers, while free returns stay free for everyone else."},
    {'tag': 'Payment', 'h': 'Keep pay-later, but use it as a signal',
     'p': "Invoice customers return more, but they are most of the business. Removing invoice payment would lose sales; feeding payment type into the risk model captures the effect without changing the checkout."},
]
html = (root / 'scripts' / 'template.html').read_text().replace('/*__DATA__*/null', json.dumps(d, separators=(',', ':')))
(root / 'index.html').write_text(html)
print('ok', len(html))
