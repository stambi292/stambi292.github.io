"""Build dhl-group/index.html from data/dhl.json (DHL Group reports, trade press)."""
import json, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
data = json.loads((root / 'data/dhl.json').read_text())
html = (root / 'scripts/template.html').read_text().replace('/*__DATA__*/null', json.dumps(data, ensure_ascii=False))
(root / 'index.html').write_text(html); print('ok')
