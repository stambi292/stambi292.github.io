"""Build large-loss-data/index.html from data/large_losses.json (NOAA billion-dollar events)."""
import json, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
data = json.loads((root / 'data/large_losses.json').read_text())
html = (root / 'scripts/template.html').read_text().replace('/*__DATA__*/null', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
(root / 'index.html').write_text(html); print('ok', len(html))
