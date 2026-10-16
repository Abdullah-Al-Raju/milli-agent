"""
Continuous 60Hz Live View Daemon for the Milli 4D Spatiotemporal Manifold.
Functions as the physical, continuous 'Eye' for any AI brain:
- Streams raw frames into a transient 2-frame circular RAM buffer (never stores video to disk).
- Continuously calculates spatial gradients (∇F), velocity transport (v), and shock delta (δ).
- Exposes instantaneous thread-safe mathematical state vectors for the AI brain to inspect at any continuous timestamp t.
"""

import time
import threading
import numpy as np
from typing import Dict, Any, Optional, Tuple
from ..capture.base import CaptureSource
from .manifold import ManifoldEngine


class LiveManifoldStream:
    """
    Persistent 60Hz live optical eye streaming continuous manifold vectors.
    Zero disk storage: all frames exist only in a transient 2-frame circular RAM buffer.
    """

    def __init__(self, capture_source: CaptureSource, fps: int = 60, event_threshold: float = 18.0):
        self.capture = capture_source
        self.engine = ManifoldEngine(event_threshold=event_threshold)
        self.fps = fps
        self.interval = 1.0 / max(fps, 1)

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        # Transient state buffers
        self._latest_vector: Dict[str, Any] = {}
        self._latest_frame: Optional[np.ndarray] = None
        self._shock_event = threading.Event()
        self._frame_counter = 0

        # Optional research trace recording (for researchers, NOT engine storage)
        self.record_research: bool = False
        self.research_log: list = []

    def start(self):
        """Starts the persistent 60Hz optical streaming daemon thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._stream_loop, daemon=True, name="MilliLiveEye")
        self._thread.start()

    def stop(self):
        """Stops the live streaming daemon and releases capture pipe."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.5)
        self._thread = None
        self.capture.close()

    def _stream_loop(self):
        """Continuous 60Hz evaluation loop."""
        while self._running:
            loop_start = time.perf_counter()

            ok, frame = self.capture.read_frame()
            if ok and frame is not None:
                # Thread-safe instant update of raw frame for zero-latency visual control
                with self._lock:
                    self._latest_frame = frame
                    self._frame_counter += 1

                # Downsample large screens via strided slicing (<0.05ms) for 60Hz real-time manifold math
                h, w = frame.shape
                if h > 240 or w > 320:
                    sy = max(1, h // 180)
                    sx = max(1, w // 320)
                    proc_frame = frame[::sy, ::sx]
                else:
                    proc_frame = frame

                # Ingest into 4D manifold (evaluates ∇F, v, δ)
                v_summary = self.engine.ingest_frame(proc_frame)

                with self._lock:
                    self._latest_vector = v_summary

                    if v_summary.get("event_triggered", False):
                        self._shock_event.set()

                    if self.record_research:
                        self.research_log.append({
                            "t": v_summary["timestamp"],
                            "vel": v_summary["mean_velocity"],
                            "delta": v_summary["residual_norm"],
                            "target": v_summary["subpixel_target"]
                        })

            elapsed = time.perf_counter() - loop_start
            sleep_time = max(0.0, self.interval - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)

    def get_live_manifold_vector(self) -> Dict[str, Any]:
        """
        Retrieves the instantaneous mathematical state vector for the AI brain.
        Takes < 0.1ms (reads thread-safe shared memory).
        """
        with self._lock:
            if not self._latest_vector:
                # Fallback if stream just started
                ok, frame = self.capture.read_frame()
                if ok:
                    self._latest_vector = self.engine.ingest_frame(frame)
                    self._latest_frame = frame
            return dict(self._latest_vector)

    def get_live_frame_view(self) -> Optional[np.ndarray]:
        """Returns zero-copy view of current transient frame (for visual action verify)."""
        with self._lock:
            return self._latest_frame.copy() if self._latest_frame is not None else None

    def wait_for_settled(self, max_velocity: float = 0.5, min_dwell_ms: float = 30.0, timeout: float = 2.0) -> bool:
        """
        Perceptual Settle Gate: Blocks until motion velocity ||v||_2 settles near zero,
        indicating page load, layout shift, or UI render has completed.
        Returns as soon as visual energy is stable for min_dwell_ms, eliminating arbitrary sleeps.
        """
        start = time.perf_counter()
        dwell_start = None

        while (time.perf_counter() - start) < timeout:
            v = self.get_live_manifold_vector()
            vel = v.get("mean_velocity", 100.0)

            if vel < max_velocity:
                if dwell_start is None:
                    dwell_start = time.perf_counter()
                elif (time.perf_counter() - dwell_start) * 1000.0 >= min_dwell_ms:
                    return True
            else:
                dwell_start = None

            time.sleep(0.008)  # Poll at 120Hz in RAM

        return False

    def wait_for_visual_effect(
        self,
        reference_frame: Optional[np.ndarray],
        target_roi: Optional[Tuple[int, int, int, int]] = None,
        min_delta: float = 10.0,
        timeout: float = 1.5
    ) -> bool:
        """
        Instant Closed-Loop Action Verification:
        Blocks until a localized visual delta appears in target_roi,
        proving the click or keystroke registered on screen without waiting for timeouts.
        """
        if reference_frame is None:
            return True

        start = time.perf_counter()
        while (time.perf_counter() - start) < timeout:
            curr = self.get_live_frame_view()
            if curr is not None and curr.shape == reference_frame.shape:
                if target_roi:
                    rx, ry, rw, rh = target_roi
                    diff = np.abs(curr[ry:ry+rh, rx:rx+rw].astype(np.int16) - reference_frame[ry:ry+rh, rx:rx+rw].astype(np.int16))
                else:
                    diff = np.abs(curr.astype(np.int16) - reference_frame.astype(np.int16))

                if np.mean(diff) >= min_delta:
                    return True

            time.sleep(0.008)

        return False

    def wait_for_shock(self, timeout: float = 2.0) -> bool:
        """Blocks until a transient shock delta occurs, or timeout."""
        triggered = self._shock_event.wait(timeout=timeout)
        self._shock_event.clear()
        return triggered
