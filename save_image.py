"""Save clipboard images and manage Windows Explorer context-menu entries."""
from __future__ import annotations

import argparse
import base64
import ctypes
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image


APP_NAME = "SaveImageToLink"
SCRIPT_DIR = Path(__file__).resolve().parent
RESULT_FILE = SCRIPT_DIR / "_last_result.txt"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tif", ".tiff"}
COPY_FORMATS = {"path", "markdown", "file_uri"}
MENU_LANGUAGES = {"zh-CN", "en"}
MENU_LANGUAGE_ALIASES = {
    "zh": "zh-CN",
    "zh_cn": "zh-CN",
    "zh-cn": "zh-CN",
    "cn": "zh-CN",
    "chinese": "zh-CN",
    "en": "en",
    "en_us": "en",
    "en-us": "en",
    "english": "en",
}
MENU_LABELS = {
    "zh-CN": {
        "here": "保存图片到此处",
        "default": "保存图片并复制链接",
    },
    "en": {
        "here": "Save image here",
        "default": "Save image and copy link",
    },
}
TEXT = {
    "window_title": "保存图片链接 / SaveImageToLink",
    "save_folder": "保存目录 / Save folder",
    "browse": "选择 / Browse",
    "copy_format": "复制格式 / Copy format",
    "filename_prefix": "文件名前缀 / Filename prefix",
    "save_settings": "保存设置 / Save",
    "open_folder": "打开目录 / Open",
    "restore_default": "恢复默认 / Default",
    "install_menu": "安装右键菜单 / Install menu",
    "uninstall_menu": "卸载右键菜单 / Uninstall menu",
    "test_save": "测试保存 / Test",
    "saved": "图片已保存 / Image saved",
    "saved_link": "图片已保存并复制链接 / Image saved and link copied",
    "failed": "保存图片失败 / Save image failed",
    "settings_saved": "设置已保存 / Settings saved",
    "menu_installed": "右键菜单已安装 / Context menu installed.",
    "menu_removed": "右键菜单已卸载 / Context menu removed.",
    "status_ready": "已准备就绪 / Ready",
    "status_installed": "右键菜单已安装 / Context menu installed",
    "status_not_installed": "右键菜单未安装 / Context menu not installed",
    "status_saved": "最近保存 / Last saved",
    "status_waiting": "等待复制图片或截图 / Waiting for an image on clipboard",
    "step_1": "1. 选择保存目录",
    "step_2": "2. 选择复制格式",
    "step_3": "3. 安装右键菜单",
    "step_4": "4. 复制图片后右键保存",
    "quick_start": "快速开始 / Quick start",
    "why_format": "选择不同格式会影响你粘贴到文档里的样子。",
    "path_hint": "适合本地脚本和文件管理器。",
    "markdown_hint": "适合 Obsidian、Markdown 笔记和文档。",
    "uri_hint": "适合网页、HTML 和支持 file:// 的工具。",
    "no_image": "剪贴板里没有图片，请先复制截图或图片。\nNo image found in clipboard. Copy a screenshot or image first.",
    "not_writable": "这个保存目录无法写入，请换一个文件夹。\nThis save folder cannot be written to. Choose another folder.",
    "copy_failed": "复制链接失败，请检查剪贴板是否可用。\nFailed to copy link. Please check clipboard access.",
}
MENU_KEYS = {
    "here": r"Software\Classes\Directory\Background\shell\SaveImageToLinkHere",
    "default": r"Software\Classes\Directory\Background\shell\SaveImageToLinkDefault",
}
LEGACY_MENU_KEYS = [
    r"Software\Classes\Directory\Background\shell\SaveImageToCopyimg",
    r"Software\Classes\Directory\Background\shell\SaveImageToFolder",
    r"Software\Classes\Directory\Background\shell\SaveImageToLink",
]


def default_save_dir(home: Path | None = None) -> Path:
    return (home or Path.home()) / "Pictures" / APP_NAME


def config_dir(appdata: str | None = None, home: Path | None = None) -> Path:
    base = appdata or os.environ.get("APPDATA")
    if base:
        return Path(base) / APP_NAME
    return (home or Path.home()) / "AppData" / "Roaming" / APP_NAME


