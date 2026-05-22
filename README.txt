SaveImageToLink / 剪贴板图片保存工具

中文说明: README.md
English README: README.en.md

Windows clipboard image saver with a compact settings window and Explorer context menu.
macOS source version with Finder Quick Actions is in macos/.

Usage:
1. Run SaveImageToLink-Setup-Windows-x64.exe.
2. Choose a save folder and copy format.
3. Click 安装并启用.
4. Copy a screenshot or image.
5. Right-click an Explorer folder background.

Menus:
- 保存图片到此处 / Save image here
- 保存图片并复制链接 / Save image and copy link

Default save folder:
%USERPROFILE%\Pictures\SaveImageToLink

Config:
%APPDATA%\SaveImageToLink\config.json

Build from source:
python -m pip install -r requirements-dev.txt
build_exe.bat
