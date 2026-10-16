"""
Unit tests for MilliVisualServer and AI multimodal endpoints.
"""

import unittest
import urllib.request
import json
import time
from milli_agent.visual.server import MilliVisualServer


class TestVisualServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Start test visual server on port 9899 in dry-run mode
        cls.server = MilliVisualServer(host="127.0.0.1", port=9899, fps=30, dry_run=True)
        cls.server.start()
        time.sleep(0.3)

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def test_dashboard_html_endpoint(self):
        """Tests that GET / serves the visual HUD dashboard."""
        url = "http://127.0.0.1:9899/"
        with urllib.request.urlopen(url, timeout=2.0) as resp:
            self.assertEqual(resp.status, 200)
            body = resp.read().decode("utf-8")
            self.assertIn("MILLI-AGENT VISUAL MANIFOLD", body)
            self.assertIn("coords-hud", body)

    def test_state_json_endpoint(self):
        """Tests that GET /api/state returns JSON telemetry."""
        url = "http://127.0.0.1:9899/api/state"
        with urllib.request.urlopen(url, timeout=2.0) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data["status"], "online")
            self.assertIn("resolution", data)

    def test_action_execution_endpoint(self):
        """Tests that POST /api/action handles visual action requests."""
        url = "http://127.0.0.1:9899/api/action"
        payload = json.dumps({"action": "click", "x": 400, "y": 300}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data["status"], "ok")
            self.assertEqual(data["coords"], [400.0, 300.0])


if __name__ == "__main__":
    unittest.main()
