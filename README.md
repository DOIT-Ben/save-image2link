# SaveImageToLink

[English README](README.en.md)

一个 Windows 剪贴板图片保存小工具：复制截图后，可以通过资源管理器右键菜单把图片保存到指定目录，并自动复制本地图片引用。

## 功能

- 可视化设置保存目录、文件名前缀和复制格式。
- 一键安装/卸载资源管理器右键菜单。
- 默认保存目录为当前用户的 `Pictures\SaveImageToLink`。
- 配置保存到当前用户的 `%APPDATA%\SaveImageToLink\config.json`。
- 右键菜单写入当前用户注册表，不需要管理员权限。
- 支持复制格式：纯路径、Markdown 图片语法、file URI。

## 使用方式

下载 `SaveImageToLink.exe` 后双击打开设置窗口。

1. 选择图片保存目录。
2. 选择复制格式。
3. 点击 `Install context menu`。
4. 复制一张截图或图片。
5. 在资源管理器文件夹空白处右键：
   - `Save image here`：保存到当前文件夹。
   - `Save image and copy link`：保存到设置目录，并复制图片引用。

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

## 隐私与本地数据

本工具只在本机读取剪贴板图片并保存到用户选择的目录。v1 不上传图片，不连接远程图床，不内置任何个人路径。

## 开发验证

```powershell
python -m unittest test_save_image.py
```