def default_config(home: Path | None = None) -> dict[str, str]:
    return {
        "save_dir": str(default_save_dir(home=home)),
        "copy_format": "markdown",
        "filename_prefix": "image",
        "menu_language": "zh-CN",
        "guide_seen": "0",
    }


def normalize_menu_language(value: str | None) -> str:
    normalized = (value or "").strip().lower().replace(" ", "").replace("_", "-")
    return MENU_LANGUAGE_ALIASES.get(normalized, "zh-CN")


def normalize_config(raw: dict[str, Any] | None, home: Path | None = None) -> dict[str, str]:
    config = default_config(home=home)
    if isinstance(raw, dict):
        config.update({key: str(value) for key, value in raw.items() if value is not None})

    if config.get("copy_format") not in COPY_FORMATS:
        config["copy_format"] = "markdown"
    prefix = "".join(ch for ch in config.get("filename_prefix", "image") if ch.isalnum() or ch in "-_").strip("_-")
    config["filename_prefix"] = prefix or "image"
    config["menu_language"] = normalize_menu_language(config.get("menu_language"))
    config["guide_seen"] = "1" if str(config.get("guide_seen", "0")).strip().lower() in {"1", "true", "yes"} else "0"
    config["save_dir"] = str(Path(config["save_dir"]).expanduser())
    return config


def load_config(config_file: Path | None = None, home: Path | None = None) -> dict[str, str]:
    path = config_file or config_dir(home=home) / "config.json"
    if not path.exists():
        return normalize_config({}, home=home)
    try:
        return normalize_config(json.loads(path.read_text(encoding="utf-8")), home=home)
    except Exception:
        return normalize_config({}, home=home)


def save_config(config: dict[str, Any], config_file: Path | None = None) -> Path:
    path = config_file or config_dir() / "config.json"
    normalized = normalize_config(config)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    Path(normalized["save_dir"]).mkdir(parents=True, exist_ok=True)
    return path


def copy_format_options() -> list[dict[str, str]]:
    return [
        {
            "value": "markdown",
            "label": "Markdown 图片（推荐）",
            "description": "适合 Obsidian、Markdown 笔记和文档。",
        },
        {
            "value": "path",
            "label": "纯路径",
            "description": "适合脚本、本地打开和文件管理器。",
        },
        {
            "value": "file_uri",
            "label": "文件链接 file://",
            "description": "适合网页、HTML 和支持 file:// 的工具。",
        },
    ]


def copy_format_label(value: str) -> str:
    for item in copy_format_options():
        if item["value"] == value:
            return item["label"]
    return value


def friendly_error_message(exc: Exception) -> str:
    message = str(exc)
    low = message.lower()
    if "no image in clipboard" in low or "clipboard does not contain an image" in low:
        return TEXT["no_image"]
    if "not writable" in low:
        return TEXT["not_writable"]
    if "failed to open clipboard" in low or "failed to set clipboard text" in low:
        return TEXT["copy_failed"]
    return message


def get_clipboard_image():
    try:
        from PIL import ImageGrab
    except Exception as exc:
        raise RuntimeError("PIL ImageGrab is not available: " + str(exc)) from exc

    return ImageGrab.grabclipboard()


def load_image_from_file(filepath: Path) -> Image.Image | None:
    try:
        with Image.open(filepath) as img:
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGBA" if "A" in img.getbands() else "RGB")
            return img.copy()
    except Exception:
        return None


def set_clipboard_text(text: str) -> None:
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    user32.OpenClipboard.argtypes = [ctypes.c_void_p]
    user32.EmptyClipboard.argtypes = []
    user32.CloseClipboard.argtypes = []
    user32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]
    kernel32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
    kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalFree.argtypes = [ctypes.c_void_p]
    kernel32.GlobalAlloc.restype = ctypes.c_void_p
    kernel32.GlobalLock.restype = ctypes.c_void_p
    user32.SetClipboardData.restype = ctypes.c_void_p
    cf_unicode_text = 13
    gmem_moveable = 0x0002

    data = text.encode("utf-16le") + b"\x00\x00"
    opened = False
    for _ in range(20):
        if user32.OpenClipboard(None):
            opened = True
            break
        time.sleep(0.05)

    if not opened:
        raise RuntimeError("Failed to open clipboard")

    try:
        if not user32.EmptyClipboard():
            raise RuntimeError("Failed to clear clipboard")
        handle = kernel32.GlobalAlloc(gmem_moveable, len(data))
        if not handle:
            raise RuntimeError("Failed to allocate clipboard memory")
        locked = kernel32.GlobalLock(handle)
        if not locked:
            kernel32.GlobalFree(handle)
            raise RuntimeError("Failed to lock clipboard memory")
        ctypes.memmove(locked, data, len(data))
        kernel32.GlobalUnlock(handle)
        if not user32.SetClipboardData(cf_unicode_text, handle):
            kernel32.GlobalFree(handle)
            raise RuntimeError("Failed to set clipboard text")
    finally:
        user32.CloseClipboard()


