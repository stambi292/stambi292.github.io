"""Build analytics-enablement/index.html from data/coty_fy25.json (figures typed from Coty's FY25 results release)."""
import json, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
data = json.loads((root / 'data/coty_fy25.json').read_text())
html = (root / 'scripts/template.html').read_text().replace('/*__DATA__*/null', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
(root / 'index.html').write_text(html); print('ok', len(html))
