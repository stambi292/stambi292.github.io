"""Build fraud-detection/index.html from template.html and data/results.json."""
import json, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
d = json.loads((root / 'data' / 'results.json').read_text())
C = {c['t']: c for c in d['curve']}
r, hi = d['recommended'], C[0.5]
band = {k: r[k] - hi[k] for k in ('flagged', 'caught', 'falseAlarms', 'caughtEur')}
eur = lambda v: f"€{round(v):,}"
d['recs'] = [
    {'tag': 'Two tiers', 'h': 'Block the obvious, review the rest',
     'p': f"Above a score of 0.50 the model flagged {hi['flagged']} payments and {hi['caught']} were fraud, so these can be declined automatically. "
          f"Between {r['t']:.2f} and 0.50 sit {band['flagged']} more alerts with {band['caught']} frauds worth {eur(band['caughtEur'])}: send those to an analyst or a 3-D Secure check."},
    {'tag': 'Threshold', 'h': 'Set the threshold by cost, not by accuracy',
     'p': f"The best setting depends on what a review costs. At €5 to €15 per alert, {r['t']:.2f} saves the most; at €30 the best point moves up to 0.30. Finance and fraud teams should agree the review cost first, then let the curve pick the threshold."},
    {'tag': 'Blind spot', 'h': 'Cover the frauds the model misses',
     'p': f"At the recommended setting {r['missed']} frauds worth {eur(r['missedEur'])} still get through, about {eur(r['missedEur'] / r['missed'])} each. Simple rules on top of the model, like limits on many payments in a short time or a new merchant, can catch part of this."},
    {'tag': 'Over time', 'h': 'Retrain and watch the alerts',
     'p': "Fraudsters change tactics, so a model trained once slowly gets worse. Retrain on recent payments on a fixed schedule, and track the share of alerts that turn out to be fraud: a falling share is the early warning."},
]
html = (root / 'scripts' / 'template.html').read_text().replace('/*__DATA__*/null', json.dumps(d, separators=(',', ':')))
(root / 'index.html').write_text(html)
print('wrote index.html', len(html))
