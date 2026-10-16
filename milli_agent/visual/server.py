"""
Milli-Agent Visual Streaming Server & AI Multimodal Endpoint.
Serves live 60Hz MJPEG stream, raw frame snapshots, telemetry, and action endpoints in RAM.
Enables AI models and humans to visually see, monitor, and control Milli-Agent.
"""

import io
import os
import sys
import time
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional, Dict, Any
import numpy as np
from PIL import Image

from ..capture import get_default_capture_source
from ..engine.live_stream import LiveManifoldStream
from ..controller.input import OSInputController
from ..brain.decision_bridge import MilliDecisionBridge
from ..platform import get_platform_driver


class VisualRequestHandler(BaseHTTPRequestHandler):
    """
    HTTP handler serving visual dashboard, live MJPEG video stream,
    frame snapshots for AI vision models, and JSON action endpoints.
    """

    @property
    def milli(self) -> 'MilliVisualServer':
        return getattr(self.server, "milli_server", self.server)

    def log_message(self, format, *args):
        # Silence default access logs to preserve terminal clarity
        pass

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self._serve_dashboard()
        elif self.path == "/stream":
            self._serve_mjpeg_stream()
        elif self.path == "/frame" or self.path == "/api/frame":
            self._serve_single_frame()
        elif self.path == "/api/state" or self.path == "/state":
            self._serve_state_json()
        else:
            self.send_error(404, "Endpoint not found")

    def do_POST(self):
        if self.path == "/api/action" or self.path == "/api/execute":
            self._handle_action()
        else:
            self.send_error(404, "Endpoint not found")

    def _serve_dashboard(self):
        html_path = os.path.join(os.path.dirname(__file__), "dashboard.html")
        if os.path.exists(html_path):
            with open(html_path, "rb") as f:
                content = f.read()
        else:
            content = b"<html><body><h1>Milli-Agent Visual Server Online</h1></body></html>"

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _serve_single_frame(self):
        """Serves raw JPEG frame for AI vision models (0 bytes disk)."""
        jpeg_bytes = self.milli.get_latest_jpeg()
        if not jpeg_bytes:
            self.send_error(503, "Camera stream initializing")
            return

        self.send_response(200)
        self.send_header("Content-Type", "image/jpeg")
        self.send_header("Content-Length", str(len(jpeg_bytes)))
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(jpeg_bytes)

    def _serve_mjpeg_stream(self):
        """Continuous multipart MJPEG stream for real-time visual inspection."""
        self.send_response(200)
        self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=--frame")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.end_headers()

        try:
            while self.milli.running:
                jpeg_bytes = self.milli.get_latest_jpeg()
                if jpeg_bytes:
                    self.wfile.write(b"--frame\r\n")
                    self.wfile.write(b"Content-Type: image/jpeg\r\n")
                    self.wfile.write(f"Content-Length: {len(jpeg_bytes)}\r\n\r\n".encode())
                    self.wfile.write(jpeg_bytes)
                    self.wfile.write(b"\r\n")
                time.sleep(0.016)  # ~60 FPS
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _serve_state_json(self):
        state = self.milli.get_telemetry_state()
        payload = json.dumps(state).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)

    def _handle_action(self):
        """Receives JSON action from external AI model or user interface."""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body)

            action = data.get("action", "").lower()
            res = {"status": "ok", "action": action}

            if action == "click":
                x = float(data.get("x", 0))
                y = float(data.get("y", 0))
                btn = int(data.get("button", 1))
                self.milli.controller.click(x, y, button=btn)
                res["coords"] = (x, y)
            elif action == "move":
                x = float(data.get("x", 0))
                y = float(data.get("y", 0))
                self.milli.controller.move_to(x, y)
                res["coords"] = (x, y)
            elif action == "type":
                text = str(data.get("text", ""))
                delay = float(data.get("delay_ms", 1))
                self.milli.controller.type_text(text, delay_ms=delay)
                res["length"] = len(text)
            elif action == "press_key":
                key = str(data.get("key", "return"))
                self.milli.controller.press_key(key)
                res["key"] = key
            elif action == "scroll":
                clicks = int(data.get("clicks", 3))
                direction = str(data.get("direction", "down"))
                self.milli.controller.scroll(clicks=clicks, direction=direction)
                res["scroll"] = (direction, clicks)
            elif action == "evaluate":
                goal = str(data.get("goal", "Execute action"))
                frame_view = self.milli.stream.get_live_frame_view()
                targets = []
                if frame_view is not None:
                    ys, xs = np.where(frame_view > 220)
                    if len(xs) > 20:
                        targets.append({"screen_x": int(xs.mean()), "screen_y": int(ys.mean()), "confidence": 0.95})
                dec = self.milli.bridge.evaluate_scene({"targets": targets}, goal=goal)
                res["decision"] = dec
            else:
                res["status"] = "unrecognized_action"

            payload = json.dumps(res).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(payload)

        except Exception as e:
            err = json.dumps({"error": str(e)}).encode("utf-8")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(err)))
            self.end_headers()
            self.wfile.write(err)


