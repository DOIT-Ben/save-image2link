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
TEXT_PRIMARY = "#1d1d1f"
TEXT_SECONDARY = "#6e6e73"
SURFACE = "#ffffff"
APP_BG = "#f5f5f7"
CONTROL_BG = "#fbfbfd"
BORDER = "#d2d2d7"
QUIET_HOVER = "#f2f2f7"
GUIDE_WINDOW_SIZE = "460x420"


def filename_preview(prefix: str) -> str:
    clean = core.normalize_config({"filename_prefix": prefix}).get("filename_prefix", "image")
    return f"{clean}_20260522_223000_123456.png"


def copy_format_examples(path_text: str | Path) -> dict[str, str]:
    path = Path(path_text)
    return {
        "markdown": core.format_clipboard_text(path, {"copy_format": "markdown"}),
        "path": core.format_clipboard_text(path, {"copy_format": "path"}),
        "file_uri": core.format_clipboard_text(path, {"copy_format": "file_uri"}),
    }


def guide_sections() -> list[dict[str, list[str] | str]]:
    return [
        {
            "title": "1. 先复制一张图片",
            "items": [
                "先截图，或在网页、聊天、图片软件里复制图片。",
                "工具读取的是剪贴板图片，不是网页地址。",
                "没有图片时，会提示“剪贴板里没有图片”。",
            ],
        },
        {
            "title": "2. 选择保存目录",
            "items": [
                r"默认保存到 %USERPROFILE%\Pictures\SaveImageToLink。",
                "点击“选择”可以换成你自己的图片目录。",
                "目录不存在时，工具会自动创建。",
            ],
        },
        {
            "title": "3. 文件名里的 image 是什么",
            "items": [
                "image 是文件名前缀，不是图片内容。",
                f"保存后类似：{filename_preview('image')}。",
                "你也可以改成 shot、note、clip 等。",
            ],
        },
        {
            "title": "4. 复制格式怎么选",
            "items": [
                "Markdown 图片（推荐）：适合 Obsidian、README 和笔记。",
                "纯路径：适合脚本、本地打开和文件管理器。",
                "文件链接 file://：适合 HTML、浏览器和支持 URI 的工具。",
            ],
        },
        {
            "title": "5. 安装并启用右键菜单",
            "items": [
                "点击“安装并启用”即可注册右键菜单。",
                "菜单出现在文件夹空白处右键里。",
                "注册在当前用户下，不需要管理员权限。",
            ],
        },
        {
            "title": "6. 实际保存流程",
            "items": [
                "复制图片后，在文件夹空白处右键。",
                "选择“保存图片到此处”会保存到当前文件夹。",
                "选择“保存图片并复制链接”会保存并复制引用。",
            ],
        },
        {
            "title": "7. 测试保存",
            "items": [
                "第一次使用时，建议先复制一张图片。",
                "点击“测试保存”，看保存目录里是否出现文件。",
                "测试成功后，右键菜单一般也能正常使用。",
            ],
        },
        {
            "title": "8. 常见问题",
            "items": [
                "找不到菜单：请在文件夹空白区域右键。",
                "想换目录：重新选择目录，再安装并启用。",
                "想移除：点击“卸载”，已保存图片不会被删除。",
            ],
        },
    ]


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


