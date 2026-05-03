# Mythos Install Directions

This explains how to install **Mythos 522026 Alpha** on an Ubuntu VPS.

## What you need

You need:

- An Ubuntu VPS
- SSH access to the VPS
- The Mythos release installer file:

```txt
mythos_522026_alpha_installer.sh
```

The installer is located in the repo here:

```txt
release/mythos_522026_alpha_installer.sh
```

## Replace the placeholders

Anywhere you see this:

```txt
YOUR_SERVER_IP
```

replace it with your VPS IP address.

Anywhere you see this:

```txt
PATH_TO_INSTALLER
```

replace it with the location of `mythos_522026_alpha_installer.sh` on your computer.

Example Windows path:

```txt
C:\Users\YourName\Downloads\mythos_522026_alpha_installer.sh
```

## Step 1: Upload the installer to your VPS

On your computer, open **PowerShell**.

Run:

```powershell
scp "PATH_TO_INSTALLER\mythos_522026_alpha_installer.sh" root@YOUR_SERVER_IP:/root/
```

Example:

```powershell
scp "C:\Users\YourName\Downloads\mythos_522026_alpha_installer.sh" root@YOUR_SERVER_IP:/root/
```

If the installer is inside the downloaded repo folder, the path may look like this:

```powershell
scp "C:\Users\YourName\Downloads\mythos-522026-alpha\release\mythos_522026_alpha_installer.sh" root@YOUR_SERVER_IP:/root/
```

## Step 2: Connect to your VPS

In PowerShell, run:

```powershell
ssh root@YOUR_SERVER_IP
```

## Step 3: Run the Mythos installer

Once you are inside the VPS terminal, run:

```bash
cd /root
chmod +x mythos_522026_alpha_installer.sh
./mythos_522026_alpha_installer.sh
```

## Step 4: Accept the EULA

The installer will show the Mythos EULA.

To continue installing, type this exactly:

```txt
ACCEPT
```

Then press **Enter**.

If you type anything else, Mythos will not install.

## Step 5: Check that Mythos installed

After the installer finishes, run:

```bash
cd /root/mythos
./mythos.py version
./mythos.py status
./mythos.py pm2-status
```

If everything worked, Mythos should say something like:

```txt
Mythos 522026 Alpha
No programs configured yet.
```

An empty PM2 table is normal.

## Step 6: Test Mythos

Run:

```bash
./mythos.py make-test
./mythos.py start mythos-test
./mythos.py logs mythos-test
```

You should see heartbeat messages.

## Step 7: Stop the test program

Run:

```bash
./mythos.py stop mythos-test
./mythos.py remove mythos-test
```

Mythos is now installed and ready.

## Where Mythos is installed

The installer puts Mythos here:

```txt
/root/mythos
```

## Most useful commands

Check version:

```bash
./mythos.py version
```

See programs:

```bash
./mythos.py list
```

Start all programs:

```bash
./mythos.py start
```

Stop all programs:

```bash
./mythos.py stop
```

View logs for a program:

```bash
./mythos.py logs program-name
```

Add a program:

```bash
./mythos.py add program-name "command here" --cwd "/path/to/program/folder"
```
