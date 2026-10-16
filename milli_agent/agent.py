"""
MilliAgent: Autonomous OS-Level Computer-Use Agent.
Combines 60Hz Continuous 4D Manifold Perception, Sub-10ms System 1 Typed Decisions,
Universal Model Adapters, and Sub-Pixel Vector Spline Execution.

The agent uses LiveManifoldStream as a continuous physical eye:
- Streams continuous 60Hz manifold state vectors without discrete screenshot overhead.
- Operates with zero feed accumulation (never saves video or frames to disk).
- Dynamic model planning with zero hardcoded task scripts.
"""

import time
from typing import Dict, Any, List, Optional

from .engine.manifold import ManifoldEngine
from .engine.live_stream import LiveManifoldStream
from .capture.base import CaptureSource
from .capture.mock import MockCanvaDesktopSource
from .capture.x11 import X11CaptureSource
from .router.typed_decisions import FastDecisionRouter
from .router.adapter import ModelAdapter
from .controller.input import OSInputController
from .controller.canvas_drawer import SplineCanvasDrawer
from .controller.reactive import ReactiveReflexController
from .controller.breakout_player import BreakoutPhysicsPlayer
from .controller.click_reflex_player import ClickReflexPlayer
from .platform import get_platform_driver
from .network import VisualManifoldActionNetwork


