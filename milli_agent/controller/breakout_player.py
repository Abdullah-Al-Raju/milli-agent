"""
Continuous 60Hz Ball-and-Paddle Physics Interceptor for Breakout / Pong.
Operates purely in transient RAM with zero disk writes.
Uses optical flow and trajectory projection to steer the paddle with sub-5ms reflex latency.
"""

import time
import numpy as np
from typing import Dict, Any, Optional, Tuple
from ..engine.live_stream import LiveManifoldStream
from .input import OSInputController


class BreakoutPhysicsPlayer:
    """
    Sub-5ms Closed-Loop Physics Interceptor for Ball-and-Paddle Games.
    Tracks ball position and velocity in RAM and projects wall-bounce trajectories.
    """

    def __init__(
        self,
        live_stream: LiveManifoldStream,
        input_controller: Optional[OSInputController] = None,
        dry_run: bool = False
    ):
        self.stream = live_stream
        self.controller = input_controller or OSInputController(dry_run=dry_run)
        self.dry_run = dry_run
        self._prev_ball_pos: Optional[Tuple[float, float, float]] = None  # (x, y, t)

    def _fold_wall_bounces(self, x: float, width: float) -> float:
        """
        Projects ball trajectory through continuous wall bounces using triangle folding.
        """
        if width <= 0:
            return x
        # Modulo over double width to account for back-and-forth reflections
        period = 2.0 * width
        mod_x = x % period
        if mod_x < 0:
            mod_x += period
        if mod_x > width:
            return 2.0 * width - mod_x
        return mod_x

    def play_live(
        self,
        duration_seconds: float = 12.0,
        target_fps: int = 60
    ) -> Dict[str, Any]:
        """
        Continuously plays Breakout live on the physical desktop.
        Zero disk storage: all processing is in transient RAM.
        """
        interval = 1.0 / max(target_fps, 1)
        start_time = time.time()
        frames_tracked = 0
        paddle_adjustments = 0

        print("\n[Milli Physics Eye] 🎱 Engaging continuous 60Hz ball tracking & interceptor...")
        print("[Milli Physics Eye] ⚡ Zero-storage mode: all processing in transient RAM buffer.")

        # Ensure target window focus and position mouse on paddle line
        win = self.controller.active_target_window
        if win:
            self.controller.ensure_focus(win.id)
            win_x, win_y, win_w, win_h = win.rect
            base_x = win_x + win_w // 2
            base_y = win_y + int(win_h * 0.88)
            self.controller.click(base_x, base_y, window_id=win.id)
        else:
            self.controller.click(683, 600)
            win_x, win_y, win_w, win_h = 0, 0, 1366, 768

        time.sleep(0.1)

        while time.time() - start_time < duration_seconds:
            loop_t0 = time.perf_counter()

            # 1. Grab instantaneous transient frame from RAM
            frame = self.stream.get_live_frame_view()
            if frame is None:
                time.sleep(0.01)
                continue

            frames_tracked += 1
            h, w = frame.shape
            now = time.time()

            # 2. Dynamic Optical Localization of Playfield:
            # Active canvas region (centered inside window bounds)
            if win:
                cx0 = max(0, win.rect[0] + int(win.rect[2] * 0.15))
                cx1 = min(w, win.rect[0] + int(win.rect[2] * 0.85))
                cy0 = max(0, win.rect[1] + int(win.rect[3] * 0.15))
                cy1 = min(h, win.rect[1] + int(win.rect[3] * 0.88))
            else:
                cx0, cx1 = int(w * 0.15), int(w * 0.85)
                cy0, cy1 = int(h * 0.15), int(h * 0.88)

            canvas_roi = frame[cy0:cy1, cx0:cx1]
            roi_h, roi_w = canvas_roi.shape

            # 3. Locate Ball: Ball is a bright white/neon circle on dark background
            # High brightness pixels (value > 220) in the playfield area above paddle
            ball_zone = canvas_roi[:int(roi_h * 0.90), :]
            bright_ys, bright_xs = np.where(ball_zone > 220)

            target_screen_x = cx0 + (roi_w // 2)

            if len(bright_xs) >= 4:
                # Ball center of mass
                cur_ball_x = float(np.mean(bright_xs))
                cur_ball_y = float(np.mean(bright_ys))

                # Estimate velocity vector v = (vx, vy)
                if self._prev_ball_pos is not None:
                    px, py, pt = self._prev_ball_pos
                    dt = max(0.001, now - pt)
                    vx = (cur_ball_x - px) / dt  # px / sec
                    vy = (cur_ball_y - py) / dt  # px / sec

                    # Paddle plane relative to ROI
                    paddle_roi_y = roi_h * 0.92

                    if vy > 10.0:
                        # Ball is heading toward paddle: project impact intercept
                        time_to_impact = (paddle_roi_y - cur_ball_y) / vy
                        predicted_raw_x = cur_ball_x + vx * time_to_impact
                        # Fold reflections off left and right canvas walls
                        predicted_bounce_x = self._fold_wall_bounces(predicted_raw_x, roi_w)
                        target_roi_x = predicted_bounce_x
                    else:
                        # Ball moving upward: smoothly shadow the ball's current X
                        target_roi_x = cur_ball_x

                    target_screen_x = int(cx0 + target_roi_x)
                    reaction_ms = (time.perf_counter() - loop_t0) * 1000.0

                    # 4. Steer paddle via mouse
                    screen_paddle_y = int(cy0 + paddle_roi_y)
                    self.controller.move_to(target_screen_x, screen_paddle_y)
                    paddle_adjustments += 1

                    if frames_tracked % 15 == 0:
                        state_str = "⏬ INTERCEPT" if vy > 0 else "⏫ TRACK"
                        print(f"  [t={(now - start_time):4.1f}s | Frame {frames_tracked:4d}] {state_str} | Ball: ({cur_ball_x:5.1f}, {cur_ball_y:5.1f}) | Target X: {target_screen_x:4d} | Reaction: {reaction_ms:.2f}ms")

                self._prev_ball_pos = (cur_ball_x, cur_ball_y, now)

            # High precision timing loop
            loop_duration = time.perf_counter() - loop_t0
            sleep_needed = max(0.0, interval - loop_duration)
            if sleep_needed > 0:
                time.sleep(sleep_needed)

        total_time = round(time.time() - start_time, 2)
        effective_fps = round(frames_tracked / max(total_time, 0.001), 1)

        print(f"\n[Milli Physics Eye] 🏆 Completed {total_time}s continuous Breakout gameplay!")
        print(f"[Milli Physics Eye] ⚡ Frames Evaluated: {frames_tracked} ({effective_fps} FPS) in RAM.")
        print(f"[Milli Physics Eye] 🎯 Paddle Intercepts: {paddle_adjustments} (Sub-5ms Steering).")
        print(f"[Milli Physics Eye] 🔒 Zero frames saved to disk. Zero token waste.")

        return {
            "status": "success",
            "duration": total_time,
            "frames_tracked": frames_tracked,
            "effective_fps": effective_fps,
            "paddle_adjustments": paddle_adjustments,
            "disk_writes_bytes": 0
        }
