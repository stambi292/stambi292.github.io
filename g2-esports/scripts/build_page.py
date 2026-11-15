"""Build bmw-group/index.html from data/g2.json (public esports data)."""
import json, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
data = json.loads((root / 'data/g2.json').read_text())
html = (root / 'scripts/template.html').read_text().replace('/*__DATA__*/null', json.dumps(data, ensure_ascii=False))
(root / 'index.html').write_text(html); print('ok')
