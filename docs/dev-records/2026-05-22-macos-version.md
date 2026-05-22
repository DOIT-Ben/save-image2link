# 2026-05-22 macOS 版本

## 目标

在现有 Windows 版之外新增 macOS 版，使仓库可以同时发布两个平台的小工具。

## 范围

- Windows 版保持现有 `save_image.py`、`SaveImageToLink.exe`、资源管理器右键菜单。
- macOS 版放入 `macos/`，独立实现剪贴板图片保存、配置、设置窗口和 Finder Quick Action 安装脚本。
- macOS 默认保存目录为 `~/Pictures/SaveImageToLink`。
- macOS 配置目录为 `~/Library/Application Support/SaveImageToLink/config.json`。
- 不在 Windows 环境承诺已完成 `.app` 打包和 Finder 真实安装验证。

## 风险

- Finder Quick Action 的真实安装和运行必须在 macOS 上验证。
- macOS 剪贴板读取依赖 Pillow 的 `ImageGrab.grabclipboard()`，不同 macOS 权限设置可能影响表现。
- macOS 发布包需要在 macOS 上使用 PyInstaller 或原生打包工具生成。

## 成功标准

- macOS 版核心函数有单元测试。
- Windows 版测试不回退。
- README 中明确两个平台的支持范围、安装方式和未验证边界。

