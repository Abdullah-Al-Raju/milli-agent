"""
Linux X11 Platform Driver for Milli-Agent.
Provides verified window targeting, EWMH protocol inspection,
and deterministic event delivery without guessing.
"""

import os
import re
import subprocess
import time
from typing import List, Optional, Tuple
from .base import OSPlatformDriver, WindowInfo


class LinuxX11PlatformDriver(OSPlatformDriver):
    """
    Direct X11 / EWMH protocol driver for Linux desktop environments (XFCE, GNOME, KDE).
    """

    def __init__(self):
        self.display = os.environ.get("DISPLAY", ":0.0")

    def get_platform_name(self) -> str:
        return "linux_x11"

    def get_screen_resolution(self) -> Tuple[int, int]:
        """Returns desktop display resolution as (width, height) via xwininfo."""
        try:
            out = subprocess.check_output(
                ["xwininfo", "-root"],
                stderr=subprocess.DEVNULL
            ).decode()
            w_match = re.search(r"Width:\s+(\d+)", out)
            h_match = re.search(r"Height:\s+(\d+)", out)
            if w_match and h_match:
                return int(w_match.group(1)), int(h_match.group(1))
        except Exception:
            pass
        return 1920, 1080

    def _parse_geometry(self, window_id: int) -> Tuple[int, int, int, int]:
        """Extracts (x, y, width, height) from xwininfo."""
        try:
            out = subprocess.check_output(
                ["xwininfo", "-id", str(window_id)],
                stderr=subprocess.DEVNULL
            ).decode()

            x = int(re.search(r"Absolute upper-left X:\s+(-?\d+)", out).group(1))
            y = int(re.search(r"Absolute upper-left Y:\s+(-?\d+)", out).group(1))
            w = int(re.search(r"Width:\s+(\d+)", out).group(1))
            h = int(re.search(r"Height:\s+(\d+)", out).group(1))
            return (x, y, w, h)
        except Exception:
            return (0, 0, 0, 0)

    def _get_window_prop(self, window_id: int, prop: str) -> str:
        """Retrieves raw string property for a window via xprop."""
        try:
            out = subprocess.check_output(
                ["xprop", "-id", str(window_id), prop],
                stderr=subprocess.DEVNULL
            ).decode()
            if "=" in out:
                return out.split("=", 1)[1].strip().strip('"')
            return ""
        except Exception:
            return ""

    def get_active_window(self) -> Optional[WindowInfo]:
        """Queries _NET_ACTIVE_WINDOW to find the window currently holding OS focus."""
        try:
            out = subprocess.check_output(
                ["xprop", "-root", "_NET_ACTIVE_WINDOW"],
                stderr=subprocess.DEVNULL
            ).decode()
            parts = out.split("#")
            if len(parts) > 1:
                hex_str = parts[1].split(",")[0].strip()
                wid = int(hex_str, 16)
                if wid > 0:
                    return self._inspect_window(wid, is_active=True)
        except Exception:
            pass
        return None

    def _inspect_window(self, wid: int, is_active: bool = False) -> WindowInfo:
        title = self._get_window_prop(wid, "WM_NAME")
        wm_class = self._get_window_prop(wid, "WM_CLASS")
        pid_str = self._get_window_prop(wid, "_NET_WM_PID")
        pid = int(pid_str) if pid_str.isdigit() else 0
        rect = self._parse_geometry(wid)

        return WindowInfo(
            id=wid,
            title=title,
            wm_class=wm_class,
            pid=pid,
            rect=rect,
            client_rect=rect,
            is_active=is_active
        )

    def list_windows(self) -> List[WindowInfo]:
        """Lists all windows in the EWMH client list."""
        windows = []
        active_wid = None
        active_win = self.get_active_window()
        if active_win:
            active_wid = active_win.id

        try:
            out = subprocess.check_output(
                ["xprop", "-root", "_NET_CLIENT_LIST"],
                stderr=subprocess.DEVNULL
            ).decode()
            parts = out.split("#")
            if len(parts) > 1:
                hex_list = [h.strip() for h in parts[1].split(",") if h.strip()]
                for h in hex_list:
                    try:
                        wid = int(h, 16)
                        if wid > 0:
                            is_act = (wid == active_wid)
                            windows.append(self._inspect_window(wid, is_active=is_act))
                    except Exception:
                        continue
        except Exception:
            pass
        return windows

    def find_window(self, query: str) -> Optional[WindowInfo]:
        """Finds the best matching window by title or class substring."""
        q_lower = query.lower()
        windows = self.list_windows()
        for w in windows:
            if q_lower in w.title.lower() or q_lower in w.wm_class.lower():
                return w
        return None

    def focus_window(self, window_id: int) -> bool:
        """
        Activates the window via EWMH protocol and verifies input focus.
        Retries up to 3 times with 50ms sync intervals.
        """
        for _ in range(3):
            subprocess.run(
                ["xdotool", "windowactivate", "--sync", str(window_id)],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(0.05)
            active = self.get_active_window()
            if active and active.id == window_id:
                return True
        return False

    def send_key_to_window(self, window_id: int, key: str) -> bool:
        """
        Sends a keyboard event to the target window with verified focus.
        """
        # Ensure window is active
        active = self.get_active_window()
        if not active or active.id != window_id:
            focused = self.focus_window(window_id)
            if not focused:
                return False

        # Direct key event injection via xdotool
        res = subprocess.run(
            ["xdotool", "key", "--window", str(window_id), key],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return res.returncode == 0

    def send_click_to_window(self, window_id: int, x: int, y: int, button: int = 1) -> bool:
        """
        Clicks at target screen coordinates with verified window focus.
        """
        active = self.get_active_window()
        if not active or active.id != window_id:
            focused = self.focus_window(window_id)
            if not focused:
                return False

        res = subprocess.run(
            ["xdotool", "mousemove", "--window", str(window_id), str(x), str(y), "click", str(button)],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return res.returncode == 0
