"""
Abstract OS Platform Driver for Milli-Agent.
Provides deterministic cross-platform primitives for window inspection,
verified focus management, and native event dispatching without guessing.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field


class WindowInfo(BaseModel):
    """
    Metadata representation of an OS window.
    """
    id: int = Field(description="Platform window identifier (XID, HWND, or CGWindowID)")
    title: str = Field(default="", description="Window title string")
    wm_class: str = Field(default="", description="Window class or bundle identifier")
    pid: int = Field(default=0, description="Process ID owning the window")
    rect: Tuple[int, int, int, int] = Field(default=(0, 0, 0, 0), description="(x, y, width, height) of window frame")
    client_rect: Tuple[int, int, int, int] = Field(default=(0, 0, 0, 0), description="(x, y, width, height) of client canvas")
    is_active: bool = Field(default=False, description="True if window currently holds OS input focus")


class OSPlatformDriver(ABC):
    """
    Abstract driver for operating system interactions.
    Subclasses implement Linux (X11/Wayland), macOS, and Windows specifics.
    """

    @abstractmethod
    def get_platform_name(self) -> str:
        """Returns platform identifier string (e.g. 'linux_x11', 'macos', 'windows')."""
        pass

    @abstractmethod
    def get_screen_resolution(self) -> Tuple[int, int]:
        """Returns desktop display resolution as (width, height)."""
        pass

    @abstractmethod
    def list_windows(self) -> List[WindowInfo]:
        """Lists all visible top-level windows currently managed by the desktop."""
        pass

    @abstractmethod
    def get_active_window(self) -> Optional[WindowInfo]:
        """Retrieves the window that currently owns OS input focus."""
        pass

    @abstractmethod
    def find_window(self, query: str) -> Optional[WindowInfo]:
        """Finds the best matching window by title or class substring."""
        pass

    @abstractmethod
    def focus_window(self, window_id: int) -> bool:
        """Brings the window to the foreground and verifies input focus."""
        pass

    @abstractmethod
    def send_key_to_window(self, window_id: int, key: str) -> bool:
        """Directs a keyboard event to the specified window with verified focus."""
        pass

    @abstractmethod
    def send_click_to_window(self, window_id: int, x: int, y: int, button: int = 1) -> bool:
        """Directs a mouse click at screen coordinates (x, y) with verified focus."""
        pass
