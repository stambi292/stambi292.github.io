"""Build bmw-group/index.html from data/bmw.json (BMW Group sales releases and reports)."""
import json, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
data = json.loads((root / 'data/bmw.json').read_text())
html = (root / 'scripts/template.html').read_text().replace('/*__DATA__*/null', json.dumps(data, ensure_ascii=False))
(root / 'index.html').write_text(html); print('ok')
