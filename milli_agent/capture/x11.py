"""
Linux X11 Desktop Framebuffer Capture Provider.
Captures live desktop screens via low-latency ffmpeg x11grab pipe.
"""

import os
import subprocess
import numpy as np
from typing import Tuple
from .base import CaptureSource


class X11CaptureSource(CaptureSource):
    """
    Captures live X11 desktop screen at high framerates (30-60 Hz).
    """

    def __init__(self, display: str = None, width: int = None, height: int = None, fps: int = 60):
        self.display = display or os.environ.get('DISPLAY', ':0.0')
        self.fps = fps
        self.screen_width, self.screen_height = self._detect_screen_resolution()
        self.width = width or self.screen_width
        self.height = height or self.screen_height
        self.frame_size = self.width * self.height
        self.proc = None
        self._spawn_process()

    def _detect_screen_resolution(self) -> Tuple[int, int]:
        """
        Dynamically auto-detect screen resolution using xrandr or xdpyinfo.
        Falls back to 1366x768 if detection is unavailable.
        """
        try:
            res = subprocess.run(
                ["xrandr", "--current"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                check=False
            )
            if res.returncode == 0 and res.stdout:
                # Look for 'current 1366 x 768' in line 'Screen 0: ... current W x H'
                import re
                match = re.search(r"current\s+(\d+)\s+x\s+(\d+)", res.stdout)
                if match:
                    return int(match.group(1)), int(match.group(2))
        except Exception:
            pass

        try:
            res = subprocess.run(
                ["xdpyinfo"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                check=False
            )
            if res.returncode == 0 and res.stdout:
                import re
                match = re.search(r"dimensions:\s+(\d+)x(\d+)\s+pixels", res.stdout)
                if match:
                    return int(match.group(1)), int(match.group(2))
        except Exception:
            pass

        return 1366, 768

    def _spawn_process(self):
        cmd = [
            'ffmpeg', '-v', 'error',
            '-f', 'x11grab',
            '-framerate', str(self.fps),
            '-video_size', f'{self.screen_width}x{self.screen_height}',
            '-i', self.display,
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
        if self.proc is None:
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

