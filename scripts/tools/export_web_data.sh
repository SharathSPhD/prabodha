#!/bin/bash
# Helper script to export data for GitHub Pages site.
# Runs scripts/tools/export_app_data.py with web-specific output paths.
# Usage: bash scripts/tools/export_web_data.sh [--repo-root .]

set -e

REPO_ROOT="${1:-.}"

echo "Exporting prabodha data for web site..."
python3 scripts/tools/export_app_data.py \
  --repo-root "$REPO_ROOT" \
  --out-app apps/web/public/data \
  --out-web web/prabodha-data.js

echo "✓ Web data exported to:"
echo "  - web/prabodha-data.js (window.PRABODHA)"
echo "  - web/data/fire_slice.json (if fire-case traces available)"

# TODO: Add slice export for D3 heatmap
# if [ -f outputs/traces/fire_case_L11_seed42.json ]; then
#   python3 scripts/tools/export_slice_data.py outputs/traces/fire_case_L11_seed42.json > web/data/fire_slice.json
# fi