def ps_quote(value: str) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def show_notification(title: str, message: str, is_error: bool = False) -> None:
    if os.name != "nt":
        return
    icon_name = "Error" if is_error else "Information"
    tip_icon = "Error" if is_error else "Info"
    script = f"""
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$notify = New-Object System.Windows.Forms.NotifyIcon
$notify.Icon = [System.Drawing.SystemIcons]::{icon_name}
$notify.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::{tip_icon}
$notify.BalloonTipTitle = {ps_quote(title)}
$notify.BalloonTipText = {ps_quote(message)}
$notify.Visible = $true
$notify.ShowBalloonTip(3500)
Start-Sleep -Milliseconds 4200
$notify.Dispose()
"""
    encoded = base64.b64encode(script.encode("utf-16le")).decode("ascii")
    subprocess.Popen(
        [
            "powershell.exe",
            "-NoProfile",
            "-WindowStyle",
            "Hidden",
            "-ExecutionPolicy",
            "Bypass",
            "-EncodedCommand",
            encoded,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


def format_clipboard_text(filepath: Path, config: dict[str, Any]) -> str:
    fmt = config.get("copy_format", "markdown")
    path_text = str(filepath)
    if fmt == "path":
        return path_text
    if fmt == "file_uri":
        return filepath.resolve().as_uri()
    return f"![]({path_text})"


def image_from_clipboard() -> Image.Image:
    img = get_clipboard_image()
    if img is None:
        raise RuntimeError("No image in clipboard")

    if isinstance(img, list) and img:
        for file_path in img:
            path = Path(file_path)
            if path.exists() and path.suffix.lower() in IMAGE_EXTENSIONS:
                loaded = load_image_from_file(path)
                if loaded:
                    return loaded
        raise RuntimeError("No valid image file in clipboard")

    if not isinstance(img, Image.Image):
        raise RuntimeError("Clipboard does not contain an image")
    return img


def ensure_writable_folder(folder: Path) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    probe = folder / ".save-image-to-link-write-test"
    try:
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
    except OSError as exc:
        raise RuntimeError(f"Target folder is not writable: {folder}") from exc
    return folder


def save_clipboard_image(
    target_folder: str | Path | None = None,
    copy_link: bool = False,
    config: dict[str, Any] | None = None,
    notify: bool = True,
) -> str:
    active_config = normalize_config(config or load_config())
    folder = Path(target_folder or active_config["save_dir"]).expanduser()
    ensure_writable_folder(folder)

    img = image_from_clipboard()
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA" if "A" in img.getbands() else "RGB")

    filename = f"{active_config['filename_prefix']}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
    filepath = folder / filename
    img.save(filepath, "PNG")
    saved_path = str(filepath)

    if copy_link:
        text = format_clipboard_text(filepath, active_config)
        set_clipboard_text(text)
        if notify:
            show_notification(TEXT["saved_link"], text, is_error=False)
    elif notify:
        show_notification(TEXT["saved"], saved_path, is_error=False)
    return saved_path


def executable_command_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable)
    return Path(__file__).resolve()


def quote_cmd(value: str | Path) -> str:
    return '"' + str(value).replace('"', r'\"') + '"'


def build_context_menu_commands(program: Path | None = None) -> dict[str, str]:
    target = program or executable_command_path()
    if getattr(sys, "frozen", False) or target.suffix.lower() == ".exe":
        prefix = quote_cmd(target)
    else:
        prefix = quote_cmd(sys.executable) + " " + quote_cmd(target)
    return {
        "here": f'{prefix} --save-here "%V"',
        "default": f"{prefix} --save-default --copy",
    }


def context_menu_labels(menu_language: str | None = None) -> dict[str, str]:
    return MENU_LABELS[normalize_menu_language(menu_language)].copy()


def install_context_menu(program: Path | None = None, menu_language: str | None = None) -> None:
    if os.name != "nt":
        raise RuntimeError("Context menu installation is only supported on Windows")
    import winreg

    commands = build_context_menu_commands(program)
    labels = context_menu_labels(menu_language or load_config().get("menu_language"))
    entries = {
        "here": (labels["here"], commands["here"]),
        "default": (labels["default"], commands["default"]),
    }
    for name, (label, command) in entries.items():
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, MENU_KEYS[name]) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, label)
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, str(program or executable_command_path()))
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, MENU_KEYS[name] + r"\command") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, command)


