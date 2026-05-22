# 2026-05-22 v0.3 产品化打磨

## 目标

把 Windows 版从脚本控制面板升级为更适合普通用户的设置中心，并补齐品牌图标、快速开始文档和可发布安装包命名。

## 改动范围

- 重做 Windows 设置窗口：快速开始、安装状态、保存目录、复制格式解释、主操作按钮。
- 增加友好错误提示，避免直接暴露 Python 异常。
- 增加 `assets/logo.svg`、`assets/icon.png`、`assets/icon.ico`。
- PyInstaller 打包嵌入 `assets/icon.ico`。
- 增加中英文快速开始文件。

## 验证

- `python -m unittest test_save_image.py test_macos_save_image.py`
- `python -m py_compile save_image.py test_save_image.py test_macos_save_image.py macos\save_image_to_link_macos.py macos\install_finder_actions.py`
- `build_exe.bat`

