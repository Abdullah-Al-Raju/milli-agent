"""
Unit tests for cross-platform Windows driver stubs and factory selection.
"""

import unittest
from unittest.mock import patch, MagicMock
from milli_agent.platform.windows import WindowsPlatformDriver
from milli_agent.controller.native_win32 import NativeWin32InputController
from milli_agent.capture.windows import WindowsCaptureSource


class TestWindowsPlatform(unittest.TestCase):

    def test_windows_platform_driver_interface(self):
        """Verifies Windows driver methods without requiring a physical Windows host."""
        driver = WindowsPlatformDriver()
        # Mock user32
        driver.user32 = MagicMock()
        driver.user32.GetSystemMetrics.side_effect = lambda code: 1920 if code == 0 else 1080
        w, h = driver.get_screen_resolution()
        self.assertEqual(w, 1920)
        self.assertEqual(h, 1080)

        # Mock window activation
        driver.user32.ShowWindow.return_value = 1
        driver.user32.SetForegroundWindow.return_value = 1
        ok = driver.activate_window(12345)
        self.assertTrue(ok)
        driver.user32.SetForegroundWindow.assert_called_with(12345)

    def test_native_win32_actuator(self):
        """Verifies native Win32 hardware input controller."""
        actuator = NativeWin32InputController()
        actuator.user32 = MagicMock()

        # Test move
        actuator.move_to(500, 300)
        actuator.user32.SetCursorPos.assert_called_with(500, 300)

        # Test click
        actuator.click(600, 400, button=1)
        self.assertEqual(actuator.user32.mouse_event.call_count, 2)


if __name__ == "__main__":
    unittest.main()
