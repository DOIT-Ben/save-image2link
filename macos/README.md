# SaveImageToLink for macOS

macOS implementation of SaveImageToLink. It saves clipboard images to a user-selected folder and copies a local image reference.

## Status

This macOS version is source-ready, but the `.app` package and Finder Quick Actions must be built and verified on macOS.

## Requirements

- macOS 12 or newer is recommended.
- Python 3.10 or newer.
- Pillow.

## Install From Source

```zsh
cd macos
python3 -m pip install -r requirements.txt
python3 save_image_to_link_macos.py --settings
```

## Finder Quick Actions

Install Quick Actions:

```zsh
python3 install_finder_actions.py
```

Uninstall Quick Actions:

```zsh
python3 install_finder_actions.py --uninstall
```

The installer writes Automator workflows to:

```text
~/Library/Services
```

After installation, Finder should show:

- `Save Image and Copy Link`
- `Save Image to Selected Folder`

If they do not appear immediately, restart Finder:

```zsh
killall Finder
```

## Commands

```zsh
python3 save_image_to_link_macos.py --save-default --copy
python3 save_image_to_link_macos.py --save-here "$HOME/Desktop" --copy
python3 save_image_to_link_macos.py --settings
```

## Build The App

Build on macOS:

```zsh
python3 -m pip install Pillow pyinstaller
./build_app.sh
```

Output:

```text
macos/dist/SaveImageToLink.app
```

## Data Location

Default save folder:

```text
~/Pictures/SaveImageToLink
```

Config:

```text
~/Library/Application Support/SaveImageToLink/config.json
```
