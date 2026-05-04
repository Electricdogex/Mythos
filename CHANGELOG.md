# Changelog

## Mythos 532026 Alpha

Date sequence: 5/3/2026

### Added

- Installer now automatically creates `/etc/systemd/system/mythos.service`.
- Installer now enables Mythos startup with `systemctl enable mythos`.
- Installer starts the systemd service after setup.
- Added `./mythos.py startup-status`.
- New programs use `autostart: true` by default.
- `./mythos.py add` now tells the user that autostart is enabled by default.
- Updated README and install directions for startup behavior.

### Notes

PM2 is still installed automatically, but Mythos itself is started on reboot by systemd.

## Mythos 522026 Alpha

Date sequence: 5/2/2026

### Added

- New build naming format: `monthdayyear Alpha`
- EULA-gated release installer
- GitHub-ready repository layout
- Program terminology instead of services
- Program examples in README
- PM2 auto-install through `install.sh`
- Test program
- Backward compatibility for old `"services"` config files
