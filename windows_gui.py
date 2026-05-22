"""CustomTkinter settings window for the Windows build."""
from __future__ import annotations

import os
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox

from PIL import Image

import save_image as core


WINDOW_SIZE = "400x520"
WINDOW_MIN_SIZE = (400, 520)
WINDOW_SCALING = None
WIDGET_SCALING = 0.9
SECONDARY_BUTTON_WIDTH = 92
FONT_FAMILY = "Microsoft YaHei UI"
ACCENT = "#0071e3"


def _format_maps() -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    options = core.copy_format_options()
    label_to_value = {item["label"]: item["value"] for item in options}
    value_to_label = {item["value"]: item["label"] for item in options}
    value_to_hint = {item["value"]: item["description"] for item in options}
    return label_to_value, value_to_label, value_to_hint


def _open_path(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        os.startfile(path)  # type: ignore[attr-defined]
        return
    webbrowser.open(str(path))


def open_settings_window() -> None:
    try:
        import customtkinter as ctk
    except Exception as exc:
        raise RuntimeError("缺少界面依赖 customtkinter，请先安装 requirements.txt。") from exc

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    if WINDOW_SCALING is not None:
        ctk.set_window_scaling(WINDOW_SCALING)
    ctk.set_widget_scaling(WIDGET_SCALING)

    config = core.load_config()
    label_to_format, format_to_label, format_hints = _format_maps()

    app = ctk.CTk(fg_color="#f5f5f7")
    app.title("SaveImageToLink")
    app.geometry(WINDOW_SIZE)
    app.minsize(*WINDOW_MIN_SIZE)
    app.maxsize(*WINDOW_MIN_SIZE)
    app.resizable(False, False)

    icon_path = core.SCRIPT_DIR / "assets" / "icon.ico"
    if icon_path.exists():
        try:
            app.iconbitmap(str(icon_path))
        except Exception:
            pass

    save_dir_var = ctk.StringVar(value=config["save_dir"])
    format_var = ctk.StringVar(value=format_to_label.get(config["copy_format"], format_to_label["markdown"]))
    prefix_var = ctk.StringVar(value=config["filename_prefix"])
    status_var = ctk.StringVar(value="")
    status_color_var = ctk.StringVar(value="#eef2f7")
    result_var = ctk.StringVar(value="复制图片后，右键即可保存并复制引用。")
    hint_var = ctk.StringVar(value="")

    def selected_copy_format() -> str:
        return label_to_format.get(format_var.get(), "markdown")

    def update_format_hint(*_args: object) -> None:
        hint_var.set(format_hints.get(selected_copy_format(), format_hints["markdown"]))

    def refresh_install_status() -> None:
        installed = core.is_context_menu_installed()
        status_var.set("右键菜单已启用" if installed else "右键菜单未启用")
        status_color_var.set("#e8f5ee" if installed else "#eef2f7")
        status_badge.configure(
            fg_color=status_color_var.get(),
            text_color="#12833b" if installed else "#6e6e73",
        )

    def current_config() -> dict[str, str]:
        return core.normalize_config(
            {
                "save_dir": save_dir_var.get(),
                "copy_format": selected_copy_format(),
                "filename_prefix": prefix_var.get(),
            }
        )

    def save_settings(show_result: bool = True) -> bool:
        try:
            core.save_config(current_config())
            if show_result:
                result_var.set("设置已保存。")
            return True
        except Exception as exc:
            messagebox.showerror(core.APP_NAME, core.friendly_error_message(exc))
            return False

    def choose_folder() -> None:
        initial = Path(save_dir_var.get()).expanduser()
        if not initial.exists():
            initial = core.default_save_dir()
        selected = filedialog.askdirectory(initialdir=str(initial))
        if selected:
            save_dir_var.set(selected)
            save_settings(show_result=False)
            result_var.set("保存目录已更新。")

    def open_folder() -> None:
        try:
            _open_path(Path(current_config()["save_dir"]).expanduser())
        except Exception as exc:
            messagebox.showerror(core.APP_NAME, core.friendly_error_message(exc))

    def install_menu() -> None:
        try:
            if not save_settings(show_result=False):
                return
            core.install_context_menu()
            refresh_install_status()
            result_var.set("已启用。复制图片后，可在文件夹空白处右键保存。")
        except Exception as exc:
            messagebox.showerror(core.APP_NAME, core.friendly_error_message(exc))

    def uninstall_menu() -> None:
        try:
            core.uninstall_context_menu()
            refresh_install_status()
            result_var.set("右键菜单已卸载。")
        except Exception as exc:
            messagebox.showerror(core.APP_NAME, core.friendly_error_message(exc))

    def test_save() -> None:
        try:
            if not save_settings(show_result=False):
                return
            result = core.save_clipboard_image(copy_link=True, config=current_config())
            result_var.set(f"已保存：{result}")
        except Exception as exc:
            messagebox.showerror(core.APP_NAME, core.friendly_error_message(exc))

    app.grid_columnconfigure(0, weight=1)
    shell = ctk.CTkFrame(app, fg_color="#ffffff", corner_radius=16, border_width=1, border_color="#e5e5ea")
    shell.grid(row=0, column=0, padx=12, pady=12, sticky="nsew")
    shell.grid_columnconfigure(0, weight=1)

    header = ctk.CTkFrame(shell, fg_color="transparent")
    header.grid(row=0, column=0, padx=18, pady=(18, 10), sticky="ew")
    header.grid_columnconfigure(1, weight=1)

    icon_image = None
    icon_png = core.SCRIPT_DIR / "assets" / "icon.png"
    if icon_png.exists():
        try:
            icon_image = ctk.CTkImage(light_image=Image.open(icon_png), size=(34, 34))
        except Exception:
            icon_image = None

    icon_box = ctk.CTkLabel(header, text="", image=icon_image, width=44, height=44, fg_color="#f5f5f7", corner_radius=11)
    icon_box.grid(row=0, column=0, rowspan=2, padx=(0, 12), sticky="w")
    ctk.CTkLabel(
        header,
        text="SaveImageToLink",
        font=ctk.CTkFont(family="Segoe UI", size=19, weight="bold"),
        text_color="#1d1d1f",
    ).grid(row=0, column=1, sticky="w")
    ctk.CTkLabel(
        header,
        text="保存截图，复制图片引用",
        font=ctk.CTkFont(family=FONT_FAMILY, size=11),
        text_color="#6e6e73",
    ).grid(row=1, column=1, sticky="w", pady=(2, 0))

    status_badge = ctk.CTkLabel(
        shell,
        textvariable=status_var,
        height=32,
        corner_radius=10,
        font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
    )
    status_badge.grid(row=1, column=0, padx=18, sticky="ew")

    body = ctk.CTkFrame(shell, fg_color="transparent")
    body.grid(row=2, column=0, padx=18, pady=(12, 0), sticky="ew")
    body.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(body, text="保存目录", anchor="w", font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold")).grid(
        row=0, column=0, sticky="ew"
    )
    folder_row = ctk.CTkFrame(body, fg_color="transparent")
    folder_row.grid(row=1, column=0, pady=(7, 0), sticky="ew")
    folder_row.grid_columnconfigure(0, weight=1)
    ctk.CTkEntry(
        folder_row,
        textvariable=save_dir_var,
        height=36,
        corner_radius=10,
        border_color="#d2d2d7",
        fg_color="#fbfbfd",
        font=ctk.CTkFont(family="Segoe UI", size=12),
    ).grid(row=0, column=0, sticky="ew")
    ctk.CTkButton(
        folder_row,
        text="选择",
        width=62,
        height=36,
        corner_radius=10,
        fg_color="#f2f2f7",
        hover_color="#e5e5ea",
        text_color="#1d1d1f",
        font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
        command=choose_folder,
    ).grid(row=0, column=1, padx=(8, 0))

    ctk.CTkLabel(body, text="复制格式", anchor="w", font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold")).grid(
        row=2, column=0, pady=(12, 0), sticky="ew"
    )
    format_menu = ctk.CTkOptionMenu(
        body,
        values=[item["label"] for item in core.copy_format_options()],
        variable=format_var,
        height=36,
        corner_radius=10,
        fg_color="#fbfbfd",
        button_color="#e5e5ea",
        button_hover_color="#d2d2d7",
        text_color="#1d1d1f",
        dropdown_fg_color="#ffffff",
        dropdown_hover_color="#f2f2f7",
        font=ctk.CTkFont(family=FONT_FAMILY, size=12),
        dropdown_font=ctk.CTkFont(family=FONT_FAMILY, size=12),
        command=lambda _value: update_format_hint(),
    )
    format_menu.grid(row=3, column=0, pady=(7, 0), sticky="ew")
    ctk.CTkLabel(
        body,
        textvariable=hint_var,
        anchor="w",
        font=ctk.CTkFont(family=FONT_FAMILY, size=10),
        text_color="#6e6e73",
    ).grid(row=4, column=0, pady=(6, 0), sticky="ew")

    compact_row = ctk.CTkFrame(body, fg_color="transparent")
    compact_row.grid(row=5, column=0, pady=(12, 0), sticky="ew")
    compact_row.grid_columnconfigure(1, weight=1)
    ctk.CTkLabel(
        compact_row,
        text="文件名",
        font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
        text_color="#1d1d1f",
    ).grid(row=0, column=0, padx=(0, 8))
    ctk.CTkEntry(
        compact_row,
        textvariable=prefix_var,
        height=32,
        width=116,
        corner_radius=9,
        border_color="#d2d2d7",
        fg_color="#fbfbfd",
        font=ctk.CTkFont(family="Segoe UI", size=12),
    ).grid(row=0, column=1, sticky="w")

    ctk.CTkButton(
        shell,
        text="安装并启用",
        height=42,
        corner_radius=12,
        fg_color=ACCENT,
        hover_color="#0077ed",
        font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
        command=install_menu,
    ).grid(row=3, column=0, padx=18, pady=(16, 0), sticky="ew")

    actions = ctk.CTkFrame(shell, fg_color="transparent")
    actions.grid(row=4, column=0, padx=18, pady=(8, 0), sticky="ew")
    actions.grid_columnconfigure((0, 1, 2), weight=1)
    action_style = {
        "width": SECONDARY_BUTTON_WIDTH,
        "height": 32,
        "corner_radius": 10,
        "fg_color": "transparent",
        "hover_color": "#f2f2f7",
        "text_color": ACCENT,
        "font": ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
    }
    ctk.CTkButton(actions, text="测试保存", command=test_save, **action_style).grid(row=0, column=0, sticky="ew")
    ctk.CTkButton(actions, text="打开目录", command=open_folder, **action_style).grid(row=0, column=1, sticky="ew", padx=4)
    ctk.CTkButton(actions, text="卸载", command=uninstall_menu, **action_style).grid(row=0, column=2, sticky="ew")

    ctk.CTkLabel(
        shell,
        textvariable=result_var,
        wraplength=330,
        justify="left",
        anchor="w",
        font=ctk.CTkFont(family=FONT_FAMILY, size=11),
        text_color="#6e6e73",
    ).grid(row=5, column=0, padx=18, pady=(8, 14), sticky="ew")

    format_var.trace_add("write", update_format_hint)
    update_format_hint()
    refresh_install_status()
    app.mainloop()
