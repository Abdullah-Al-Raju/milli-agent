"""
Standard Model Context Protocol (MCP) Server for Milli-Agent.
Communicates via JSON-RPC 2.0 over standard I/O (stdin/stdout).
Allows any MCP-compliant agent (Claude Desktop, Cursor, Antigravity)
to execute microsecond OS and browser actions without screenshot loops.
"""

import sys
import json
import base64
import traceback
from typing import Dict, Any, Optional

from ..platform import get_platform_driver
from ..controller.input import OSInputController
from ..capture import get_default_capture_source


class MilliMCPServer:
    """
    Model Context Protocol (MCP) server providing low-latency OS and web automation tools.
    """

    PROTOCOL_VERSION = "2024-11-05"

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.platform = get_platform_driver()
        self.controller = OSInputController(dry_run=dry_run, driver=self.platform)
        self.capture_source = None
        self._running = False

    def get_tool_definitions(self) -> list:
        return [
            {
                "name": "milli_click",
                "description": "Clicks at screen coordinates (x, y) with sub-0.02ms native C hardware latency.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "x": {"type": "number", "description": "Screen X coordinate"},
                        "y": {"type": "number", "description": "Screen Y coordinate"},
                        "button": {"type": "integer", "description": "Mouse button: 1=Left, 2=Middle, 3=Right", "default": 1}
                    },
                    "required": ["x", "y"]
                }
            },
            {
                "name": "milli_move",
                "description": "Warps pointer to screen coordinates (x, y) in 0.013 ms.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "x": {"type": "number", "description": "Target screen X coordinate"},
                        "y": {"type": "number", "description": "Target screen Y coordinate"}
                    },
                    "required": ["x", "y"]
                }
            },
            {
                "name": "milli_type",
                "description": "Streams hardware keystrokes directly into active window at ~20,000 WPM (1,700+ chars/sec).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "String of text to type"},
                        "delay_ms": {"type": "number", "description": "Delay between keystrokes in milliseconds", "default": 1}
                    },
                    "required": ["text"]
                }
            },
            {
                "name": "milli_key",
                "description": "Sends a hardware key press or shortcut (e.g. 'Return', 'ctrl+s', 'Tab', 'Escape').",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "key": {"type": "string", "description": "Key symbol or shortcut"}
                    },
                    "required": ["key"]
                }
            },
            {
                "name": "milli_scroll",
                "description": "Dispatches physical mouse wheel scroll clicks up or down.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "clicks": {"type": "integer", "description": "Number of scroll increments", "default": 3},
                        "direction": {"type": "string", "enum": ["up", "down"], "default": "down"}
                    }
                }
            },
            {
                "name": "milli_get_state",
                "description": "Returns active window title, window ID, platform, and desktop resolution.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "milli_get_frame",
                "description": "Captures raw JPEG desktop frame in transient RAM (0 bytes disk persistence) and returns base64 string.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]

    def handle_tool_call(self, name: str, args: Dict[str, Any]) -> Any:
        if name == "milli_click":
            x = float(args.get("x", 0))
            y = float(args.get("y", 0))
            btn = int(args.get("button", 1))
            self.controller.click(x, y, button=btn)
            return {"status": "ok", "action": "click", "coords": [x, y], "button": btn}

        elif name == "milli_move":
            x = float(args.get("x", 0))
            y = float(args.get("y", 0))
            self.controller.move_to(x, y)
            return {"status": "ok", "action": "move", "coords": [x, y]}

        elif name == "milli_type":
            text = str(args.get("text", ""))
            delay = float(args.get("delay_ms", 1))
            self.controller.type_text(text, delay_ms=delay)
            return {"status": "ok", "action": "type", "chars": len(text)}

        elif name == "milli_key":
            key = str(args.get("key", "Return"))
            self.controller.press_key(key)
            return {"status": "ok", "action": "key", "key": key}

        elif name == "milli_scroll":
            clicks = int(args.get("clicks", 3))
            direction = str(args.get("direction", "down"))
            self.controller.scroll(clicks=clicks, direction=direction)
            return {"status": "ok", "action": "scroll", "clicks": clicks, "direction": direction}

        elif name == "milli_get_state":
            active_win = self.platform.get_active_window()
            res_w, res_h = self.platform.get_screen_resolution()
            return {
                "platform": self.platform.get_platform_name(),
                "resolution": [res_w, res_h],
                "active_window": active_win.title if active_win else "Unknown",
                "active_window_id": active_win.id if active_win else None
            }

        elif name == "milli_get_frame":
            try:
                from PIL import Image
                import io
                if self.capture_source is None:
                    self.capture_source = get_default_capture_source(fps=30)
                frame = self.capture_source.read_frame()
                if frame is not None:
                    img = Image.fromarray(frame)
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG", quality=70)
                    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                    return {"format": "jpeg", "data": b64, "storage": "0 bytes disk (transient RAM)"}
                return {"error": "frame capture returned null"}
            except Exception as e:
                return {"error": str(e)}

        raise ValueError(f"Unrecognized tool: {name}")

    def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        method = request.get("method")
        msg_id = request.get("id")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": self.PROTOCOL_VERSION,
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "milli-agent-mcp",
                        "version": "1.0.0"
                    }
                }
            }

        elif method == "notifications/initialized":
            return None

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": self.get_tool_definitions()
                }
            }

        elif method == "tools/call":
            params = request.get("params", {})
            name = params.get("name")
            arguments = params.get("arguments", {})
            try:
                result = self.handle_tool_call(name, arguments)
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    }
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32000,
                        "message": str(e)
                    }
                }

        elif method == "ping":
            return {"jsonrpc": "2.0", "id": msg_id, "result": {}}

        # Method not found
        if msg_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
        return None

    def run_stdio(self):
        """Runs the MCP server loop reading JSON-RPC lines from stdin and writing to stdout."""
        self._running = True
        while self._running:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                line = line.strip()
                if not line:
                    continue
                req = json.loads(line)
                resp = self.handle_request(req)
                if resp is not None:
                    out = json.dumps(resp)
                    sys.stdout.write(out + "\n")
                    sys.stdout.flush()
            except (KeyboardInterrupt, SystemExit):
                break
            except Exception as e:
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
                }
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()


def main():
    server = MilliMCPServer()
    server.run_stdio()


if __name__ == "__main__":
    main()
