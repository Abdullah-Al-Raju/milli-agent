"""
Unit and integration tests for MilliBrowserEngine, FastCDPClient, and multimodal decision bridging.
"""

import unittest
import asyncio
import numpy as np
from milli_agent.brain.decision_bridge import MilliDecisionBridge
from milli_agent.browser.engine import MilliBrowserEngine
from milli_agent.browser.cdp_fast import FastCDPClient


class TestMilliBrowser(unittest.TestCase):

    def setUp(self):
        self.bridge = MilliDecisionBridge()

    def test_decision_bridge_dom_elements(self):
        """Tests sub-15ms non-autoregressive decision generation from DOM elements."""
        browser_state = {
            "title": "Search Engine",
            "url": "https://example.com",
            "elements": [
                {"tag": "input", "id": "search-box", "text": "", "x": 120, "y": 60, "selector": "#search-box"},
                {"tag": "button", "id": "btn-search", "text": "Execute Search", "x": 240, "y": 60, "selector": "#btn-search"},
                {"tag": "a", "id": "nav-link", "text": "About Us", "x": 500, "y": 20, "selector": "#nav-link"}
            ]
        }

        # Test TYPE decision for search query
        dec_type = self.bridge.evaluate_browser_action(browser_state, goal="type query in search-box")
        self.assertEqual(dec_type["operation"], "TYPE")
        self.assertEqual(dec_type["target_pos"], (120, 60))
        self.assertLess(dec_type["latency_ms"], 15.0)

        # Test CLICK decision for search button
        dec_click = self.bridge.evaluate_browser_action(browser_state, goal="click execute search")
        self.assertEqual(dec_click["operation"], "CLICK")
        self.assertEqual(dec_click["target_pos"], (240, 60))
        self.assertLess(dec_click["latency_ms"], 15.0)

    def test_decision_bridge_optical_fallback(self):
        """Tests fallback to optical manifold targets when no DOM elements are passed."""
        optical_state = {
            "targets": [
                {"screen_x": 640, "screen_y": 480, "confidence": 0.96}
            ]
        }
        dec = self.bridge.evaluate_scene(optical_state)
        self.assertEqual(dec["operation"], "CLICK")
        self.assertEqual(dec["target_pos"], (640, 480))
        self.assertLess(dec["latency_ms"], 15.0)

    def test_live_browser_in_loop_execution(self):
        """Tests live in-loop execution, zero arbitrary sleep, and RAM frame buffer."""
        async def _run():
            engine = MilliBrowserEngine(headless=True, port=9444, user_data_dir="/tmp/milli_test_p2")
            try:
                # 1. Start browser
                status = await engine.start()
                self.assertEqual(status["status"], "ready")

                # 2. Cypress Navigate (reactive settling, zero sleep)
                nav_res = await engine.cy_navigate(
                    "data:text/html,<html><body><button id='action-btn' onclick='this.innerText=\"DONE\"'>INITIAL</button><input id='name-box' /></body></html>"
                )
                self.assertEqual(nav_res["action"], "navigate")

                # 3. Interactive state query
                state = await engine.get_interactive_state()
                self.assertGreaterEqual(state["elements_count"], 2)

                # 4. Cypress In-Loop Click
                click_res = await engine.cy_click("#action-btn")
                self.assertEqual(click_res["action"], "click")
                val = await engine.cy_evaluate("document.getElementById('action-btn').innerText")
                self.assertEqual(val, "DONE")

                # 5. Cypress In-Loop Type
                type_res = await engine.cy_type("MilliAgentSpeed", selector="#name-box")
                self.assertEqual(type_res["action"], "type")
                typed_val = await engine.cy_evaluate("document.getElementById('name-box').value")
                self.assertEqual(typed_val, "MilliAgentSpeed")

                # 6. Direct Framebuffer Capture into RAM (Zero Disk Writes)
                frame = await engine.capture_frame_to_ram()
                self.assertIsInstance(frame, np.ndarray)
                self.assertGreater(frame.shape[0], 0)
                self.assertGreater(frame.shape[1], 0)

            finally:
                await engine.aclose()

        asyncio.run(_run())


if __name__ == "__main__":
    unittest.main()