def centered_geometry(width: int, height: int, screen_width: int, screen_height: int) -> str:
    x = max((screen_width - width) // 2, 0)
    y = max((screen_height - height) // 2, 0)
    return f"{width}x{height}+{x}+{y}"


def _center_window(window, width: int, height: int) -> None:
    window.update_idletasks()
    window.geometry(centered_geometry(width, height, window.winfo_screenwidth(), window.winfo_screenheight()))


def should_show_startup_guide(config: dict[str, str]) -> bool:
    return str(config.get("guide_seen", "0")) != "1"


def guide_nav_labels(index: int, total: int) -> tuple[str, str]:
    previous_label = "关闭" if index <= 0 else "上一步"
    next_label = "完成" if index >= total - 1 else "下一步"
    return previous_label, next_label


def open_guide_window(parent, ctk):
    guide = ctk.CTkToplevel(parent, fg_color=APP_BG)
    guide.title("使用引导")
    guide.geometry(GUIDE_WINDOW_SIZE)
    guide.minsize(460, 420)
    guide.maxsize(460, 420)
    guide.resizable(False, False)
    guide.transient(parent)
    guide.grab_set()
    guide.grid_columnconfigure(0, weight=1)
    guide.grid_rowconfigure(1, weight=1)
    sections = guide_sections()
    state = {"index": 0}

    header = ctk.CTkFrame(guide, fg_color="transparent")
    header.grid(row=0, column=0, sticky="ew", padx=22, pady=(20, 10))
    header.grid_columnconfigure(0, weight=1)
    step_var = ctk.StringVar(value="")
    ctk.CTkLabel(
        header,
        textvariable=step_var,
        anchor="w",
        font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
        text_color=ACCENT,
    ).grid(row=0, column=0, sticky="ew")
    ctk.CTkLabel(
        header,
        text="一步一步完成设置，不用一次看完所有说明。",
        anchor="w",
        font=ctk.CTkFont(family=FONT_FAMILY, size=12),
        text_color=TEXT_SECONDARY,
    ).grid(row=1, column=0, sticky="ew", pady=(4, 0))

    progress = ctk.CTkProgressBar(header, height=5, corner_radius=3, fg_color="#e5e5ea", progress_color=ACCENT)
    progress.grid(row=2, column=0, sticky="ew", pady=(12, 0))

    card = ctk.CTkFrame(guide, fg_color=SURFACE, corner_radius=14, border_width=1, border_color="#e5e5ea")
    card.grid(row=1, column=0, sticky="nsew", padx=22, pady=(0, 14))
    card.grid_columnconfigure(0, weight=1)

    footer = ctk.CTkFrame(guide, fg_color="transparent")
    footer.grid(row=2, column=0, sticky="ew", padx=22, pady=(0, 18))
    footer.grid_columnconfigure((0, 1), weight=1)
    previous_button = ctk.CTkButton(
        footer,
        text="关闭",
        width=112,
        height=36,
        corner_radius=10,
        fg_color=QUIET_HOVER,
        hover_color="#e5e5ea",
        text_color=TEXT_PRIMARY,
        font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
    )
    previous_button.grid(row=0, column=0, sticky="w")
    next_button = ctk.CTkButton(
        footer,
        text="下一步",
        width=112,
        height=36,
        corner_radius=10,
        fg_color=ACCENT,
        hover_color="#0077ed",
        font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
    )
    next_button.grid(row=0, column=1, sticky="e")

    def render_step() -> None:
        for child in card.winfo_children():
            child.destroy()
        index = state["index"]
        section = sections[index]
        previous_label, next_label = guide_nav_labels(index, len(sections))
        step_var.set(f"步骤 {index + 1} / {len(sections)}")
        progress.set((index + 1) / len(sections))
        previous_button.configure(text=previous_label)
        next_button.configure(text=next_label)
        ctk.CTkLabel(
            card,
            text=str(section["title"]),
            anchor="w",
            font=ctk.CTkFont(family=FONT_FAMILY, size=19, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).grid(row=0, column=0, sticky="ew", padx=22, pady=(22, 14))
        for row, item in enumerate(list(section["items"]), start=1):
            ctk.CTkLabel(
                card,
                text="• " + item,
                anchor="w",
                justify="left",
                wraplength=374,
                font=ctk.CTkFont(family=FONT_FAMILY, size=13),
                text_color="#424245",
            ).grid(row=row, column=0, sticky="ew", padx=22, pady=(0, 10))

    def go_previous() -> None:
        if state["index"] <= 0:
            guide.destroy()
            return
        state["index"] -= 1
        render_step()

    def go_next() -> None:
        if state["index"] >= len(sections) - 1:
            guide.destroy()
            return
        state["index"] += 1
        render_step()

    previous_button.configure(command=go_previous)
    next_button.configure(command=go_next)
    render_step()
    _center_window(guide, 460, 420)
    guide.lift()
    guide.attributes("-topmost", True)
    guide.after(250, lambda: guide.attributes("-topmost", False))
    guide.focus_force()
    return guide


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

    app = ctk.CTk(fg_color=APP_BG)
    app.title("SaveImageToLink")
    app.geometry(WINDOW_SIZE)
    app.minsize(*WINDOW_MIN_SIZE)
    app.maxsize(*WINDOW_MIN_SIZE)
    app.resizable(False, False)
    _center_window(app, *WINDOW_MIN_SIZE)

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
                "menu_language": config.get("menu_language", "zh-CN"),
                "guide_seen": config.get("guide_seen", "0"),
            }
        )

    def mark_guide_seen() -> None:
        config["guide_seen"] = "1"
        core.save_config(current_config())

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

    def show_guide() -> None:
        open_guide_window(app, ctk)

    def show_startup_guide() -> None:
        if not should_show_startup_guide(config):
            return
        open_guide_window(app, ctk)
        mark_guide_seen()

    app.grid_columnconfigure(0, weight=1)
    shell = ctk.CTkFrame(app, fg_color=SURFACE, corner_radius=16, border_width=1, border_color="#e5e5ea")
    shell.grid(row=0, column=0, padx=12, pady=12, sticky="nsew")
    shell.grid_columnconfigure(0, weight=1)

    header = ctk.CTkFrame(shell, fg_color="transparent")
    header.grid(row=0, column=0, padx=18, pady=(18, 10), sticky="ew")
    header.grid_columnconfigure(1, weight=1)
    header.grid_columnconfigure(2, weight=0)

    icon_image = None
    icon_png = core.SCRIPT_DIR / "assets" / "icon.png"
    if icon_png.exists():
        try:
            icon_image = ctk.CTkImage(light_image=Image.open(icon_png), size=(34, 34))
        except Exception:
            icon_image = None

    icon_box = ctk.CTkLabel(header, text="", image=icon_image, width=44, height=44, fg_color=APP_BG, corner_radius=11)
    icon_box.grid(row=0, column=0, rowspan=2, padx=(0, 12), sticky="w")
    ctk.CTkLabel(
        header,
        text="SaveImageToLink",
        font=ctk.CTkFont(family="Segoe UI", size=19, weight="bold"),
        text_color=TEXT_PRIMARY,
    ).grid(row=0, column=1, sticky="w")
    ctk.CTkLabel(
        header,
        text="保存截图，复制图片引用",
        font=ctk.CTkFont(family=FONT_FAMILY, size=11),
        text_color=TEXT_SECONDARY,
    ).grid(row=1, column=1, sticky="w", pady=(2, 0))
    ctk.CTkButton(
        header,
        text="引导",
        width=54,
        height=30,
        corner_radius=10,
        fg_color=QUIET_HOVER,
        hover_color="#e5e5ea",
        text_color=ACCENT,
        font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
        command=show_guide,
    ).grid(row=0, column=2, rowspan=2, sticky="e")

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
        border_color=BORDER,
        fg_color=CONTROL_BG,
        font=ctk.CTkFont(family="Segoe UI", size=12),
    ).grid(row=0, column=0, sticky="ew")
    ctk.CTkButton(
        folder_row,
        text="选择",
        width=62,
        height=36,
        corner_radius=10,
        fg_color=QUIET_HOVER,
        hover_color="#e5e5ea",
        text_color=TEXT_PRIMARY,
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
        fg_color=CONTROL_BG,
        button_color=CONTROL_BG,
        button_hover_color=QUIET_HOVER,
        text_color=TEXT_PRIMARY,
        dropdown_fg_color=SURFACE,
        dropdown_hover_color=QUIET_HOVER,
        dropdown_text_color=TEXT_PRIMARY,
        font=ctk.CTkFont(family=FONT_FAMILY, size=12),
        dropdown_font=ctk.CTkFont(family=FONT_FAMILY, size=12),
        command=lambda _value: update_format_hint(),
    )
    format_menu.configure(anchor="w")
    format_menu.grid(row=3, column=0, pady=(7, 0), sticky="ew")
    ctk.CTkLabel(
        body,
        textvariable=hint_var,
        anchor="w",
        font=ctk.CTkFont(family=FONT_FAMILY, size=10),
        text_color=TEXT_SECONDARY,
    ).grid(row=4, column=0, pady=(6, 0), sticky="ew")

    compact_row = ctk.CTkFrame(body, fg_color="transparent")
    compact_row.grid(row=5, column=0, pady=(12, 0), sticky="ew")
    compact_row.grid_columnconfigure(1, weight=1)
    ctk.CTkLabel(
        compact_row,
        text="文件名",
        font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
        text_color=TEXT_PRIMARY,
    ).grid(row=0, column=0, padx=(0, 8))
    ctk.CTkEntry(
        compact_row,
        textvariable=prefix_var,
        height=32,
        width=116,
        corner_radius=9,
        border_color=BORDER,
        fg_color=CONTROL_BG,
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
        "hover_color": QUIET_HOVER,
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
        text_color=TEXT_SECONDARY,
    ).grid(row=5, column=0, padx=18, pady=(8, 14), sticky="ew")

    format_var.trace_add("write", update_format_hint)
    update_format_hint()
    refresh_install_status()
    app.after(350, show_startup_guide)
    app.mainloop()
