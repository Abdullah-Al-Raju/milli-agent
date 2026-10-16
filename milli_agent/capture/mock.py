"""
Synthetic Desktop & Canva/Browser Simulation Provider.
Generates realistic desktop frames with browser chrome, canvas tools,
and dynamic cursor movement for headless testing and zero-setup demos.
"""

import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple
from .base import CaptureSource


class MockCanvaDesktopSource(CaptureSource):
    """
    Simulates a 1280x720 desktop running a browser with Canva/Moodboard open.
    Features:
    - Browser address bar (https://canva.com/design/moodboard-cat)
    - Tool palette (Brush, Shapes, Colors)
    - Dynamic cursor & drawn strokes
    """

    def __init__(self, width: int = 1280, height: int = 720):
        self.width = width
        self.height = height
        self.t0 = time.time()
        self.drawn_strokes = []

    def add_stroke(self, x0: float, y0: float, x1: float, y1: float):
        self.drawn_strokes.append((x0, y0, x1, y1))

    def read_frame(self) -> Tuple[bool, np.ndarray]:
        t = time.time() - self.t0
        img = Image.new('L', (self.width, self.height), color=25)
        draw = ImageDraw.Draw(img)

        # 1. Desktop Background & Taskbar
        draw.rectangle([0, self.height - 40, self.width, self.height], fill=35)
        draw.text((15, self.height - 28), "Milli OS Agent Active (60 Hz)", fill=160)

        # 2. Browser Window Chrome
        draw.rectangle([60, 40, self.width - 60, self.height - 60], fill=40, outline=60, width=2)
        # Window Title bar
        draw.rectangle([60, 40, self.width - 60, 80], fill=30)
        draw.ellipse([75, 55, 87, 67], fill=180)  # red dot
        draw.ellipse([95, 55, 107, 67], fill=140)
        draw.ellipse([115, 55, 127, 67], fill=100)
        draw.text((140, 54), "Canva — Moodboard: Milli Cat Mascot", fill=200)

        # URL Bar
        draw.rectangle([280, 88, self.width - 280, 115], fill=50, outline=80)
        draw.text((290, 95), "https://www.canva.com/design/milli-cat-moodboard", fill=170)

        # 3. Canva Toolbar (Left Sidebar)
        draw.rectangle([60, 120, 220, self.height - 60], fill=35)
        tools = ["Templates", "Elements", "Draw (Active)", "Text", "Uploads"]
        for idx, tool in enumerate(tools):
            y = 140 + idx * 45
            is_active = "Draw" in tool
            draw.rectangle([75, y, 205, y + 35], fill=70 if is_active else 45)
            draw.text((85, y + 10), tool, fill=255 if is_active else 160)

        # 4. Canvas Whiteboard Area
        canvas_rect = [250, 140, self.width - 90, self.height - 90]
        draw.rectangle(canvas_rect, fill=240, outline=200, width=2)
        draw.text((270, 155), "Canva Whiteboard — Draw Milli Mascot (Cat)", fill=60)

        # Draw any recorded strokes from agent
        for (x0, y0, x1, y1) in self.drawn_strokes:
            draw.line([(x0, y0), (x1, y1)], fill=20, width=4)

        # Dynamic cursor sweep across canvas
        cursor_x = 450 + int(np.sin(t * 3.0) * 180)
        cursor_y = 350 + int(np.cos(t * 2.2) * 120)
        draw.polygon([(cursor_x, cursor_y), (cursor_x + 12, cursor_y + 12), (cursor_x + 4, cursor_y + 14)], fill=10)

        frame = np.array(img, dtype=np.uint8)
        return True, frame

    def get_dimensions(self) -> Tuple[int, int]:
        return self.width, self.height

    def close(self):
        pass
