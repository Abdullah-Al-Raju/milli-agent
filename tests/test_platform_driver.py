import unittest
from milli_agent.platform import get_platform_driver, WindowInfo


class TestPlatformDriver(unittest.TestCase):

    def setUp(self):
        self.driver = get_platform_driver()

    def test_platform_detection(self):
        name = self.driver.get_platform_name()
        self.assertIn(name, ["linux_x11", "linux_wayland", "macos", "windows"])

    def test_list_windows(self):
        windows = self.driver.list_windows()
        self.assertIsInstance(windows, list)
        if len(windows) > 0:
            w = windows[0]
            self.assertIsInstance(w, WindowInfo)
            self.assertGreater(w.id, 0)

    def test_active_window(self):
        active = self.driver.get_active_window()
        # On headless or CI it might be None, but on desktop display it returns active window
        if active is not None:
            self.assertIsInstance(active, WindowInfo)
            self.assertTrue(active.is_active)
            self.assertGreater(active.id, 0)


if __name__ == '__main__':
    unittest.main()
