#!/usr/bin/env bash
set -e

cd "$(dirname "${BASH_SOURCE[0]}")"

echo "============================================================" 
echo "                J-BOT - RUN ONLINE" 
echo "============================================================" 

if [ -f "venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source venv/bin/activate
else
  echo "[WARN] venv not found. Trying system python..."
fi

echo "[INFO] Working directory: $(pwd)"

python ongent.py
