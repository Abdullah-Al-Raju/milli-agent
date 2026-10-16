"""
Video File and Stream Capture Provider.
Utilizes ffmpeg pipe for zero-dependency frame ingestion.
"""

import subprocess
import numpy as np
from typing import Tuple
from .base import CaptureSource


class VideoCaptureSource(CaptureSource):
    """
    Ingests video streams or files (MP4, WebM, MKV) via lightweight ffmpeg pipe.
    """

    def __init__(self, video_path: str, width: int = 720, height: int = 720, loop: bool = True):
        self.video_path = video_path
        self.width = width
        self.height = height
        self.loop = loop
        self.frame_size = width * height
        self.proc = None
        self._spawn_process()

    def _spawn_process(self):
        if self.proc is not None:
            self.proc.terminate()
            self.proc.wait()

        cmd = [
            'ffmpeg', '-v', 'error',
            '-i', self.video_path,
            '-vf', f'scale={self.width}:{self.height}',
            '-f', 'rawvideo',
            '-pix_fmt', 'gray',
            '-'
        ]
        self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    def read_frame(self) -> Tuple[bool, np.ndarray]:
        if self.proc is None:
            return False, np.zeros((self.height, self.width), dtype=np.uint8)

        raw = self.proc.stdout.read(self.frame_size)
        if len(raw) < self.frame_size:
            if self.loop:
                self._spawn_process()
                raw = self.proc.stdout.read(self.frame_size)
                if len(raw) < self.frame_size:
                    return False, np.zeros((self.height, self.width), dtype=np.uint8)
            else:
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
