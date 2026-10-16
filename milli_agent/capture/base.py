"""
Abstract Framebuffer Capture Interface.
"""

from abc import ABC, abstractmethod
import numpy as np
from typing import Tuple


class CaptureSource(ABC):
    """
    Standard interface for all screen / window / video capture providers.
    """

    @abstractmethod
    def read_frame(self) -> Tuple[bool, np.ndarray]:
        """
        Returns:
            success: bool indicating if frame was captured
            frame_gray: 2D uint8 numpy array of shape (height, width)
        """
        pass

    @abstractmethod
    def get_dimensions(self) -> Tuple[int, int]:
        """Returns (width, height)"""
        pass

    @abstractmethod
    def close(self):
        """Releases underlying hardware / process resources."""
        pass

    def to_physical(self, norm_x: float, norm_y: float) -> Tuple[float, float]:
        """Convert normalized [0.0, 1.0] coordinates to physical screen pixels."""
        w, h = self.get_dimensions()
        return norm_x * w, norm_y * h

    def to_normalized(self, phys_x: float, phys_y: float) -> Tuple[float, float]:
        """Convert physical screen pixels to normalized [0.0, 1.0] coordinates."""
        w, h = self.get_dimensions()
        w = max(w, 1)
        h = max(h, 1)
        return phys_x / w, phys_y / h
