SaveImageToLink / 剪贴板图片保存工具

中文说明: README.md
English README: README.en.md

Windows clipboard image saver with a compact settings window and Explorer context menu.
macOS source version with Finder Quick Actions is in macos/.

Usage:
1. Run SaveImageToLink-Setup-Windows-x64.exe.
2. Click 引导 for the step-by-step guide if this is your first time.
3. Choose a save folder and copy format.
4. Click 安装并启用.
5. Copy a screenshot or image.
6. Right-click an Explorer folder background.

Menus:
- 中文版: 保存图片到此处; 保存图片并复制链接
- English: Save image here; Save image and copy link

Default save folder:
%USERPROFILE%\Pictures\SaveImageToLink

Config:
%APPDATA%\SaveImageToLink\config.json

Build from source:
python -m pip install -r requirements-dev.txt
build_exe.bat
