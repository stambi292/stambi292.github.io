"""Build index.html: insert data/amazon_data.json into src/template.html.

Usage (from the project folder):  python scripts/build_page.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEAD = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n')


def main():
    data = json.loads((ROOT / "data" / "amazon_data.json").read_text(encoding="utf-8"))
    template = (ROOT / "src" / "template.html").read_text(encoding="utf-8")
    page = template.replace("/*__DATA__*/{}", json.dumps(data, separators=(",", ":")))
    split = page.index('<header class="band">')
    html = HEAD + page[:split] + "</head>\n<body>\n" + page[split:] + "\n</body>\n</html>\n"
    (ROOT / "index.html").write_text(html, encoding="utf-8")
    print("index.html written")


if __name__ == "__main__":
    main()
