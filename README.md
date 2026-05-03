# Mythos 522026 Alpha

Tiny VPS program runner.

This is an early **Alpha** build.

## What Mythos does

Mythos lets you run multiple programs on one VPS from a simple config file.

Examples:

- Discord bot
- Web server
- Python script
- Node.js server
- Game server helper
- Background automation

Mythos starts empty. It does not include real apps, bots, databases, or servers.

## Features

- Program-based config
- EULA acceptance
- EULA-gated self-extracting installer
- PM2 auto-install/update
- Program start/stop/restart/status
- Program logs
- Included test program
- Backward compatibility with old `"services"` configs

## Repository layout

```txt
mythos-522026-alpha/
├─ INSTALL-DIRECTIONS.md
├─ mythos.py
├─ mythos.json
├─ install.sh
├─ EULA.md
├─ LICENSE
├─ README.md
├─ CHANGELOG.md
├─ .gitignore
├─ examples/
│  └─ test_program.py
└─ release/
   └─ mythos_522026_alpha_installer.sh
```

## Install from the release installer

The recommended install method is the release installer.

The installer does not extract Mythos until the EULA is accepted.

The installer file is here:

```txt
release/mythos_522026_alpha_installer.sh
```

Upload it to your VPS:

```powershell
scp "PATH_TO_INSTALLER\mythos_522026_alpha_installer.sh" root@YOUR_SERVER_IP:/root/
```

Example:

```powershell
scp "C:\Users\YourName\Downloads\mythos-522026-alpha\release\mythos_522026_alpha_installer.sh" root@YOUR_SERVER_IP:/root/
```

Connect to the VPS:

```powershell
ssh root@YOUR_SERVER_IP
```

Run the installer:

```bash
cd /root
chmod +x mythos_522026_alpha_installer.sh
./mythos_522026_alpha_installer.sh
```

When prompted, type:

```txt
ACCEPT
```

## Install from GitHub clone

This method is useful for developers who want to edit the source.

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
chmod +x install.sh mythos.py
./install.sh
./mythos.py eula
./mythos.py accept-eula
./mythos.py version
```

Replace:

```txt
YOUR_USERNAME/YOUR_REPO_NAME
```

with your actual GitHub repo path.

## Test Mythos

```bash
cd /root/mythos
./mythos.py version
./mythos.py status
./mythos.py pm2-status

./mythos.py make-test
./mythos.py start mythos-test
./mythos.py logs mythos-test
```

Stop and remove the test:

```bash
./mythos.py stop mythos-test
./mythos.py remove mythos-test
```

## How Mythos programs work

A Mythos **program** is just a command that Mythos can start, stop, and log.

A program has:

- `name` — the Mythos name for the program
- `command` — the command to run
- `cwd` — the folder where the command runs
- `autostart` — whether it starts when you run `./mythos.py start`
- `env` — optional environment variables

Example:

```json
{
  "name": "discord-bot",
  "command": "node bot.js",
  "cwd": "/root/my-discord-bot",
  "autostart": true,
  "restart": "never",
  "env": {
    "NODE_ENV": "production"
  }
}
```

## Make a simple Python program

```bash
mkdir -p /root/my-first-program
cd /root/my-first-program
nano app.py
```

Paste:

```python
import time

count = 0
print("My first Mythos program started.", flush=True)

while True:
    count += 1
    print(f"Program heartbeat {count}", flush=True)
    time.sleep(5)
```

Add it:

```bash
cd /root/mythos
./mythos.py add my-first-program "python3 app.py" --cwd "/root/my-first-program"
```

Start it:

```bash
./mythos.py start my-first-program
./mythos.py logs my-first-program
```

Stop it:

```bash
./mythos.py stop my-first-program
```

## Make a simple Node.js program

```bash
mkdir -p /root/my-node-program
cd /root/my-node-program
nano app.js
```

Paste:

```javascript
let count = 0;

console.log("My Node.js Mythos program started.");

setInterval(() => {
  count += 1;
  console.log(`Node heartbeat ${count}`);
}, 5000);
```

Add it:

```bash
cd /root/mythos
./mythos.py add my-node-program "node app.js" --cwd "/root/my-node-program"
```

Start it:

```bash
./mythos.py start my-node-program
./mythos.py logs my-node-program
```

## Core commands

```bash
./mythos.py version
./mythos.py eula
./mythos.py accept-eula
./mythos.py list
./mythos.py start
./mythos.py start program-name
./mythos.py stop
./mythos.py stop program-name
./mythos.py restart program-name
./mythos.py logs program-name
./mythos.py remove program-name
```

## PM2 commands

```bash
./mythos.py pm2-status
./mythos.py install-pm2
./mythos.py update-pm2
```

## Optional systemd startup

```bash
nano /etc/systemd/system/mythos.service
```

Paste:

```ini
[Unit]
Description=Mythos Program Runner
After=network.target

[Service]
Type=oneshot
WorkingDirectory=/root/mythos
ExecStart=/usr/bin/python3 /root/mythos/mythos.py start
ExecStop=/usr/bin/python3 /root/mythos/mythos.py stop
RemainAfterExit=yes
User=root

[Install]
WantedBy=multi-user.target
```

Enable:

```bash
systemctl daemon-reload
systemctl enable mythos
systemctl start mythos
systemctl status mythos
```
