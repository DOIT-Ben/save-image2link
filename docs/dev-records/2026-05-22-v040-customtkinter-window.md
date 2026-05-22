# 2026-05-22 v0.4.0 CustomTkinter 小窗

## 目标

把 Windows 设置窗口从原生 Tkinter 替换为更小巧、现代、可发布的 CustomTkinter 界面，同时保持核心保存逻辑、右键菜单和配置路径不变。

## 改动

- 新增 `windows_gui.py`，承载 Windows 可视化设置窗口。
- `save_image.py` 继续作为 CLI、右键菜单和核心保存入口，只在打开设置窗口时加载 GUI。
- 复制格式选项改为中文紧凑标签，避免控件内中英文堆叠。
- 新增 `customtkinter` 运行依赖。
- 更新 PyInstaller 打包脚本，收集 CustomTkinter 和应用图标资源。
- 更新中英文 README、Quickstart 和根说明文件。

## 验证

- 已新增并执行界面文案映射测试。
- 已执行全量单元测试和 `py_compile`。
- 已执行 GUI 构建 smoke test。
