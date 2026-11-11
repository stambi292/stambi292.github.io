"""Build predictive-maintenance/index.html from template.html and data/results.json."""
import json, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
d = json.loads((root / 'data' / 'results.json').read_text())
P = {p['th']: p for p in d['predictive']}
d['recs'] = [
    {'tag': 'Start safe', 'h': 'Begin with a wide safety margin',
     'p': f"With a margin of 20 cycles the model caused no failures and left about {round(P[20]['wasted'] / 100)} cycles of life unused per engine; with 6 cycles, one engine failed. Start wide, then narrow the margin as the model proves itself on your own fleet."},
    {'tag': 'Fleet', 'h': 'Rank the fleet by risk every day',
     'p': "The same score that triggers a service can sort every vehicle or system by remaining life. Planners see which units need parts and workshop slots next week, instead of finding out when something breaks."},
    {'tag': 'Data', 'h': 'Label real failures from maintenance logs',
     'p': "Real fleets rarely run to failure, so labels are scarce. Workshop reports and maintenance logs hold that history as free text; a language model can turn them into structured failure records that train the next model."},
    {'tag': 'Trust', 'h': 'Show engineers why the model alarms',
     'p': "Pair every alert with the sensors that moved: for these engines, temperature and pressure trends carried the signal. Engineers act faster on an alert they can check than on a number they cannot."},
]
html = (root / 'scripts' / 'template.html').read_text().replace('/*__DATA__*/null', json.dumps(d, separators=(',', ':')))
(root / 'index.html').write_text(html)
print('ok', len(html))
