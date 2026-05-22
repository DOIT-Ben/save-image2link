import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

import save_image


class SaveImageTests(unittest.TestCase):
    def test_default_save_dir_uses_current_user_pictures_folder(self):
        save_dir = save_image.default_save_dir(home=Path(r"C:\Users\Alice"))

        self.assertEqual(save_dir, Path(r"C:\Users\Alice\Pictures\SaveImageToLink"))

    def test_format_clipboard_text_supports_markdown_and_file_uri(self):
        path = Path(r"C:\Users\Alice\Pictures\SaveImageToLink\image.png")

        self.assertEqual(
            save_image.format_clipboard_text(path, {"copy_format": "markdown"}),
            r"![](C:\Users\Alice\Pictures\SaveImageToLink\image.png)",
        )
        self.assertEqual(
            save_image.format_clipboard_text(path, {"copy_format": "path"}),
            r"C:\Users\Alice\Pictures\SaveImageToLink\image.png",
        )
        self.assertEqual(
            save_image.format_clipboard_text(path, {"copy_format": "file_uri"}),
            "file:///C:/Users/Alice/Pictures/SaveImageToLink/image.png",
        )

    def test_config_round_trip_creates_public_default_without_personal_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"
            home = Path(r"C:\Users\Alice")

            config = save_image.load_config(config_file=config_file, home=home)
            self.assertEqual(config["save_dir"], str(home / "Pictures" / "SaveImageToLink"))

            config["save_dir"] = str(Path(tmpdir) / "images")
            config["copy_format"] = "path"
            save_image.save_config(config, config_file=config_file)
            loaded = save_image.load_config(config_file=config_file, home=home)
            self.assertEqual(loaded["copy_format"], "path")
            self.assertEqual(loaded["save_dir"], str(Path(tmpdir) / "images"))

    def test_build_context_menu_commands_target_program_and_configured_actions(self):
        commands = save_image.build_context_menu_commands(Path(r"C:\Tools\SaveImageToLink.exe"))

        self.assertIn("--save-here", commands["here"])
        self.assertIn('"%V"', commands["here"])
        self.assertIn("--save-default", commands["default"])
        self.assertIn("--copy", commands["default"])

    def test_default_mode_saves_to_configured_folder_and_copies_markdown(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            copied = []
            img = Image.new("RGB", (4, 4), "blue")
            config = {
                "save_dir": tmpdir,
                "copy_format": "markdown",
                "filename_prefix": "image",
            }

            with patch.object(save_image, "get_clipboard_image", return_value=img):
                with patch.object(save_image, "set_clipboard_text", copied.append):
                    with patch.object(save_image, "show_notification") as notify:
                        result = save_image.save_clipboard_image(copy_link=True, config=config)

            saved = Path(result)
            self.assertEqual(saved.parent, Path(tmpdir))
            self.assertTrue(saved.name.startswith("image_"))
            self.assertEqual(saved.suffix, ".png")
            self.assertTrue(saved.exists())
            self.assertEqual(copied, [f"![]({saved})"])
            notify.assert_called_once_with("Image saved and link copied", f"![]({saved})", is_error=False)

    def test_current_folder_mode_shows_saved_notification(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            img = Image.new("RGB", (4, 4), "green")

            with patch.object(save_image, "get_clipboard_image", return_value=img):
                with patch.object(save_image, "show_notification") as notify:
                    result = save_image.save_clipboard_image(target_folder=tmpdir, config={"filename_prefix": "image"})

            saved = Path(result)
            self.assertEqual(saved.parent, Path(tmpdir))
            self.assertTrue(saved.exists())
            notify.assert_called_once_with("Image saved", str(saved), is_error=False)


if __name__ == "__main__":
    unittest.main()
