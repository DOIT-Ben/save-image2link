# SaveImageToLink

[English README](README.en.md)

一个剪贴板图片本地资产化小工具：复制截图或图片后，把它保存到指定目录，并自动复制可粘贴、可追踪、可复用的本地图片引用。

## 它解决的不是“上传截图”

很多 AI 编码 CLI 和聊天工具现在已经支持直接上传截图。如果只是临时让 AI 看一眼图片，直接上传通常更快。

SaveImageToLink 解决的是另一个问题：

> 截图之后，这张图要保存在哪里？文档里怎么引用？过几天还能不能找到？

它适合把剪贴板图片变成稳定的本地素材，放进 README、Obsidian、教程、GitHub issue、项目复盘或其他 Markdown 工作流里。

简单说：

- 临时上传：解决“这一次让 AI 看见”。
- SaveImageToLink：解决“这张图片以后放哪、怎么引用、怎么复用”。

本工具默认只处理本地文件，不上传图片，不连接图床，也不绑定任何账号。

## 平台状态

| 平台 | 状态 | 集成方式 |
|------|------|----------|
| Windows 10 / 11 | 已实现，可打包 exe | 资源管理器右键菜单 |
| macOS 12+ | 源码已实现，需在 macOS 上打包和验证 | Finder Quick Actions |

## 功能

- 小巧的现代设置窗口，可视化设置保存目录、文件名前缀和复制格式。
- 内置新手引导页，解释 `image` 文件名前缀、三种复制格式和右键保存流程。
- Windows 支持一键安装/卸载资源管理器右键菜单。
- macOS 支持安装 Finder Quick Actions。
- 默认保存目录为当前用户的图片目录下 `SaveImageToLink`。
- 支持复制格式：纯路径、Markdown 图片语法、file URI。
- Windows exe 内置应用图标，并提供中英文快速开始说明。

## Windows 使用方式

下载 `SaveImageToLink-Setup-Windows-x64.exe` 后双击打开设置窗口。

1. 如果不清楚每个选项的含义，先点击窗口右上角 `引导`。
2. 选择图片保存目录。
3. 选择复制格式。
4. 点击 `安装并启用`。
5. 复制一张截图或图片。
6. 在资源管理器文件夹空白处右键：
   - `保存图片到此处`：保存到当前文件夹。
   - `保存图片并复制链接`：保存到设置目录，并复制图片引用。

也可以使用批处理：

```bat
install.bat
uninstall.bat
```

## 从源码运行

```powershell
python -m pip install -r requirements.txt
python .\save_image.py
```

Windows 设置窗口使用 `CustomTkinter`，源码运行时会随 `requirements.txt` 安装；发布版 exe 已内置依赖，普通用户不需要安装 Python。

常用命令：

```powershell
python .\save_image.py --install-context-menu
python .\save_image.py --uninstall-context-menu
python .\save_image.py --save-default --copy
python .\save_image.py --save-here "D:\Images"
```

右键菜单语言：

```powershell
python .\save_image.py --install-context-menu --menu-language zh-CN
python .\save_image.py --install-context-menu --menu-language en
```

中文版本默认注册中文菜单；英文版本或英文安装脚本应使用 `--menu-language en`。右键菜单不会再同时显示中英文。

## 打包 exe

```powershell
python -m pip install -r requirements-dev.txt
.\build_exe.bat
```

生成文件：

```text
dist\SaveImageToLink.exe
```

## macOS 使用方式

macOS 版本源码在：

```text
macos/
```

运行设置窗口：

```zsh
cd macos
python3 -m pip install -r requirements.txt
python3 save_image_to_link_macos.py --settings
```

安装 Finder Quick Actions：

```zsh
python3 install_finder_actions.py
```

卸载 Finder Quick Actions：

```zsh
python3 install_finder_actions.py --uninstall
```

打包 `.app` 需要在 macOS 上执行：

```zsh
./build_app.sh
```

详见：

```text
macos/README.md
```

## 隐私与本地数据

本工具只在本机读取剪贴板图片并保存到用户选择的目录。v1 不上传图片，不连接远程图床，不内置任何个人路径。

## 语言

Windows exe 的设置界面以中文为主，避免小窗口信息过载；英文说明保留在 `README.en.md` 和 `QUICKSTART.en.txt`。

## 开发验证

```powershell
python -m unittest test_windows_gui.py test_save_image.py test_macos_save_image.py
```
