# SaveImageToLink

[中文说明](README.md)

A small Windows clipboard image saver. Copy a screenshot or image, then use the Explorer context menu to save it to a folder and copy a local image reference.

## Features

- Visual settings window for save folder, filename prefix, and copy format.
- One-click install/uninstall for Explorer context-menu entries.
- Default save folder: current user's `Pictures\SaveImageToLink`.
- User config: `%APPDATA%\SaveImageToLink\config.json`.
- Context menu is installed under the current user registry hive, so admin permission is not required.
- Copy formats: plain path, Markdown image syntax, and file URI.

## Usage

Download `SaveImageToLink.exe` and double-click it to open the settings window.

1. Choose a save folder.
2. Choose a copy format.
3. Click `Install context menu`.
4. Copy a screenshot or image.
5. Right-click the background area of an Explorer folder:
   - `Save image here`: save the image to the current folder.
   - `Save image and copy link`: save the image to the configured folder and copy the image reference.

You can also use the batch files:

```bat
install.bat
uninstall.bat
```

## Run From Source

```powershell
python -m pip install -r requirements.txt
python .\save_image.py
```

Common commands:

```powershell
python .\save_image.py --install-context-menu
python .\save_image.py --uninstall-context-menu
python .\save_image.py --save-default --copy
python .\save_image.py --save-here "D:\Images"
```

## Build The exe

```powershell
python -m pip install -r requirements-dev.txt
.\build_exe.bat
```

Output:

```text
dist\SaveImageToLink.exe
```

## Privacy And Local Data

This tool only reads clipboard images locally and saves them to the folder selected by the user. v1 does not upload images, connect to a remote image host, or include personal paths.

## Development Check

```powershell
python -m unittest test_save_image.py
```

