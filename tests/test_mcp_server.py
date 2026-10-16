"""
Unit tests for Milli-Agent MCP Server.
"""

import unittest
import json
from milli_agent.mcp.server import MilliMCPServer


class TestMilliMCPServer(unittest.TestCase):

    def setUp(self):
        self.server = MilliMCPServer(dry_run=True)

    def test_mcp_initialize(self):
        req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        }
        resp = self.server.handle_request(req)
        self.assertEqual(resp["id"], 1)
        self.assertIn("protocolVersion", resp["result"])
        self.assertEqual(resp["result"]["serverInfo"]["name"], "milli-agent-mcp")

    def test_mcp_tools_list(self):
        req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        resp = self.server.handle_request(req)
        self.assertEqual(resp["id"], 2)
        tools = resp["result"]["tools"]
        tool_names = [t["name"] for t in tools]
        self.assertIn("milli_click", tool_names)
        self.assertIn("milli_type", tool_names)
        self.assertIn("milli_key", tool_names)
        self.assertIn("milli_scroll", tool_names)
        self.assertIn("milli_get_state", tool_names)
        self.assertIn("milli_get_frame", tool_names)

    def test_mcp_tool_call_click(self):
        req = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "milli_click",
                "arguments": {"x": 500, "y": 300, "button": 1}
            }
        }
        resp = self.server.handle_request(req)
        self.assertEqual(resp["id"], 3)
        content = json.loads(resp["result"]["content"][0]["text"])
        self.assertEqual(content["status"], "ok")
        self.assertEqual(content["coords"], [500.0, 300.0])

    def test_mcp_tool_call_get_state(self):
        req = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "milli_get_state",
                "arguments": {}
            }
        }
        resp = self.server.handle_request(req)
        self.assertEqual(resp["id"], 4)
        content = json.loads(resp["result"]["content"][0]["text"])
        self.assertIn("platform", content)
        self.assertIn("resolution", content)


if __name__ == "__main__":
    unittest.main()
