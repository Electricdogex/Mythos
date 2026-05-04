# Mythos 532026 Alpha Install Directions

This explains how to install **Mythos 532026 Alpha** on an Ubuntu VPS.

## What you need

- An Ubuntu VPS
- SSH access to the VPS
- The Mythos release installer file:

```txt
mythos_532026_alpha_installer.sh
```

The installer is located in the repo here:

```txt
release/mythos_532026_alpha_installer.sh
```

## Replace the placeholders

Replace `YOUR_SERVER_IP` with your VPS IP address.

Replace `PATH_TO_INSTALLER` with the location of `mythos_532026_alpha_installer.sh` on your computer.

## Step 1: Upload the installer to your VPS

On your computer, open **PowerShell**.

```powershell
scp "PATH_TO_INSTALLER\mythos_532026_alpha_installer.sh" root@YOUR_SERVER_IP:/root/
```

Example:

```powershell
scp "C:\Users\YourName\Downloads\mythos-532026-alpha\release\mythos_532026_alpha_installer.sh" root@YOUR_SERVER_IP:/root/
```

## Step 2: Connect to your VPS

```powershell
ssh root@YOUR_SERVER_IP
```

## Step 3: Run the Mythos installer

```bash
cd /root
chmod +x mythos_532026_alpha_installer.sh
./mythos_532026_alpha_installer.sh
```

## Step 4: Accept the EULA

Type this exactly:

```txt
ACCEPT
```

Then press **Enter**.

## Step 5: Check that Mythos installed

```bash
cd /root/mythos
./mythos.py version
./mythos.py status
./mythos.py startup-status
./mythos.py pm2-status
```

## Step 6: Confirm startup was enabled

```bash
systemctl is-enabled mythos
systemctl status mythos
```

You should see that `mythos` is enabled.

## Step 7: Test Mythos

```bash
./mythos.py make-test
./mythos.py start mythos-test
./mythos.py logs mythos-test
```

## Step 8: Test reboot autostart

```bash
reboot
```

Reconnect:

```powershell
ssh root@YOUR_SERVER_IP
```

Check Mythos:

```bash
cd /root/mythos
./mythos.py status
./mythos.py logs mythos-test
```

## Step 9: Stop the test program

```bash
./mythos.py stop mythos-test
./mythos.py remove mythos-test
```

## Add a program

Autostart is enabled by default:

```bash
./mythos.py add program-name "command here" --cwd "/path/to/program/folder"
```

Manual/no boot autostart:

```bash
./mythos.py add program-name "command here" --cwd "/path/to/program/folder" --manual
```
