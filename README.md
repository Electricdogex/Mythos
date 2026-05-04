# Mythos 532026 Alpha

Tiny VPS program runner.

This is an early **Alpha** build.

## What changed from 522026 Alpha

- Installer now automatically creates and enables the `mythos.service` systemd startup service.
- Mythos now starts on VPS boot after install.
- Programs added with `./mythos.py add` use `autostart: true` by default.
- Added `./mythos.py startup-status` to check the systemd service.

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
- Automatic systemd startup setup
- Program start/stop/restart/status
- Programs autostart by default
- Program logs
- Included test program
- Backward compatibility with old `"services"` configs

## Repository layout

```txt
mythos-532026-alpha/
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
   └─ mythos_532026_alpha_installer.sh
```

## Install from the release installer

The recommended install method is the release installer.

The installer does not extract Mythos until the EULA is accepted.

```powershell
scp "PATH_TO_INSTALLER\mythos_532026_alpha_installer.sh" root@YOUR_SERVER_IP:/root/
ssh root@YOUR_SERVER_IP
```

Then on the VPS:

```bash
cd /root
chmod +x mythos_532026_alpha_installer.sh
./mythos_532026_alpha_installer.sh
```

When prompted, type:

```txt
ACCEPT
```

## Test Mythos

```bash
cd /root/mythos
./mythos.py version
./mythos.py status
./mythos.py startup-status
./mythos.py pm2-status

./mythos.py make-test
./mythos.py start mythos-test
./mythos.py logs mythos-test
```

## Test boot autostart

```bash
cd /root/mythos
./mythos.py make-test
reboot
```

Reconnect:

```powershell
ssh root@YOUR_SERVER_IP
```

Check it:

```bash
cd /root/mythos
./mythos.py status
./mythos.py logs mythos-test
```

If it worked, `mythos-test` should be running after reboot.

Stop and remove the test:

```bash
./mythos.py stop mythos-test
./mythos.py remove mythos-test
```

## How Mythos programs work

A Mythos **program** is just a command that Mythos can start, stop, and log.

Programs use `autostart: true` by default.

Add a program with autostart enabled:

```bash
./mythos.py add discord-bot "node bot.js" --cwd "/root/my-discord-bot"
```

Add a program without autostart:

```bash
./mythos.py add test-only "python3 test.py" --cwd "/root/test-only" --manual
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
./mythos.py startup-status
```

## PM2 commands

```bash
./mythos.py pm2-status
./mythos.py install-pm2
./mythos.py update-pm2
```