def is_context_menu_installed() -> bool:
    if os.name != "nt":
        return False
    import winreg

    for key in MENU_KEYS.values():
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key + r"\command"):
                pass
        except FileNotFoundError:
            return False
    return True


def delete_reg_tree(root, subkey: str) -> None:
    import winreg

    try:
        with winreg.OpenKey(root, subkey, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
            while True:
                try:
                    child = winreg.EnumKey(key, 0)
                except OSError:
                    break
                delete_reg_tree(root, subkey + "\\" + child)
        winreg.DeleteKey(root, subkey)
    except FileNotFoundError:
        return


def uninstall_context_menu() -> None:
    if os.name != "nt":
        raise RuntimeError("Context menu uninstall is only supported on Windows")
    import winreg

    for key in [*MENU_KEYS.values(), *LEGACY_MENU_KEYS]:
        delete_reg_tree(winreg.HKEY_CURRENT_USER, key)


def open_settings_window() -> None:
    from windows_gui import open_settings_window as open_windows_settings_window

    open_windows_settings_window()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Save clipboard image and copy a local image link.")
    parser.add_argument("target", nargs="?", help="Target folder from Explorer right-click.")
    parser.add_argument("--save-here", help="Save clipboard image to this folder.")
    parser.add_argument("--save-default", action="store_true", help="Save clipboard image to configured folder.")
    parser.add_argument("--copy", "--copy-path", dest="copy", action="store_true", help="Copy formatted link to clipboard.")
    parser.add_argument("--copy-format", choices=sorted(COPY_FORMATS), help="Override configured copy format.")
    parser.add_argument(
        "--menu-language",
        help="Context-menu language for installation: zh-CN/zh or en/en-US.",
    )
    parser.add_argument("--install-context-menu", action="store_true", help="Install Explorer context-menu entries.")
    parser.add_argument("--uninstall-context-menu", action="store_true", help="Uninstall Explorer context-menu entries.")
    parser.add_argument("--settings", action="store_true", help="Open the visual settings window.")
    parser.add_argument("--temp", action="store_true", help="Compatibility alias for --save-default.")
    parser.add_argument("--no-notify", action="store_true", help="Disable Windows notification balloon.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> str | None:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    config = load_config()
    if args.copy_format:
        config["copy_format"] = args.copy_format
    if args.menu_language:
        config["menu_language"] = normalize_menu_language(args.menu_language)

    if args.install_context_menu:
        if args.menu_language:
            save_config(config)
        install_context_menu(menu_language=config["menu_language"])
        return "context-menu-installed"
    if args.uninstall_context_menu:
        uninstall_context_menu()
        return "context-menu-uninstalled"
    if args.settings or not any([args.save_here, args.save_default, args.temp, args.target]):
        open_settings_window()
        return None

    target = args.save_here or args.target
    if args.save_default or args.temp:
        target = config["save_dir"]
    return save_clipboard_image(target_folder=target, copy_link=args.copy, config=config, notify=not args.no_notify)


if __name__ == "__main__":
    try:
        result = main()
        if result:
            RESULT_FILE.write_text("OK:" + result, encoding="utf-8")
    except Exception as exc:
        message = str(exc)
        RESULT_FILE.write_text("ERROR:" + message, encoding="utf-8")
        show_notification(TEXT["failed"], message, is_error=True)
        raise
