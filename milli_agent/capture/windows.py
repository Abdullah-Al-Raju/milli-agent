"""
Windows Desktop Framebuffer Capture Provider for Milli-Agent.
Captures live desktop screens via ffmpeg gdigrab or direct ctypes GDI BitBlt into RAM.
"""

import sys
import subprocess
import numpy as np
from typing import Tuple
from .base import CaptureSource


class WindowsCaptureSource(CaptureSource):
    """
    High-speed Windows desktop screen capture into transient RAM.
    """

    def __init__(self, width: int = None, height: int = None, fps: int = 60):
        self.fps = fps
        self.width = width or 1920
        self.height = height or 1080
        self.frame_size = self.width * self.height
        self.proc = None
        self._spawn_process()

    def _spawn_process(self):
        cmd = [
            'ffmpeg', '-v', 'error',
            '-f', 'gdigrab',
            '-framerate', str(self.fps),
            '-i', 'desktop',
            '-vf', f'scale={self.width}:{self.height}',
            '-f', 'rawvideo',
            '-pix_fmt', 'gray',
            '-'
        ]
        try:
            self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        except Exception:
            self.proc = None

    def read_frame(self) -> Tuple[bool, np.ndarray]:
        if self.proc is None or self.proc.stdout is None:
            return False, np.zeros((self.height, self.width), dtype=np.uint8)

        raw = self.proc.stdout.read(self.frame_size)
        if len(raw) < self.frame_size:
            return False, np.zeros((self.height, self.width), dtype=np.uint8)

        frame = np.frombuffer(raw, dtype=np.uint8).reshape((self.height, self.width))
        return True, frame

    def get_dimensions(self) -> Tuple[int, int]:
        return self.width, self.height

    def close(self):
        if self.proc:
            try:
                self.proc.terminate()
                self.proc.wait(timeout=1.0)
            except Exception:
                pass
            self.proc = None