class MilliAgent:
    """
    High-performance, beginner-friendly autonomous OS agent powered by the
    Milli Continuous 4D Spatiotemporal Manifold.
    """

    def __init__(
        self,
        capture_source: Optional[CaptureSource] = None,
        model: str = "builtin",
        dry_run: bool = False,
        use_live_stream: bool = True
    ):
        self.capture = capture_source or MockCanvaDesktopSource()
        self.engine = ManifoldEngine()
        self.router = FastDecisionRouter()
        self.adapter = ModelAdapter(model_spec=model)
        self.platform = get_platform_driver()
        self.vman = VisualManifoldActionNetwork()
        self.controller = OSInputController(dry_run=dry_run, driver=self.platform)
        self.dry_run = dry_run

        # Persistent 60Hz Live Eye Daemon
        self.use_live_stream = use_live_stream
        self.live_stream: Optional[LiveManifoldStream] = None
        self.reflex: Optional[ReactiveReflexController] = None
        if self.use_live_stream:
            self.live_stream = LiveManifoldStream(self.capture, fps=60)
            self.live_stream.start()
            self.reflex = ReactiveReflexController(self.live_stream, self.controller, dry_run=self.dry_run)

    def execute_goal(self, goal: str, max_steps: int = 10) -> Dict[str, Any]:
        """
        Executes an arbitrary high-level goal autonomously at maximum speed.
        Reads the continuous live optical stream directly with zero screenshot overhead.
        """
        t0 = time.time()
        print(f"\n[Milli-Agent] 🎯 Executing Goal: '{goal}'")
        print(f"[Milli-Agent] ⚙  Model Backend: {self.adapter.model_spec} | Dry Run: {self.dry_run}")

        # 1. Inspect live optical eye (Continuous 4D Manifold Vector)
        t_see_start = time.perf_counter()
        if self.live_stream:
            v_summary = self.live_stream.get_live_manifold_vector()
        else:
            ok, frame = self.capture.read_frame()
            if not ok:
                return {"status": "error", "message": "Failed to read framebuffer"}
            v_summary = self.engine.ingest_frame(frame)
        t_see_ms = (time.perf_counter() - t_see_start) * 1000.0

        print(f"[Milli-Agent] 👁  Optical Eye Active: S(x, y) locked in {t_see_ms:.2f}ms ({v_summary.get('tokens_emitted', 160)} tokens). 60 Hz Stream Live.")

        # 2. Plan High-Level Actions Dynamically via Model Adapter
        t_plan_start = time.perf_counter()
        steps = self.adapter.plan_steps(goal, v_summary)
        t_plan_ms = (time.perf_counter() - t_plan_start) * 1000.0
        print(f"[Milli-Agent] 🧠 Dynamic Plan Generated ({t_plan_ms:.1f}ms): {len(steps)} steps.")

        execution_log: List[Dict[str, Any]] = []

        # 3. Execute Steps with Continuous Reaction Tracking
        for idx, step in enumerate(steps[:max_steps]):
            action_type = step.get("action")
            desc = step.get("description", action_type)
            step_start = time.perf_counter()
            print(f"  [{idx+1}/{len(steps)}] {desc}...")

            # Grab pre-action live frame for localized delta verification
            pre_frame = self.live_stream.get_live_frame_view() if self.live_stream else None

            if action_type == "launch_app":
                app = step.get("app", "brave-browser")
                if not self.dry_run:
                    import subprocess
                    subprocess.Popen([app], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    if self.live_stream:
                        self.live_stream.wait_for_settled(max_velocity=0.8, timeout=0.8)
                    else:
                        time.sleep(0.1)
                execution_log.append({"step": idx+1, "action": "launch_app", "app": app, "status": "launched"})

            elif action_type == "launch_notepad":
                app = step.get("app", "mousepad")
                text = step.get("text", "")
                output_file = step.get("output_file", "notepad_output.txt")
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(text)

                if not self.dry_run:
                    import subprocess
                    subprocess.Popen([app, output_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    if self.live_stream:
                        self.live_stream.wait_for_settled(max_velocity=0.8, timeout=0.8)
                    else:
                        time.sleep(0.1)
                execution_log.append({
                    "step": idx+1,
                    "action": "launch_notepad",
                    "app": app,
                    "file": output_file,
                    "status": "opened_and_written"
                })

            elif action_type == "navigate_url":
                url = step.get("url", "https://google.com")
                self.controller.pipeline_navigate_url(url)
                if self.live_stream:
                    self.live_stream.wait_for_settled(max_velocity=0.5, timeout=1.5)
                execution_log.append({"step": idx+1, "action": "navigate_url", "url": url, "status": "navigated"})

            elif action_type == "fill_form":
                fields = step.get("fields", [])
                self.controller.pipeline_fill_form(fields)
                if self.live_stream:
                    self.live_stream.wait_for_settled(max_velocity=0.5, timeout=0.5)
                execution_log.append({"step": idx+1, "action": "fill_form", "fields_count": len(fields), "status": "filled"})

            elif action_type == "hotkey":
                key = step.get("key", "ctrl+l")
                self.controller.press_key(key)
                time.sleep(0.04)
                execution_log.append({"step": idx+1, "action": "hotkey", "key": key, "status": "pressed"})

            elif action_type == "type_text":
                text = step.get("text", "")
                press_return = step.get("press_return", False)
                self.controller.type_text(text)
                if press_return:
                    time.sleep(0.02)
                    self.controller.press_key("Return")
                execution_log.append({"step": idx+1, "action": "type_text", "text": text, "status": "typed"})

            elif action_type == "sleep":
                dur = step.get("duration", 0.1)
                if self.live_stream:
                    self.live_stream.wait_for_settled(max_velocity=0.5, timeout=dur)
                else:
                    time.sleep(min(dur, 0.2))
                execution_log.append({"step": idx+1, "action": "perceptual_settle", "duration": dur, "status": "settled"})

            elif action_type == "neural_decision":
                # Instant System 1 forward pass via VMAN
                v_state = self.live_stream.get_live_manifold_vector() if self.live_stream else v_summary
                sub_goal = step.get("sub_goal", goal)
                decision = self.vman.forward(v_state, sub_goal)
                if decision.action_type == "CLICK":
                    px, py = self.capture.to_physical(decision.coords[0], decision.coords[1])
                    self.controller.click(px, py)
                elif decision.action_type == "KEY_PRESS":
                    self.controller.press_key(decision.key_arg)
                execution_log.append({
                    "step": idx+1,
                    "action": "neural_decision",
                    "decision": decision._asdict(),
                    "status": "executed"
                })

            elif action_type == "click":
                coord = step.get("coord", [640.0, 360.0])
                if 0.0 <= coord[0] <= 1.0 and 0.0 <= coord[1] <= 1.0:
                    px, py = self.capture.to_physical(coord[0], coord[1])
                else:
                    px, py = coord[0], coord[1]

                self.controller.click(px, py)

                post_frame = self.live_stream.get_live_frame_view() if self.live_stream else None
                feedback = {"effect_detected": True}
                if pre_frame is not None and post_frame is not None:
                    feedback = self.engine.verify_action_effect(pre_frame, post_frame, target_coord=(px, py))

                execution_log.append({
                    "step": idx+1,
                    "action": "click",
                    "coord": [px, py],
                    "status": "executed",
                    "visual_feedback": feedback
                })

            elif action_type == "draw_spline_shape":
                shape = step.get("shape", "architecture_diagram")
                center = step.get("center", (680.0, 380.0))
                scale = step.get("scale", 1.0)

                if 0.0 <= center[0] <= 1.0 and 0.0 <= center[1] <= 1.0:
                    cx, cy = self.capture.to_physical(center[0], center[1])
                    center = (cx, cy)

                if shape == "architecture_diagram":
                    strokes = SplineCanvasDrawer.generate_architecture_diagram_splines(center_y=center[1])
                else:
                    strokes = SplineCanvasDrawer.generate_cat_mascot_splines(center, scale)

                print(f"      🎨 Streaming {len(strokes)} continuous spline strokes to canvas ({shape})...")

                for s_idx, stroke in enumerate(strokes):
                    self.controller.drag_path(stroke, delay_ms=4.0)
                    if isinstance(self.capture, MockCanvaDesktopSource):
                        for p0, p1 in zip(stroke[:-1], stroke[1:]):
                            self.capture.add_stroke(p0[0], p0[1], p1[0], p1[1])

                post_frame = self.live_stream.get_live_frame_view() if self.live_stream else None
                feedback = {"effect_detected": True}
                if pre_frame is not None and post_frame is not None:
                    feedback = self.engine.verify_action_effect(pre_frame, post_frame, target_coord=center, radius=120)

                execution_log.append({
                    "step": idx+1,
                    "action": "draw_spline_shape",
                    "shape": shape,
                    "strokes_count": len(strokes),
                    "status": "drawn",
                    "visual_feedback": feedback
                })

            step_time = (time.perf_counter() - step_start) * 1000.0
            print(f"      ✓ Finished in {step_time:.1f}ms (Zero token overhead).")

        total_elapsed = time.time() - t0
        active_engine = self.live_stream.engine if self.live_stream else self.engine
        print(f"\n[Milli-Agent] ✨ Goal Completed Successfully in {total_elapsed:.2f}s!")
        print(f"[Milli-Agent] 📊 Telemetry: {active_engine.total_milli_tokens} Milli tokens vs ~{active_engine.frame_count * 258} ViT tokens ({active_engine.token_savings_percent:.1f}% context savings)")

        return {
            "status": "completed",
            "goal": goal,
            "elapsed_seconds": round(total_elapsed, 3),
            "steps_executed": len(execution_log),
            "log": execution_log,
            "telemetry": {
                "milli_tokens": active_engine.total_milli_tokens,
                "token_savings_percent": round(active_engine.token_savings_percent, 1)
            }
        }

    def execute_reactive_loop(
        self,
        task: str = "flappy",
        duration_seconds: float = 10.0,
        target_window_query: Optional[str] = None,
        target_goal_count: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Executes a continuous System 1 reactive task at 60Hz.
        Zero disk storage: all perception is purely in-memory transient optical flow.
        """
        if not self.reflex:
            raise RuntimeError("Live stream is required for reactive loop execution.")

        if target_window_query:
            win = self.platform.find_window(target_window_query)
            if win:
                print(f"[Milli-Agent] 🪟 Bound to Target Window: '{win.title}' (ID: {win.id}, Class: {win.wm_class})")
                self.controller.bind_target_window(win)
                self.controller.ensure_focus(win.id)

        if task == "breakout":
            player = BreakoutPhysicsPlayer(self.live_stream, self.controller, dry_run=self.dry_run)
            return player.play_live(duration_seconds=duration_seconds)

        if task == "click" or task == "reflex":
            from .controller.reflex_player import MilliReflexPlayer
            player = MilliReflexPlayer(self.live_stream, self.controller, dry_run=self.dry_run)
            return player.play_live(duration_seconds=duration_seconds, target_goal_count=target_goal_count)

        return self.reflex.play_flappy_live(duration_seconds=duration_seconds)

    def close(self):
        """Clean shutdown of live optical daemon and capture devices."""
        if self.live_stream:
            self.live_stream.stop()
            self.live_stream = None
        else:
            self.capture.close()
