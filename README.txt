SaveImageToLink / 剪贴板图片保存工具

中文说明: README.md
English README: README.en.md

Windows clipboard image saver with an Explorer context menu.

Usage:
1. Run SaveImageToLink.exe.
2. Choose a save folder and copy format.
3. Click Install context menu.
4. Copy a screenshot or image.
5. Right-click an Explorer folder background.

Menus:
- Save image here
- Save image and copy link

Default save folder:
%USERPROFILE%\Pictures\SaveImageToLink

Config:
%APPDATA%\SaveImageToLink\config.json

Build from source:
python -m pip install -r requirements-dev.txt
build_exe.bat
