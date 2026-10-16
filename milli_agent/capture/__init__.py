import sys
from .base import CaptureSource
from .video import VideoCaptureSource
from .x11 import X11CaptureSource
from .windows import WindowsCaptureSource
from .mock import MockCanvaDesktopSource


def get_default_capture_source(fps: int = 60) -> CaptureSource:
    """Returns the optimal native CaptureSource for the host operating system."""
    if sys.platform == "win32":
        return WindowsCaptureSource(fps=fps)
    return X11CaptureSource(fps=fps)


__all__ = [
    "CaptureSource",
    "VideoCaptureSource",
    "X11CaptureSource",
    "WindowsCaptureSource",
    "MockCanvaDesktopSource",
    "get_default_capture_source"
]

