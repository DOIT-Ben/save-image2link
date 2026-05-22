# 2026-05-22 v0.3.1 极简小窗

## 目标

把 v0.3 的大设置中心收敛为更小巧的 Windows 设置窗口，减少第一屏信息量。

## 改动

- 设置窗口固定为约 `420x430`。
- 主界面改为中文优先，英文保留在文档中。
- 去掉左侧步骤面板和双栏布局。
- 保留最小功能：安装状态、保存目录、复制格式、文件名前缀、安装、测试、打开目录、卸载。
- 文档同步说明中文主界面和英文文档入口。

## 验证

- `python -m unittest test_save_image.py test_macos_save_image.py`
- `python -m py_compile save_image.py test_save_image.py test_macos_save_image.py macos\save_image_to_link_macos.py macos\install_finder_actions.py`