class MilliVisualServer:
    """
    Visual streaming server hosting real-time HUD and AI multimodal endpoints.
    Operates in transient RAM with zero secondary storage writes.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 8765, fps: int = 60, dry_run: bool = False):
        self.host = host
        self.port = port
        self.fps = fps
        self.dry_run = dry_run
        self.running = False

        self.platform = get_platform_driver()
        self.controller = OSInputController(dry_run=dry_run, driver=self.platform)
        self.capture = get_default_capture_source(fps=fps)
        self.stream = LiveManifoldStream(self.capture, fps=fps)
        self.bridge = MilliDecisionBridge()

        self._latest_jpeg: Optional[bytes] = None
        self._lock = threading.Lock()
        self._httpd: Optional[HTTPServer] = None
        self._server_thread: Optional[threading.Thread] = None
        self._encoder_thread: Optional[threading.Thread] = None
        self._frame_count = 0
        self._start_time = time.time()

    def start(self):
        """Starts live optical stream and background HTTP server."""
        self.running = True
        self.stream.start()
        self._start_time = time.time()

        # Start JPEG encoding thread
        self._encoder_thread = threading.Thread(target=self._encode_loop, daemon=True)
        self._encoder_thread.start()

        # Start HTTP server
        handler_class = VisualRequestHandler
        self._httpd = HTTPServer((self.host, self.port), handler_class)
        self._httpd.milli_server = self

        self._server_thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._server_thread.start()

        print("\n" + "="*70)
        print("👁  MILLI-AGENT VISUAL HUD & AI MULTIMODAL SERVER ONLINE")
        print("="*70)
        print(f"  • Visual Dashboard (Human / AI): http://localhost:{self.port}")
        print(f"  • Live Video Stream (MJPEG):      http://localhost:{self.port}/stream")
        print(f"  • Raw Frame Snapshot (AI Vision): http://localhost:{self.port}/frame")
        print(f"  • JSON State & Telemetry:         http://localhost:{self.port}/api/state")
        print(f"  • Action Execution Endpoint:      http://localhost:{self.port}/api/action")
        print(f"  • Host Operating System:          {sys.platform.capitalize()}")
        print(f"  • Storage Footprint:              0 bytes (100% transient RAM)")
        print("="*70 + "\n")

    def _encode_loop(self):
        """Continuously encodes live optical frames into RAM JPEG bytes (~60Hz)."""
        while self.running:
            t0 = time.perf_counter()
            frame = self.stream.get_live_frame_view()
            if frame is not None:
                try:
                    img = Image.fromarray(frame)
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG", quality=75)
                    jpeg_bytes = buf.getvalue()
                    with self._lock:
                        self._latest_jpeg = jpeg_bytes
                        self._frame_count += 1
                except Exception:
                    pass

            elapsed = time.perf_counter() - t0
            sleep_needed = max(0.0, (1.0 / self.fps) - elapsed)
            time.sleep(sleep_needed)

    def get_latest_jpeg(self) -> Optional[bytes]:
        with self._lock:
            return self._latest_jpeg

    def get_telemetry_state(self) -> Dict[str, Any]:
        elapsed = time.time() - self._start_time
        effective_fps = round(self._frame_count / max(elapsed, 0.001), 1)
        active_win = self.platform.get_active_window()
        res_w, res_h = self.platform.get_screen_resolution()

        return {
            "status": "online",
            "uptime_seconds": round(elapsed, 1),
            "effective_fps": effective_fps,
            "resolution": [res_w, res_h],
            "active_window": active_win.title if active_win else "Unknown",
            "active_window_id": active_win.id if active_win else None,
            "platform": sys.platform,
            "perception_memory": "Circular RAM Buffer (0 bytes disk)"
        }

    def stop(self):
        """Shuts down server and releases optical capture resources."""
        self.running = False
        if self._httpd:
            self._httpd.shutdown()
            self._httpd.server_close()
            self._httpd = None
        self.stream.stop()
        self.capture.close()


def main():
    server = MilliVisualServer(host="0.0.0.0", port=8765)
    server.start()
    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        server.stop()


if __name__ == "__main__":
    main()
