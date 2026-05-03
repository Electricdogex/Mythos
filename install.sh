#!/usr/bin/env bash
set -e

echo "Installing Mythos 522026 Alpha..."

chmod +x mythos.py
mkdir -p .mythos/pids
mkdir -p .mythos/logs

if [ ! -f mythos.json ]; then
  echo '{ "name": "Mythos", "version": "522026-alpha", "programs": [] }' > mythos.json
fi

if [ -f .mythos/installer_eula_accepted ]; then
  python3 mythos.py accept-eula --yes >/dev/null 2>&1 || true
fi

echo ""
echo "Installing/updating PM2 automatically..."

if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
  echo "Node.js/npm not found. Installing through apt..."
  apt update
  apt install -y nodejs npm
else
  echo "Node.js and npm are already installed."
fi

npm install -g pm2@latest

echo ""
echo "PM2 version:"
pm2 --version || true

echo ""
echo "Mythos 522026 Alpha is installed."
echo ""
echo "Try:"
echo "  ./mythos.py version"
echo "  ./mythos.py status"
echo "  ./mythos.py pm2-status"
echo "  ./mythos.py make-test"
