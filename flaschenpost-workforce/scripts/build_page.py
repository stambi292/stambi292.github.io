"""Build flaschenpost-workforce/index.html from data/workforce.json (IBM public HR sample)."""
import json, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
data = json.loads((root / 'data/workforce.json').read_text())
html = (root / 'scripts/template.html').read_text().replace('/*__DATA__*/null', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
(root / 'index.html').write_text(html); print('ok', len(html))
