#!/usr/bin/env zsh
set -euo pipefail

cd "$(dirname "$0")"

python3 -m pip show pyinstaller >/dev/null 2>&1 || {
  echo "PyInstaller is not installed."
  echo "Run: python3 -m pip install Pillow pyinstaller"
  exit 1
}

python3 -m PyInstaller \
  --windowed \
  --name SaveImageToLink \
  save_image_to_link_macos.py

echo "Built: dist/SaveImageToLink.app"

