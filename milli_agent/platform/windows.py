"""
Windows Win32 Platform Driver for Milli-Agent.
Uses native ctypes to user32.dll and kernel32.dll.
Zero external pip dependencies required.
"""

import sys
import ctypes
from typing import List, Optional, Tuple
from .base import OSPlatformDriver, WindowInfo


class WindowsPlatformDriver(OSPlatformDriver):
    """
    Win32 platform driver providing sub-millisecond window targeting and activation.
    """

    def __init__(self):
        self.user32 = None
        self.kernel32 = None
        if sys.platform == "win32":
            self.user32 = ctypes.windll.user32
            self.kernel32 = ctypes.windll.kernel32

    def get_platform_name(self) -> str:
        """Returns platform identifier string."""
        return "windows"

    def get_screen_resolution(self) -> Tuple[int, int]:
        """Returns desktop width and height via GetSystemMetrics."""
        if not self.user32:
            return 1920, 1080
        w = self.user32.GetSystemMetrics(0)  # SM_CXSCREEN
        h = self.user32.GetSystemMetrics(1)  # SM_CYSCREEN
        return w, h

    def list_windows(self) -> List[WindowInfo]:
        """Enumerates visible top-level windows on the desktop."""
        if not self.user32:
            return []

        windows: List[WindowInfo] = []
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

        def enum_cb(hwnd, lparam):
            if self.user32.IsWindowVisible(hwnd):
                length = self.user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    self.user32.GetWindowTextW(hwnd, buff, length + 1)
                    title = buff.value

                    # Get Rect
                    class RECT(ctypes.Structure):
                        _fields_ = [("left", ctypes.c_long),
                                    ("top", ctypes.c_long),
                                    ("right", ctypes.c_long),
                                    ("bottom", ctypes.c_long)]

                    rect = RECT()
                    self.user32.GetWindowRect(hwnd, ctypes.byref(rect))
                    w = rect.right - rect.left
                    h = rect.bottom - rect.top

                    if w > 10 and h > 10:
                        windows.append(WindowInfo(
                            id=int(hwnd),
                            title=title,
                            wm_class="win32",
                            pid=0,
                            rect=(rect.left, rect.top, w, h),
                            client_rect=(rect.left, rect.top, w, h),
                            is_active=(hwnd == self.user32.GetForegroundWindow())
                        ))
            return True

        self.user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
        return windows

    def find_window(self, query: str) -> Optional[WindowInfo]:
        """Finds window by title substring case-insensitively."""
        q = query.lower()
        for win in self.list_windows():
            if q in win.title.lower():
                return win
        return None

    def activate_window(self, window_id: int) -> bool:
        """Sets target window as foreground active window."""
        if not self.user32:
            return False
        # SW_RESTORE = 9, SW_SHOW = 5
        self.user32.ShowWindow(window_id, 9)
        res = self.user32.SetForegroundWindow(window_id)
        return bool(res)

    def get_active_window(self) -> Optional[WindowInfo]:
        """Returns the currently focused active window."""
        if not self.user32:
            return None
        hwnd = self.user32.GetForegroundWindow()
        if not hwnd:
            return None
        for win in self.list_windows():
            if win.id == hwnd:
                return win
        return None

    def focus_window(self, window_id: int) -> bool:
        """Brings the window to the foreground and verifies input focus."""
        return self.activate_window(window_id)

    def send_key_to_window(self, window_id: int, key: str) -> bool:
        """Directs a keyboard event to target window with verified focus."""
        if not self.focus_window(window_id):
            return False
        if not self.user32:
            return False
        WM_KEYDOWN = 0x0100
        WM_KEYUP = 0x0101
        if len(key) == 1:
            vk = self.user32.VkKeyScanW(ord(key)) & 0xFF
            self.user32.PostMessageW(window_id, WM_KEYDOWN, vk, 0)
            self.user32.PostMessageW(window_id, WM_KEYUP, vk, 0)
            return True
        elif key.lower() in ("enter", "return"):
            VK_RETURN = 0x0D
            self.user32.PostMessageW(window_id, WM_KEYDOWN, VK_RETURN, 0)
            self.user32.PostMessageW(window_id, WM_KEYUP, VK_RETURN, 0)
            return True
        return True

    def send_click_to_window(self, window_id: int, x: int, y: int, button: int = 1) -> bool:
        """Directs a mouse click at screen coordinates (x, y) with verified focus."""
        if not self.focus_window(window_id):
            return False
        if not self.user32:
            return False
        self.user32.SetCursorPos(int(x), int(y))
        MOUSEEVENTF_LEFTDOWN = 0x0002
        MOUSEEVENTF_LEFTUP = 0x0004
        MOUSEEVENTF_RIGHTDOWN = 0x0008
        MOUSEEVENTF_RIGHTUP = 0x0010
        if button == 1:
            self.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            self.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        elif button == 3:
            self.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            self.user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
        return True

    def close_window(self, window_id: int) -> bool:
        """Sends WM_CLOSE message to window."""
        if not self.user32:
            return False
        WM_CLOSE = 0x0010
        res = self.user32.PostMessageW(window_id, WM_CLOSE, 0, 0)
        return bool(res)
