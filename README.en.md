# SaveImageToLink

[中文说明](README.md)

A small local asset tool for clipboard images. Copy a screenshot or image, save it to a folder you control, and copy a reusable local image reference.

## This Is Not A Screenshot Upload Tool

Many AI coding CLIs and chat tools can already accept screenshots directly. If you only need to show an image to AI once, direct upload is usually faster.

SaveImageToLink solves a different problem:

> After a screenshot is copied, where should it live? How should a document reference it? Will you still find it later?

It is for turning clipboard images into stable local assets for README files, Obsidian notes, tutorials, GitHub issues, project logs, and other Markdown workflows.

In short:

- Direct upload solves "show this image once".
- SaveImageToLink solves "save this image locally, reference it, and reuse it later".

The tool works with local files by default. It does not upload images, connect to an image host, or require an account.

## Platform Status

| Platform | Status | Integration |
|----------|--------|-------------|
| Windows 10 / 11 | Implemented, exe build works | Explorer context menu |
| macOS 12+ | Source implemented, package and Quick Actions must be verified on macOS | Finder Quick Actions |

## Features

- Compact modern settings window for save folder, filename prefix, and copy format.
- Built-in guide page explaining the `image` filename prefix, copy formats, and Explorer workflow.
- Windows: one-click install/uninstall for Explorer context-menu entries.
- macOS: Finder Quick Actions installer.
- Default save folder: current user's Pictures folder under `SaveImageToLink`.
- Copy formats: plain path, Markdown image syntax, and file URI.
- Windows exe includes an app icon and bilingual quick-start files.

## Windows Usage

Download `SaveImageToLink-Setup-Windows-x64.exe` and double-click it to open the settings window.

1. If an option is unclear, click `引导` in the top-right corner first.
2. Choose a save folder.
3. Choose a copy format.
4. Click `安装并启用`.
5. Copy a screenshot or image.
6. Right-click the background area of an Explorer folder:
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

The Windows settings window uses `CustomTkinter`. Source users install it through `requirements.txt`; the released exe bundles all required dependencies.

Common commands:

```powershell
python .\save_image.py --install-context-menu
python .\save_image.py --uninstall-context-menu
python .\save_image.py --save-default --copy
python .\save_image.py --save-here "D:\Images"
```

Context-menu language:

```powershell
python .\save_image.py --install-context-menu --menu-language zh-CN
python .\save_image.py --install-context-menu --menu-language en
```

The Chinese build should register Chinese menu labels by default. English builds or English install scripts should use `--menu-language en`. Context-menu labels are no longer bilingual.

## Build The exe

```powershell
python -m pip install -r requirements-dev.txt
.\build_exe.bat
```

Output:

```text
dist\SaveImageToLink.exe
```

## macOS Usage

The macOS source lives in:

```text
macos/
```

Open settings:

```zsh
cd macos
python3 -m pip install -r requirements.txt
python3 save_image_to_link_macos.py --settings
```

Install Finder Quick Actions:

```zsh
python3 install_finder_actions.py
```

Uninstall Finder Quick Actions:

```zsh
python3 install_finder_actions.py --uninstall
```

Build the `.app` on macOS:

```zsh
./build_app.sh
```

See:

```text
macos/README.md
```

## Privacy And Local Data

This tool only reads clipboard images locally and saves them to the folder selected by the user. v1 does not upload images, connect to a remote image host, or include personal paths.

## Language

The Windows exe uses a compact Chinese-first interface to keep the small window clean. English documentation is available in `README.en.md` and `QUICKSTART.en.txt`.

## Development Check

```powershell
python -m unittest test_windows_gui.py test_save_image.py test_macos_save_image.py
```
