#!/usr/bin/env bash
# Downloads the public Olist dataset into data/raw (the CSVs are not committed to git).
set -euo pipefail
cd "$(dirname "$0")/.."
tmp=$(mktemp -d)
git clone --depth 1 https://github.com/olist/work-at-olist-data.git "$tmp/olist"
mkdir -p data/raw
cp "$tmp"/olist/datasets/*.csv data/raw/
rm -f data/raw/olist_geolocation_dataset.csv   # not used in this project
rm -rf "$tmp"
echo "Data ready in data/raw/"
ls data/raw
