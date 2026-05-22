import unittest

import windows_gui


class WindowsGuiLayoutTests(unittest.TestCase):
    def test_window_layout_is_compact_and_dpi_stable(self):
        self.assertEqual(windows_gui.WINDOW_SIZE, "400x520")
        self.assertEqual(windows_gui.WINDOW_MIN_SIZE, (400, 520))
        self.assertIsNone(windows_gui.WINDOW_SCALING)
        self.assertLess(windows_gui.WIDGET_SCALING, 1.0)
        self.assertLessEqual(windows_gui.SECONDARY_BUTTON_WIDTH * 3, 300)


if __name__ == "__main__":
    unittest.main()
