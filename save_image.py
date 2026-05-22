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
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image


APP_NAME = "SaveImageToLink"
SCRIPT_DIR = Path(__file__).resolve().parent
RESULT_FILE = SCRIPT_DIR / "_last_result.txt"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tif", ".tiff"}
COPY_FORMATS = {"path", "markdown", "file_uri"}
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
    "menu_here": "保存图片到此处 / Save image here",
    "menu_default": "保存图片并复制链接 / Save image and copy link",
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
    }


def normalize_config(raw: dict[str, Any] | None, home: Path | None = None) -> dict[str, str]:
    config = default_config(home=home)
    if isinstance(raw, dict):
        config.update({key: str(value) for key, value in raw.items() if value is not None})

    if config.get("copy_format") not in COPY_FORMATS:
        config["copy_format"] = "markdown"
    prefix = "".join(ch for ch in config.get("filename_prefix", "image") if ch.isalnum() or ch in "-_").strip("_-")
    config["filename_prefix"] = prefix or "image"
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
            "label": "Markdown 图片 / Markdown image",
            "description": "推荐 / Recommended. 适合笔记和文档。",
        },
        {
            "value": "path",
            "label": "纯路径 / Plain path",
            "description": "适合脚本、本地打开和文件管理器。",
        },
        {
            "value": "file_uri",
            "label": "文件链接 / File URI",
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


def install_context_menu(program: Path | None = None) -> None:
    if os.name != "nt":
        raise RuntimeError("Context menu installation is only supported on Windows")
    import winreg

    commands = build_context_menu_commands(program)
    entries = {
        "here": (TEXT["menu_here"], commands["here"]),
        "default": (TEXT["menu_default"], commands["default"]),
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
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    config = load_config()
    root = tk.Tk()
    root.title(TEXT["window_title"])
    root.geometry("420x430")
    root.resizable(False, False)
    root.configure(bg="#ffffff")
    icon_path = SCRIPT_DIR / "assets" / "icon.ico"
    if icon_path.exists():
        try:
            root.iconbitmap(str(icon_path))
        except Exception:
            pass

    save_dir_var = tk.StringVar(value=config["save_dir"])
    format_items = [
        ("Markdown 图片（推荐）", "markdown", "适合 Obsidian 和 Markdown 文档。"),
        ("纯路径", "path", "复制本地文件路径。"),
        ("文件链接 file://", "file_uri", "复制标准文件链接。"),
    ]
    label_to_format = {label: value for label, value, _hint in format_items}
    format_to_label = {value: label for label, value, _hint in format_items}
    format_hints = {value: hint for _label, value, hint in format_items}
    format_var = tk.StringVar(value=format_to_label.get(config["copy_format"], format_to_label["markdown"]))
    format_hint_var = tk.StringVar(value="")
    prefix_var = tk.StringVar(value=config["filename_prefix"])
    install_status_var = tk.StringVar(value="")
    result_var = tk.StringVar(value="复制截图后，在文件夹空白处右键保存。")

    font_title = ("Segoe UI", 19, "bold")
    font_body = ("Segoe UI", 10)
    font_label = ("Segoe UI", 10, "bold")
    font_small = ("Segoe UI", 9)

    def selected_copy_format() -> str:
        return label_to_format.get(format_var.get(), "markdown")

    def update_format_description(*_args: Any) -> None:
        format_hint_var.set(format_hints.get(selected_copy_format(), format_hints["markdown"]))

    def refresh_install_status() -> None:
        install_status_var.set("右键菜单已安装" if is_context_menu_installed() else "右键菜单未安装")

    def choose_folder() -> None:
        selected = filedialog.askdirectory(initialdir=save_dir_var.get() or str(default_save_dir()))
        if selected:
            save_dir_var.set(selected)

    def current_config() -> dict[str, str]:
        return normalize_config(
            {
                "save_dir": save_dir_var.get(),
                "copy_format": selected_copy_format(),
                "filename_prefix": prefix_var.get(),
            }
        )

    def save_settings() -> None:
        try:
            save_config(current_config())
            result_var.set("设置已保存。")
            return True
        except Exception as exc:
            messagebox.showerror(APP_NAME, friendly_error_message(exc))
            return False

    def open_folder() -> None:
        try:
            cfg = current_config()
            Path(cfg["save_dir"]).mkdir(parents=True, exist_ok=True)
            webbrowser.open(str(Path(cfg["save_dir"])))
        except Exception as exc:
            messagebox.showerror(APP_NAME, friendly_error_message(exc))

    def reset_default() -> None:
        save_dir_var.set(str(default_save_dir()))

    def install_menu() -> None:
        try:
            if not save_settings():
                return
            install_context_menu()
            refresh_install_status()
            result_var.set("已安装。复制图片后，在文件夹空白处右键使用。")
        except Exception as exc:
            messagebox.showerror(APP_NAME, friendly_error_message(exc))

    def uninstall_menu() -> None:
        try:
            uninstall_context_menu()
            refresh_install_status()
            result_var.set("右键菜单已卸载。")
        except Exception as exc:
            messagebox.showerror(APP_NAME, friendly_error_message(exc))

    def test_save() -> None:
        try:
            if not save_settings():
                return
            result = save_clipboard_image(copy_link=True, config=current_config())
            result_var.set(f"已保存：{result}")
        except Exception as exc:
            messagebox.showerror(APP_NAME, friendly_error_message(exc))

    root.columnconfigure(0, weight=1)

    titlebar = tk.Frame(root, bg="#fbfbfd", height=40, highlightthickness=0)
    titlebar.grid(row=0, column=0, sticky="ew")
    titlebar.grid_propagate(False)
    titlebar.columnconfigure(0, weight=1)
    tk.Label(titlebar, text="SaveImageToLink", bg="#fbfbfd", fg="#6e6e73", font=("Segoe UI", 9, "bold")).grid(
        row=0, column=0, sticky="w", padx=18, pady=11
    )

    frame = tk.Frame(root, bg="#ffffff", padx=24, pady=22)
    frame.grid(row=1, column=0, sticky="nsew")
    frame.columnconfigure(0, weight=1)

    header = tk.Frame(frame, bg="#ffffff")
    header.grid(row=0, column=0, sticky="ew")
    icon_file = SCRIPT_DIR / "assets" / "icon.png"
    icon_image = None
    if icon_file.exists():
        try:
            icon_image = tk.PhotoImage(file=str(icon_file)).subsample(12, 12)
            tk.Label(header, image=icon_image, bg="#ffffff").grid(row=0, column=0, rowspan=2, sticky="nw", padx=(0, 12))
        except Exception:
            icon_image = None
    root._save_image_icon = icon_image
    tk.Label(header, text="SaveImageToLink", bg="#ffffff", fg="#1d1d1f", font=font_title).grid(row=0, column=1, sticky="w")
    tk.Label(header, text="保存截图，复制图片引用。", bg="#ffffff", fg="#6e6e73", font=font_body).grid(
        row=1, column=1, sticky="w", pady=(4, 0)
    )

    tk.Label(
        frame,
        textvariable=install_status_var,
        bg="#eaf8ef",
        fg="#10883f",
        anchor="w",
        padx=12,
        pady=8,
        font=("Segoe UI", 10, "bold"),
    ).grid(row=1, column=0, sticky="ew", pady=(18, 2))

    tk.Label(frame, text="保存到", bg="#ffffff", fg="#1d1d1f", font=font_label).grid(row=2, column=0, sticky="w", pady=(14, 6))
    folder_row = tk.Frame(frame, bg="#ffffff")
    folder_row.grid(row=3, column=0, sticky="ew")
    folder_row.columnconfigure(0, weight=1)
    tk.Entry(folder_row, textvariable=save_dir_var, relief="solid", bd=1, font=font_body).grid(row=0, column=0, sticky="ew", ipady=8)
    tk.Button(folder_row, text="选择", command=choose_folder, relief="solid", bd=1, font=font_label, width=8).grid(
        row=0, column=1, padx=(8, 0), ipady=5
    )

    tk.Label(frame, text="复制为", bg="#ffffff", fg="#1d1d1f", font=font_label).grid(row=4, column=0, sticky="w", pady=(14, 6))
    ttk.Combobox(
        frame,
        values=[label for label, _value, _hint in format_items],
        textvariable=format_var,
        state="readonly",
        font=font_body,
    ).grid(row=5, column=0, sticky="ew", ipady=6)
    tk.Label(frame, textvariable=format_hint_var, bg="#ffffff", fg="#6e6e73", font=font_small, anchor="w").grid(
        row=6, column=0, sticky="ew", pady=(7, 0)
    )

    tk.Label(frame, text="文件名前缀", bg="#ffffff", fg="#1d1d1f", font=font_label).grid(row=7, column=0, sticky="w", pady=(14, 6))
    tk.Entry(frame, textvariable=prefix_var, relief="solid", bd=1, font=font_body, width=22).grid(row=8, column=0, sticky="w", ipady=8)

    tk.Button(
        frame,
        text="安装并启用",
        command=install_menu,
        bg="#0071e3",
        activebackground="#0077ed",
        fg="#ffffff",
        activeforeground="#ffffff",
        relief="flat",
        bd=0,
        font=("Segoe UI", 10, "bold"),
    ).grid(row=9, column=0, sticky="ew", pady=(22, 0), ipady=10)

    secondary = tk.Frame(frame, bg="#ffffff")
    secondary.grid(row=10, column=0, sticky="ew", pady=(13, 0))
    secondary.columnconfigure((0, 1, 2), weight=1)
    for col, (label, command) in enumerate([("测试保存", test_save), ("打开目录", open_folder), ("卸载", uninstall_menu)]):
        tk.Button(secondary, text=label, command=command, relief="flat", bd=0, bg="#ffffff", fg="#0071e3", font=font_label).grid(
            row=0, column=col
        )

    tk.Label(frame, textvariable=result_var, bg="#ffffff", fg="#6e6e73", font=font_small, wraplength=360, justify="left").grid(
        row=11, column=0, sticky="ew", pady=(14, 0)
    )

    format_var.trace_add("write", update_format_description)
    update_format_description()
    refresh_install_status()
    root.mainloop()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Save clipboard image and copy a local image link.")
    parser.add_argument("target", nargs="?", help="Target folder from Explorer right-click.")
    parser.add_argument("--save-here", help="Save clipboard image to this folder.")
    parser.add_argument("--save-default", action="store_true", help="Save clipboard image to configured folder.")
    parser.add_argument("--copy", "--copy-path", dest="copy", action="store_true", help="Copy formatted link to clipboard.")
    parser.add_argument("--copy-format", choices=sorted(COPY_FORMATS), help="Override configured copy format.")
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

    if args.install_context_menu:
        install_context_menu()
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
