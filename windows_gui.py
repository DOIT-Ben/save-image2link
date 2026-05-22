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
GUIDE_WINDOW_SIZE = "560x680"


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
    sample_path = r"C:\Users\Alice\Pictures\SaveImageToLink\image.png"
    examples = copy_format_examples(sample_path)
    return [
        {
            "title": "1. 先复制一张图片",
            "items": [
                "这个工具读取的是剪贴板里的图片。你可以先截图、复制网页图片、复制聊天里的图片，或在图片软件里按 Ctrl+C。",
                "如果剪贴板里不是图片，点击“测试保存”或右键保存时会提示“剪贴板里没有图片”。",
            ],
        },
        {
            "title": "2. 选择保存目录",
            "items": [
                r"默认目录是 %USERPROFILE%\Pictures\SaveImageToLink，也就是每个用户自己的图片目录。",
                "点击“选择”可以换成任意你想保存图片的位置。工具会自动创建不存在的目录。",
                "公开发布版本不会写入你的个人路径，别人的电脑会使用他们自己的用户目录。",
            ],
        },
        {
            "title": "3. 文件名里的 image 是什么",
            "items": [
                "image 是文件名前缀，不是图片内容，也不是图片链接。",
                f"保存时会自动追加时间，示例：{filename_preview('image')}。",
                "你可以把它改成 shot、note、clip 等。比如前缀是 note，文件名会变成 note_时间.png。",
                "保留前缀的好处是：图片不会重名，也能从文件名看出它们来自这个工具。",
            ],
        },
        {
            "title": "4. 复制格式怎么选",
            "items": [
                f"Markdown 图片（推荐）：复制 {examples['markdown']}。适合 Obsidian、Markdown 文档、很多笔记软件。粘贴后通常会直接显示图片。",
                f"纯路径：复制 {examples['path']}。适合发给本地脚本、资源管理器地址栏、需要文件路径的软件。",
                f"文件链接 file://：复制 {examples['file_uri']}。适合 HTML、浏览器、部分支持标准文件 URI 的工具。",
                "不知道选哪个就用 Markdown 图片（推荐）。它对笔记场景最友好。",
            ],
        },
        {
            "title": "5. 安装并启用右键菜单",
            "items": [
                "点“安装并启用”后，会在当前 Windows 用户下注册资源管理器右键菜单，不需要管理员权限。",
                "菜单会出现在文件夹空白处右键里，不是图片文件本身的右键菜单。",
                "如果按钮状态显示“右键菜单已启用”，说明注册成功。",
            ],
        },
        {
            "title": "6. 实际保存流程",
            "items": [
                "第一步：复制一张图片或截图。",
                "第二步：打开资源管理器，在目标文件夹空白处右键。",
                "第三步：选择“保存图片到此处”，图片会保存到当前文件夹。",
                "或者选择“保存图片并复制链接”，图片会保存到设置目录，并按当前复制格式把引用放进剪贴板。",
                "第四步：到文档、笔记或聊天框里粘贴刚复制的引用。",
            ],
        },
        {
            "title": "7. 测试保存",
            "items": [
                "点击“测试保存”会直接从剪贴板保存一张图片，并复制对应引用。",
                "它适合第一次安装后自检：先复制图片，再点测试保存，看保存目录里是否出现文件。",
                "如果测试保存成功，右键菜单一般也可以正常使用。",
            ],
        },
        {
            "title": "8. 常见问题",
            "items": [
                "没有图片：先确认你复制的是图片本身，不是图片所在网页地址。",
                "找不到右键菜单：在文件夹空白区域右键，不要在文件上右键；必要时重启资源管理器或重新点击“安装并启用”。",
                "想换目录：重新打开程序，点击“选择”，再点击“安装并启用”保存配置。",
                "想移除：点击“卸载”，右键菜单会从当前用户配置中移除，已保存的图片不会被删除。",
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


def _add_guide_section(ctk, parent, title: str, items: list[str]) -> None:
    section = ctk.CTkFrame(parent, fg_color="#ffffff", corner_radius=12, border_width=1, border_color="#e5e5ea")
    section.pack(fill="x", padx=0, pady=(0, 10))
    ctk.CTkLabel(
        section,
        text=title,
        anchor="w",
        font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
        text_color="#1d1d1f",
    ).pack(fill="x", padx=14, pady=(12, 6))
    for item in items:
        ctk.CTkLabel(
            section,
            text="• " + item,
            anchor="w",
            justify="left",
            wraplength=470,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color="#424245",
        ).pack(fill="x", padx=14, pady=(0, 7))


def open_guide_window(parent, ctk) -> None:
    guide = ctk.CTkToplevel(parent, fg_color="#f5f5f7")
    guide.title("使用引导")
    guide.geometry(GUIDE_WINDOW_SIZE)
    guide.minsize(520, 600)
    guide.transient(parent)
    guide.grab_set()
    guide.grid_columnconfigure(0, weight=1)
    guide.grid_rowconfigure(1, weight=1)

    header = ctk.CTkFrame(guide, fg_color="transparent")
    header.grid(row=0, column=0, sticky="ew", padx=22, pady=(22, 12))
    header.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(
        header,
        text="一步步设置 SaveImageToLink",
        anchor="w",
        font=ctk.CTkFont(family=FONT_FAMILY, size=21, weight="bold"),
        text_color="#1d1d1f",
    ).grid(row=0, column=0, sticky="ew")
    ctk.CTkLabel(
        header,
        text="先理解保存目录、文件名前缀和复制格式，再安装右键菜单。",
        anchor="w",
        font=ctk.CTkFont(family=FONT_FAMILY, size=12),
        text_color="#6e6e73",
    ).grid(row=1, column=0, sticky="ew", pady=(6, 0))

    scroll = ctk.CTkScrollableFrame(guide, fg_color="transparent")
    scroll.grid(row=1, column=0, sticky="nsew", padx=22, pady=(0, 12))
    for section in guide_sections():
        _add_guide_section(ctk, scroll, str(section["title"]), list(section["items"]))

    footer = ctk.CTkFrame(guide, fg_color="transparent")
    footer.grid(row=2, column=0, sticky="ew", padx=22, pady=(0, 18))
    footer.grid_columnconfigure(0, weight=1)
    ctk.CTkButton(
        footer,
        text="我明白了",
        width=118,
        height=36,
        corner_radius=10,
        fg_color=ACCENT,
        hover_color="#0077ed",
        font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
        command=guide.destroy,
    ).grid(row=0, column=1, sticky="e")
    guide.focus_force()


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

    def show_guide() -> None:
        open_guide_window(app, ctk)

    app.grid_columnconfigure(0, weight=1)
    shell = ctk.CTkFrame(app, fg_color="#ffffff", corner_radius=16, border_width=1, border_color="#e5e5ea")
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
    ctk.CTkButton(
        header,
        text="引导",
        width=54,
        height=30,
        corner_radius=10,
        fg_color="#f2f2f7",
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
