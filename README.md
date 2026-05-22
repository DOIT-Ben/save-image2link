# SaveImageToLink

[English README](README.en.md)

一个剪贴板图片保存小工具：复制截图后，把图片保存到指定目录，并自动复制本地图片引用。

## 平台状态

| 平台 | 状态 | 集成方式 |
|------|------|----------|
| Windows 10 / 11 | 已实现，可打包 exe | 资源管理器右键菜单 |
| macOS 12+ | 源码已实现，需在 macOS 上打包和验证 | Finder Quick Actions |

## 功能

- 可视化设置保存目录、文件名前缀和复制格式。
- Windows 支持一键安装/卸载资源管理器右键菜单。
- macOS 支持安装 Finder Quick Actions。
- 默认保存目录为当前用户的图片目录下 `SaveImageToLink`。
- 支持复制格式：纯路径、Markdown 图片语法、file URI。

## Windows 使用方式

下载 `SaveImageToLink.exe` 后双击打开设置窗口。

1. 选择图片保存目录。
2. 选择复制格式。
3. 点击 `安装右键菜单 / Install menu`。
4. 复制一张截图或图片。
5. 在资源管理器文件夹空白处右键：
   - `保存图片到此处 / Save image here`：保存到当前文件夹。
   - `保存图片并复制链接 / Save image and copy link`：保存到设置目录，并复制图片引用。

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

常用命令：

```powershell
python .\save_image.py --install-context-menu
python .\save_image.py --uninstall-context-menu
python .\save_image.py --save-default --copy
python .\save_image.py --save-here "D:\Images"
```

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

Windows exe 的设置界面、通知和右键菜单使用中英双语文案。文档提供中文 `README.md` 和英文 `README.en.md` 两版。

## 开发验证

```powershell
python -m unittest test_save_image.py test_macos_save_image.py
```
