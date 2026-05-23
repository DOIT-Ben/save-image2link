import unittest

import windows_gui


class WindowsGuiLayoutTests(unittest.TestCase):
    def test_window_layout_is_compact_and_dpi_stable(self):
        self.assertEqual(windows_gui.WINDOW_SIZE, "400x520")
        self.assertEqual(windows_gui.WINDOW_MIN_SIZE, (400, 520))
        self.assertEqual(windows_gui.GUIDE_WINDOW_SIZE, "460x420")
        self.assertIsNone(windows_gui.WINDOW_SCALING)
        self.assertLess(windows_gui.WIDGET_SCALING, 1.0)
        self.assertLessEqual(windows_gui.SECONDARY_BUTTON_WIDTH * 3, 300)

    def test_filename_preview_explains_image_prefix(self):
        preview = windows_gui.filename_preview("image")

        self.assertEqual(preview, "image_20260522_223000_123456.png")

    def test_centered_geometry_uses_screen_center(self):
        self.assertEqual(windows_gui.centered_geometry(400, 520, 1920, 1080), "400x520+760+280")
        self.assertEqual(windows_gui.centered_geometry(460, 420, 1920, 1080), "460x420+730+330")
        self.assertEqual(windows_gui.centered_geometry(460, 420, 300, 300), "460x420+0+0")

    def test_startup_guide_only_shows_before_seen(self):
        self.assertTrue(windows_gui.should_show_startup_guide({"guide_seen": "0"}))
        self.assertFalse(windows_gui.should_show_startup_guide({"guide_seen": "1"}))

    def test_copy_format_examples_explain_all_modes(self):
        examples = windows_gui.copy_format_examples(r"C:\Users\Alice\Pictures\SaveImageToLink\image.png")

        self.assertEqual(examples["markdown"], r"![](C:\Users\Alice\Pictures\SaveImageToLink\image.png)")
        self.assertEqual(examples["path"], r"C:\Users\Alice\Pictures\SaveImageToLink\image.png")
        self.assertEqual(examples["file_uri"], "file:///C:/Users/Alice/Pictures/SaveImageToLink/image.png")

    def test_guide_sections_are_step_by_step_and_cover_core_questions(self):
        sections = windows_gui.guide_sections()
        titles = [section["title"] for section in sections]
        full_text = "\n".join([section["title"] + "\n" + "\n".join(section["items"]) for section in sections])

        self.assertGreaterEqual(len(sections), 7)
        self.assertEqual(titles[0], "1. 先复制一张图片")
        self.assertIn("image 是文件名前缀", full_text)
        self.assertIn("Markdown 图片（推荐）", full_text)
        self.assertIn("纯路径", full_text)
        self.assertIn("文件链接 file://", full_text)
        self.assertIn("安装并启用", full_text)
        self.assertIn("测试保存", full_text)

    def test_guide_uses_compact_single_step_pages(self):
        sections = windows_gui.guide_sections()

        self.assertEqual(windows_gui.guide_nav_labels(0, len(sections)), ("关闭", "下一步"))
        self.assertEqual(windows_gui.guide_nav_labels(1, len(sections)), ("上一步", "下一步"))
        self.assertEqual(windows_gui.guide_nav_labels(len(sections) - 1, len(sections)), ("上一步", "完成"))
        for section in sections:
            self.assertLessEqual(len(section["items"]), 3)
            for item in section["items"]:
                self.assertLessEqual(len(item), 96)


if __name__ == "__main__":
    unittest.main()
