import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image


ROOT = Path(__file__).resolve().parent
MODULE_PATH = ROOT / "macos" / "save_image_to_link_macos.py"
spec = importlib.util.spec_from_file_location("save_image_to_link_macos", MODULE_PATH)
macos = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(macos)

INSTALLER_PATH = ROOT / "macos" / "install_finder_actions.py"
installer_spec = importlib.util.spec_from_file_location("install_finder_actions", INSTALLER_PATH)
installer = importlib.util.module_from_spec(installer_spec)
assert installer_spec and installer_spec.loader
installer_spec.loader.exec_module(installer)


class MacOSSaveImageTests(unittest.TestCase):
    def test_default_paths_are_macos_user_paths(self):
        home = Path("/Users/alice")

        self.assertEqual(macos.default_save_dir(home=home), Path("/Users/alice/Pictures/SaveImageToLink"))
        self.assertEqual(
            macos.config_dir(home=home),
            Path("/Users/alice/Library/Application Support/SaveImageToLink"),
        )

    def test_format_clipboard_text(self):
        path = Path("/Users/alice/Pictures/SaveImageToLink/image.png")

        self.assertEqual(macos.format_clipboard_text(path, {"copy_format": "path"}), str(path))
        self.assertEqual(macos.format_clipboard_text(path, {"copy_format": "markdown"}), f"![]({path})")
        self.assertEqual(
            macos.format_clipboard_text(path, {"copy_format": "file_uri"}),
            "file:///Users/alice/Pictures/SaveImageToLink/image.png",
        )

    def test_save_clipboard_image_uses_configured_folder_and_markdown(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            copied = []
            image = Image.new("RGB", (4, 4), "red")
            config = {"save_dir": tmpdir, "copy_format": "markdown", "filename_prefix": "image"}

            with patch.object(macos, "get_clipboard_image", return_value=image):
                with patch.object(macos, "set_clipboard_text", copied.append):
                    with patch.object(macos, "notify"):
                        result = macos.save_clipboard_image(copy_link=True, config=config)

            saved = Path(result)
            self.assertEqual(saved.parent, Path(tmpdir))
            self.assertTrue(saved.name.startswith("image_"))
            self.assertEqual(copied, [f"![]({saved})"])

    def test_finder_workflow_contains_script_and_service_metadata(self):
        plist = installer.workflow_plist("Save Image and Copy Link", "python3 tool.py\n", receives_input=False)

        self.assertEqual(plist["workflowMetaData"]["serviceApplicationBundleID"], "com.apple.finder")
        self.assertIn("python3 tool.py", plist["actions"][0]["action"]["ActionParameters"]["COMMAND_STRING"])

    def test_installer_parse_args_supports_uninstall(self):
        args = installer.parse_args(["--uninstall"])

        self.assertTrue(args.uninstall)


if __name__ == "__main__":
    unittest.main()
