# 2026-05-22 v0.4.1 窗口适配修正

## 目标

修复 Windows 设置窗口在系统缩放下显得过大、底部内容被截断、次按钮撑破横向布局的问题。

## 改动

- 窗口改为 `400x520`，宽度比 v0.4.0 更收敛，高度足够容纳完整操作区。
- 仅压缩控件缩放，不强行覆盖窗口 DPI 缩放，避免在高 DPI 环境出现截图和布局裁切。
- 底部次按钮设置紧凑固定宽度，避免三个按钮使用默认宽度撑破小窗。
- 新增 `test_windows_gui.py` 锁定窗口尺寸、缩放策略和次按钮宽度。

## 验证

- `python -m unittest test_windows_gui.py test_save_image.py test_macos_save_image.py`
- `python -m py_compile save_image.py windows_gui.py test_windows_gui.py test_save_image.py test_macos_save_image.py macos\save_image_to_link_macos.py macos\install_finder_actions.py`
- GUI smoke test 和布局请求尺寸检查。
