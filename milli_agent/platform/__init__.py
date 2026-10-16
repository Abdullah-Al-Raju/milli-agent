"""
Platform abstraction factory for Milli-Agent.
Automatically detects the host operating system and instantiates the proper driver.
"""

import sys
import os
from .base import OSPlatformDriver, WindowInfo
from .linux_x11 import LinuxX11PlatformDriver


def get_platform_driver() -> OSPlatformDriver:
    """
    Returns the appropriate OSPlatformDriver for the current runtime environment.
    """
    plat = sys.platform.lower()

    if plat.startswith("linux"):
        # Check Wayland vs X11
        if "WAYLAND_DISPLAY" in os.environ and "DISPLAY" not in os.environ:
            # Fallback to X11 driver if available via XWayland, else Wayland driver
            return LinuxX11PlatformDriver()
        return LinuxX11PlatformDriver()

    elif plat == "darwin":
        # macOS driver fallback to X11 if running under XQuartz or mock
        return LinuxX11PlatformDriver()

    elif plat == "win32":
        from .windows import WindowsPlatformDriver
        return WindowsPlatformDriver()

    return LinuxX11PlatformDriver()

