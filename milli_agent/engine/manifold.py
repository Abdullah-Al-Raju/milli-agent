"""
Core Continuous 4D Spatiotemporal Manifold Engine.
Decomposes dynamic visual streams into:
    F(x, y, t) = S((x, y) - ∫ v(τ) dτ) + δ(x, y, t)
"""

import time
import numpy as np
from typing import Dict, Any, Optional, Tuple

from .fourier import FourierCoordinateProjector
from .flow import OpticalSplineFlow


class ManifoldEngine:
    """
    Continuous 4D Manifold Engine tracking base scaffolds,
    continuous flow splines, and microsecond residual triggers.
    """

    def __init__(self, event_threshold: float = 18.0):
        self.fourier = FourierCoordinateProjector(num_frequencies=16, scale=10.0)
        self.flow = OpticalSplineFlow(regularization=10.0)
        self.event_threshold = event_threshold

        self.base_manifold: Optional[np.ndarray] = None
        self.base_signature: Optional[Dict[str, Any]] = None
        self.prev_frame: Optional[np.ndarray] = None
        self.t0: float = time.time()
        self.frame_count: int = 0

        # Accumulated metrics
        self.total_vit_tokens: int = 0
        self.total_milli_tokens: int = 0
        self.event_count: int = 0
        self.token_savings_percent: float = 0.0

    def reset(self):
        self.base_manifold = None
        self.base_signature = None
        self.prev_frame = None
        self.t0 = time.time()
        self.frame_count = 0
        self.total_vit_tokens = 0
        self.total_milli_tokens = 0
        self.event_count = 0
        self.token_savings_percent = 0.0

    def ingest_frame(self, frame_gray: np.ndarray, timestamp: float = None) -> Dict[str, Any]:
        """
        Processes a single frame through the continuous 4D manifold engine.
        Returns telemetry, active velocity vectors, and sparse delta triggers.
        """
        if timestamp is None:
            timestamp = time.time() - self.t0

        frame_float = frame_gray.astype(np.float32)
        h, w = frame_float.shape

        # Initial frame locks base manifold S(x, y) or resets on resolution change
        if self.base_manifold is None or self.prev_frame is None or self.prev_frame.shape != frame_float.shape:
            self.base_manifold = frame_float.copy()
            self.base_signature = self.fourier.extract_static_signature(frame_gray)
            self.prev_frame = frame_float.copy()
            self.frame_count = 1
            self.total_milli_tokens += 160  # Initial base manifold token cost
            self.total_vit_tokens += 258
            self.token_savings_percent = 38.0

            return {
                "timestamp": timestamp,
                "is_key_manifold": True,
                "event_triggered": False,
                "residual_norm": 0.0,
                "mean_velocity": 0.0,
                "subpixel_target": (w * 0.5, h * 0.5),
                "tokens_emitted": 160,
                "token_savings_percent": 38.0
            }

        # 1. Evaluate spatial & temporal gradients: Ix, Iy, It
        Ix, Iy, It = self.flow.compute_gradients(self.prev_frame, frame_float)
        u, v = self.flow.estimate_velocity_field(Ix, Iy, It)
        velocity_mag = np.mean(np.sqrt(u**2 + v**2))

        # 2. Sparse Transient Residual Evaluation:
        # δ(x, y, t) = F(x, y, t) - S((x, y) - ∫ v dτ)
        # Approximate instantaneous transport residual
        predicted_It = -(Ix * u + Iy * v)
        residual_field = It - predicted_It
        residual_norm = float(np.mean(np.abs(residual_field)))

        event_triggered = residual_norm > self.event_threshold
        tokens_emitted = 0

        if event_triggered:
            # Microsecond transient or scene cut: fire 18-token alert & refresh key manifold
            tokens_emitted += 18
            self.event_count += 1
            self.base_manifold = frame_float.copy()  # Adaptive Key-Manifold Refresh (AKMR)
        else:
            # Continuous transport streaming (~15 tokens/sec / 30 FPS = ~0.5 tokens/frame)
            tokens_emitted += 1

        self.total_milli_tokens += tokens_emitted
        self.total_vit_tokens += 258  # 1 full ViT frame
        self.frame_count += 1
        self.prev_frame = frame_float.copy()

        # 3. Continuous sub-pixel extrema
        target_x, target_y, target_conf = self.flow.find_subpixel_target(frame_gray)

        token_savings = 100.0 * (1.0 - (self.total_milli_tokens / max(self.total_vit_tokens, 1)))
        self.token_savings_percent = float(token_savings)

        return {
            "timestamp": timestamp,
            "is_key_manifold": event_triggered,
            "event_triggered": event_triggered,
            "residual_norm": residual_norm,
            "mean_velocity": float(velocity_mag),
            "subpixel_target": (target_x, target_y),
            "target_confidence": target_conf,
            "tokens_emitted": tokens_emitted,
            "total_milli_tokens": self.total_milli_tokens,
            "total_vit_tokens": self.total_vit_tokens,
            "token_savings_percent": float(token_savings)
        }

    def verify_action_effect(
        self,
        prev_frame: np.ndarray,
        post_frame: np.ndarray,
        target_coord: Optional[Tuple[float, float]] = None,
        radius: int = 40
    ) -> Dict[str, Any]:
        """
        Calculates localized spatiotemporal delta residual around an executed action
        (e.g. click or drag target) to confirm the UI changed / responded to the action.
        """
        p0 = prev_frame.astype(np.float32)
        p1 = post_frame.astype(np.float32)

        abs_diff = np.abs(p1 - p0)
        global_delta = float(np.mean(abs_diff))

        local_delta = 0.0
        h, w = p0.shape

        if target_coord is not None:
            cx, cy = int(target_coord[0]), int(target_coord[1])
            x0 = max(0, cx - radius)
            x1 = min(w, cx + radius)
            y0 = max(0, cy - radius)
            y1 = min(h, cy + radius)
            if x1 > x0 and y1 > y0:
                local_delta = float(np.mean(abs_diff[y0:y1, x0:x1]))
            else:
                local_delta = global_delta
        else:
            local_delta = global_delta

        # An action is visually confirmed if local perturbation > 2.0 or global perturbation > 1.5
        effect_detected = (local_delta > 2.0) or (global_delta > 1.5)

        return {
            "effect_detected": effect_detected,
            "local_delta": local_delta,
            "global_delta": global_delta,
            "target_coord": target_coord,
            "radius": radius
        }
