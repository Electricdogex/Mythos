#!/usr/bin/env bash
set -e

echo "Installing Mythos 532026 Alpha..."

INSTALL_DIR="$(cd "$(dirname "$0")" && pwd)"

chmod +x mythos.py
mkdir -p .mythos/pids
mkdir -p .mythos/logs

if [ ! -f mythos.json ]; then
  echo '{ "name": "Mythos", "version": "532026-alpha", "programs": [] }' > mythos.json
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
echo "Setting up Mythos startup service..."

if command -v systemctl >/dev/null 2>&1; then
  cat > /etc/systemd/system/mythos.service <<EOF
[Unit]
Description=Mythos Program Runner
After=network.target

[Service]
Type=oneshot
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 $INSTALL_DIR/mythos.py start
ExecStop=/usr/bin/python3 $INSTALL_DIR/mythos.py stop
RemainAfterExit=yes
User=root

[Install]
WantedBy=multi-user.target
EOF

  systemctl daemon-reload
  systemctl enable mythos
  systemctl start mythos || true

  echo "Mythos startup service enabled."
  echo "Check it with:"
  echo "  systemctl status mythos"
else
  echo "systemctl was not found. Skipping automatic startup setup."
fi

echo ""
echo "Mythos 532026 Alpha is installed."
echo ""
echo "New programs use autostart: true by default."
echo ""
echo "Try:"
echo "  ./mythos.py version"
echo "  ./mythos.py status"
echo "  ./mythos.py startup-status"
echo "  ./mythos.py pm2-status"
echo "  ./mythos.py make-test"
