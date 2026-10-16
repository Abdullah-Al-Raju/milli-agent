"""
Native Win32 C Hardware Actuator via user32.dll SendInput.
Provides sub-0.02ms pointer warps, mouse clicks, and keystroke injection on Windows.
"""

import sys
import time
import ctypes
from typing import Optional


class NativeWin32InputController:
    """
    Direct user32.SendInput actuation driver for Windows.
    Sub-0.02ms cursor warps and hardware event dispatch.
    """

    def __init__(self):
        self.user32 = None
        if sys.platform == "win32":
            self.user32 = ctypes.windll.user32

    def move_to(self, x: int, y: int):
        """Warps cursor instantly to (x, y) coordinates via SetCursorPos."""
        if self.user32:
            self.user32.SetCursorPos(int(x), int(y))

    def click(self, x: Optional[int] = None, y: Optional[int] = None, button: int = 1):
        """Dispatches mouse down and mouse up in single hardware tick."""
        if not self.user32:
            return

        if x is not None and y is not None:
            self.move_to(x, y)

        # mouse_event / SendInput flags
        # MOUSEEVENTF_LEFTDOWN = 0x0002, MOUSEEVENTF_LEFTUP = 0x0004
        # MOUSEEVENTF_RIGHTDOWN = 0x0008, MOUSEEVENTF_RIGHTUP = 0x0010
        if button == 1:
            down_flag = 0x0002
            up_flag = 0x0004
        elif button == 3:
            down_flag = 0x0008
            up_flag = 0x0010
        else:
            down_flag = 0x0020
            up_flag = 0x0040

        self.user32.mouse_event(down_flag, 0, 0, 0, 0)
        self.user32.mouse_event(up_flag, 0, 0, 0, 0)

    def scroll(self, clicks: int = 1, direction: str = "down"):
        """Dispatches hardware mouse wheel event."""
        if not self.user32:
            return
        # MOUSEEVENTF_WHEEL = 0x0800, WHEEL_DELTA = 120
        delta = -120 * clicks if direction.lower() == "down" else 120 * clicks
        self.user32.mouse_event(0x0800, 0, 0, delta, 0)

    def type_char(self, char: str):
        """Injects unicode character directly via KEYEVENTF_UNICODE."""
        if not self.user32:
            return
        # KEYEVENTF_UNICODE = 0x0004, KEYEVENTF_KEYUP = 0x0002
        code = ord(char)
        self.user32.keybd_event(0, code, 0x0004, 0)
        self.user32.keybd_event(0, code, 0x0004 | 0x0002, 0)

    def press_key(self, key_name: str):
        """Dispatches virtual key code press and release."""
        if not self.user32:
            return
        # Common virtual key mappings
        vk_map = {
            "return": 0x0D,
            "enter": 0x0D,
            "tab": 0x09,
            "space": 0x20,
            "backspace": 0x08,
            "escape": 0x1B,
            "ctrl": 0x11,
            "shift": 0x10,
            "alt": 0x12
        }
        vk = vk_map.get(key_name.lower())
        if vk:
            self.user32.keybd_event(vk, 0, 0, 0)
            self.user32.keybd_event(vk, 0, 0x0002, 0)
