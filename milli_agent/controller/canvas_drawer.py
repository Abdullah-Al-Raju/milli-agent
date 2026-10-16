"""
Continuous Spline Stroke Generator for Canvas & Moodboard Drawing.
Generates smooth parametric mathematical spline paths for drawing vector graphics
(e.g., the Milli Cat Mascot) directly on canvas whiteboards (Canva, Figma, Excalidraw, Paint).
"""

import numpy as np
from typing import List, Tuple


class SplineCanvasDrawer:
    """
    Parametric vector spline generator for drawing freehand illustrations at 60 Hz.
    """

    @staticmethod
    def generate_cat_mascot_splines(center: Tuple[float, float], scale: float = 1.0) -> List[List[Tuple[float, float]]]:
        """
        Generates continuous parametric spline paths for the Milli Cat Mascot:
        - Head outline
        - Left & Right triangular ears
        - Left & Right eyes
        - Cat nose & mouth curve
        - Left & Right whiskers
        """
        cx, cy = center
        r = 70.0 * scale
        strokes = []

        # 1. Head Contour (Parametric ellipse with chin tuck)
        head_pts = []
        for theta in np.linspace(0, 2 * np.pi, 36):
            # slightly wider than tall (cute chibi cat ratio)
            x = cx + np.cos(theta) * r * 1.15
            y = cy + np.sin(theta) * r * 0.95
            head_pts.append((float(x), float(y)))
        head_pts.append(head_pts[0])  # Close loop
        strokes.append(head_pts)

        # 2. Left Ear (Triangular spline)
        ear_l = [
            (cx - r * 0.8, cy - r * 0.5),
            (cx - r * 0.95, cy - r * 1.4),
            (cx - r * 0.3, cy - r * 0.85)
        ]
        strokes.append(ear_l)

        # 3. Right Ear
        ear_r = [
            (cx + r * 0.3, cy - r * 0.85),
            (cx + r * 0.95, cy - r * 1.4),
            (cx + r * 0.8, cy - r * 0.5)
        ]
        strokes.append(ear_r)

        # 4. Left Eye & Right Eye (Friendly ovals)
        eye_l = [
            (cx - r * 0.45, cy - r * 0.1),
            (cx - r * 0.35, cy - r * 0.25),
            (cx - r * 0.25, cy - r * 0.1),
            (cx - r * 0.35, cy + r * 0.05),
            (cx - r * 0.45, cy - r * 0.1)
        ]
        eye_r = [
            (cx + r * 0.25, cy - r * 0.1),
            (cx + r * 0.35, cy - r * 0.25),
            (cx + r * 0.45, cy - r * 0.1),
            (cx + r * 0.35, cy + r * 0.05),
            (cx + r * 0.25, cy - r * 0.1)
        ]
        strokes.append(eye_l)
        strokes.append(eye_r)

        # 5. Nose (Small triangle)
        nose = [
            (cx - r * 0.08, cy + r * 0.15),
            (cx + r * 0.08, cy + r * 0.15),
            (cx, cy + r * 0.25),
            (cx - r * 0.08, cy + r * 0.15)
        ]
        strokes.append(nose)

        # 6. Mouth / Smile (W-curve)
        mouth_l = [
            (cx, cy + r * 0.25),
            (cx - r * 0.15, cy + r * 0.38),
            (cx - r * 0.28, cy + r * 0.30)
        ]
        mouth_r = [
            (cx, cy + r * 0.25),
            (cx + r * 0.15, cy + r * 0.38),
            (cx + r * 0.28, cy + r * 0.30)
        ]
        strokes.append(mouth_l)
        strokes.append(mouth_r)

        # 7. Left Whiskers (3 whiskers)
        w_l1 = [(cx - r * 0.5, cy + r * 0.15), (cx - r * 1.3, cy + r * 0.05)]
        w_l2 = [(cx - r * 0.5, cy + r * 0.25), (cx - r * 1.35, cy + r * 0.25)]
        w_l3 = [(cx - r * 0.5, cy + r * 0.35), (cx - r * 1.25, cy + r * 0.45)]
        strokes.extend([w_l1, w_l2, w_l3])

        # 8. Right Whiskers (3 whiskers)
        w_r1 = [(cx + r * 0.5, cy + r * 0.15), (cx + r * 1.3, cy + r * 0.05)]
        w_r2 = [(cx + r * 0.5, cy + r * 0.25), (cx + r * 1.35, cy + r * 0.25)]
        w_r3 = [(cx + r * 0.5, cy + r * 0.35), (cx + r * 1.25, cy + r * 0.45)]
        strokes.extend([w_r1, w_r2, w_r3])

        return strokes

    @staticmethod
    def generate_architecture_diagram_splines(
        center_y: float = 380.0,
        box_w: float = 180.0,
        box_h: float = 90.0
    ) -> List[List[Tuple[float, float]]]:
        """
        Generates continuous vector splines for 3 connected architecture boxes:
        [Client (Potato Silicon)] -> [Milli 4D Engine] -> [AI Brain]
        Including box perimeters and directional connecting arrows.
        """
        strokes = []

        # Box Centers
        c_client = (280.0, center_y)
        c_milli = (580.0, center_y)
        c_brain = (880.0, center_y)

        def make_rect(cx, cy, w, h):
            x0, x1 = cx - w/2, cx + w/2
            y0, y1 = cy - h/2, cy + h/2
            return [
                (x0, y0), (x1, y0),
                (x1, y1), (x0, y1),
                (x0, y0)
            ]

        def make_arrow(start_x, end_x, y):
            stem = [(start_x, y), (end_x, y)]
            head_top = [(end_x - 14, y - 8), (end_x, y)]
            head_bot = [(end_x - 14, y + 8), (end_x, y)]
            return [stem, head_top, head_bot]

        # 1. Box 1: Client
        strokes.append(make_rect(c_client[0], c_client[1], box_w, box_h))

        # 2. Arrow 1: Client -> Milli
        arr1 = make_arrow(c_client[0] + box_w/2, c_milli[0] - box_w/2, center_y)
        strokes.extend(arr1)

        # 3. Box 2: Milli Engine
        strokes.append(make_rect(c_milli[0], c_milli[1], box_w, box_h))

        # 4. Arrow 2: Milli -> Brain
        arr2 = make_arrow(c_milli[0] + box_w/2, c_brain[0] - box_w/2, center_y)
        strokes.extend(arr2)

        # 5. Box 3: Brain
        strokes.append(make_rect(c_brain[0], c_brain[1], box_w, box_h))

        return strokes

