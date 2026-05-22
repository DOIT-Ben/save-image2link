"""macOS implementation for SaveImageToLink."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

from PIL import Image


APP_NAME = "SaveImageToLink"
COPY_FORMATS = {"path", "markdown", "file_uri"}


def default_save_dir(home: Path | None = None) -> Path:
    return (home or Path.home()) / "Pictures" / APP_NAME


def config_dir(home: Path | None = None) -> Path:
    return (home or Path.home()) / "Library" / "Application Support" / APP_NAME


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


def get_clipboard_image() -> Image.Image:
    try:
        from PIL import ImageGrab
    except Exception as exc:
        raise RuntimeError("Pillow ImageGrab is not available: " + str(exc)) from exc
    image = ImageGrab.grabclipboard()
    if image is None:
        raise RuntimeError("No image in clipboard")
    if not isinstance(image, Image.Image):
        raise RuntimeError("Clipboard does not contain an image")
    return image


def set_clipboard_text(text: str) -> None:
    subprocess.run(["pbcopy"], input=text, text=True, check=True)


def notify(title: str, message: str) -> None:
    script = f'display notification {json.dumps(message)} with title {json.dumps(title)}'
    subprocess.run(["osascript", "-e", script], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def format_clipboard_text(filepath: Path, config: dict[str, Any]) -> str:
    fmt = config.get("copy_format", "markdown")
    path_text = str(filepath)
    if fmt == "path":
        return path_text
    if fmt == "file_uri":
        posix_path = path_text.replace("\\", "/")
        if not posix_path.startswith("/"):
            posix_path = str(filepath.resolve()).replace("\\", "/")
        return "file://" + quote(posix_path)
    return f"![]({path_text})"


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
    show_notification: bool = True,
) -> str:
    active_config = normalize_config(config or load_config())
    folder = Path(target_folder or active_config["save_dir"]).expanduser()
    ensure_writable_folder(folder)

    image = get_clipboard_image()
    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGBA" if "A" in image.getbands() else "RGB")

    filename = f"{active_config['filename_prefix']}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
    filepath = folder / filename
    image.save(filepath, "PNG")

    if copy_link:
        text = format_clipboard_text(filepath, active_config)
        set_clipboard_text(text)
        if show_notification:
            notify("Image saved and link copied", text)
    elif show_notification:
        notify("Image saved", str(filepath))
    return str(filepath)


def open_settings_window() -> None:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    config = load_config()
    root = tk.Tk()
    root.title(APP_NAME)
    root.resizable(False, False)

    save_dir_var = tk.StringVar(value=config["save_dir"])
    format_var = tk.StringVar(value=config["copy_format"])
    prefix_var = tk.StringVar(value=config["filename_prefix"])
    status_var = tk.StringVar(value="")

    def choose_folder() -> None:
        selected = filedialog.askdirectory(initialdir=save_dir_var.get() or str(default_save_dir()))
        if selected:
            save_dir_var.set(selected)

    def current_config() -> dict[str, str]:
        return normalize_config(
            {
                "save_dir": save_dir_var.get(),
                "copy_format": format_var.get(),
                "filename_prefix": prefix_var.get(),
            }
        )

    def save_settings() -> None:
        path = save_config(current_config())
        status_var.set(f"Settings saved: {path}")

    def open_folder() -> None:
        cfg = current_config()
        Path(cfg["save_dir"]).mkdir(parents=True, exist_ok=True)
        webbrowser.open(str(Path(cfg["save_dir"])))

    def install_actions() -> None:
        try:
            save_settings()
            installer = Path(__file__).with_name("install_finder_actions.py")
            subprocess.run([sys.executable, str(installer)], check=True)
            messagebox.showinfo(APP_NAME, "Finder Quick Actions installed.")
        except Exception as exc:
            messagebox.showerror(APP_NAME, str(exc))

    def test_save() -> None:
        try:
            save_settings()
            result = save_clipboard_image(copy_link=True, config=current_config())
            status_var.set(f"Saved: {result}")
        except Exception as exc:
            messagebox.showerror(APP_NAME, str(exc))

    frame = ttk.Frame(root, padding=12)
    frame.grid(row=0, column=0, sticky="nsew")
    padding = {"padx": 12, "pady": 6}

    ttk.Label(frame, text="Save folder").grid(row=0, column=0, sticky="w", **padding)
    ttk.Entry(frame, width=54, textvariable=save_dir_var).grid(row=0, column=1, sticky="ew", **padding)
    ttk.Button(frame, text="Browse", command=choose_folder).grid(row=0, column=2, **padding)

    ttk.Label(frame, text="Copy format").grid(row=1, column=0, sticky="w", **padding)
    ttk.Combobox(frame, values=sorted(COPY_FORMATS), textvariable=format_var, state="readonly", width=18).grid(
        row=1, column=1, sticky="w", **padding
    )

    ttk.Label(frame, text="Filename prefix").grid(row=2, column=0, sticky="w", **padding)
    ttk.Entry(frame, width=24, textvariable=prefix_var).grid(row=2, column=1, sticky="w", **padding)

    buttons = ttk.Frame(frame)
    buttons.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(10, 2))
    ttk.Button(buttons, text="Save settings", command=save_settings).grid(row=0, column=0, padx=4)
    ttk.Button(buttons, text="Open folder", command=open_folder).grid(row=0, column=1, padx=4)
    ttk.Button(buttons, text="Install Finder actions", command=install_actions).grid(row=0, column=2, padx=4)
    ttk.Button(buttons, text="Test save", command=test_save).grid(row=0, column=3, padx=4)

    ttk.Label(frame, textvariable=status_var, foreground="#555").grid(row=4, column=0, columnspan=3, sticky="w", **padding)
    root.mainloop()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Save clipboard image and copy a local image link on macOS.")
    parser.add_argument("target", nargs="?", help="Optional target folder.")
    parser.add_argument("--save-here", help="Save clipboard image to this folder.")
    parser.add_argument("--save-default", action="store_true", help="Save clipboard image to configured folder.")
    parser.add_argument("--copy", action="store_true", help="Copy formatted link to clipboard.")
    parser.add_argument("--copy-format", choices=sorted(COPY_FORMATS), help="Override configured copy format.")
    parser.add_argument("--settings", action="store_true", help="Open visual settings window.")
    parser.add_argument("--no-notify", action="store_true", help="Disable macOS notification.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> str | None:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    config = load_config()
    if args.copy_format:
        config["copy_format"] = args.copy_format
    if args.settings or not any([args.save_here, args.save_default, args.target]):
        open_settings_window()
        return None
    target = args.save_here or args.target
    if args.save_default:
        target = config["save_dir"]
    return save_clipboard_image(target_folder=target, copy_link=args.copy, config=config, show_notification=not args.no_notify)


if __name__ == "__main__":
    main()
