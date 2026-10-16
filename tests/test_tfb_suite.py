"""
Unit Tests for Task Finished Benchmark (TFB) Suite and Turbo Components.
Verifies pipelined controllers, VMAN spatial target regression, perceptual settle gates,
and benchmark suite execution.
"""

import unittest
import numpy as np
from milli_agent.network.vman import VisualManifoldActionNetwork, ACTION_TYPES
from milli_agent.controller.input import OSInputController
from milli_agent.engine.live_stream import LiveManifoldStream
from milli_agent.capture.mock import MockCanvaDesktopSource
from milli_agent.eval.tfb_suite import TaskFinishedBenchmarkSuite


class TestTFBComponents(unittest.TestCase):

    def setUp(self):
        self.vman = VisualManifoldActionNetwork()
        self.mock_source = MockCanvaDesktopSource()
        self.controller = OSInputController(dry_run=True)

    def test_vman_expanded_actions_and_spatial_prediction(self):
        # 1. Check expanded action types
        self.assertIn("TYPE_TEXT", ACTION_TYPES)
        self.assertIn("HOTKEY", ACTION_TYPES)
        self.assertIn("NAVIGATE", ACTION_TYPES)

        # 2. Check spatial target prediction on synthetic image
        frame = np.zeros((100, 100), dtype=np.uint8)
        # Create a bright target at (60, 40)
        frame[35:45, 55:65] = 250

        target = self.vman.predict_spatial_target(frame, contrast_threshold=220.0)
        self.assertIsNotNone(target)
        cx, cy, salience = target
        self.assertAlmostEqual(cx, 59.5, delta=2.0)
        self.assertAlmostEqual(cy, 39.5, delta=2.0)
        self.assertGreater(salience, 0.0)

    def test_controller_pipelined_methods(self):
        # 1. Pipelined URL navigation (dry run)
        ok_nav = self.controller.pipeline_navigate_url("https://example.com")
        self.assertTrue(ok_nav)

        # 2. Pipelined Form Fill (dry run)
        ok_form = self.controller.pipeline_fill_form(["Alice", "alice@milli.ai", "SecretProject"])
        self.assertTrue(ok_form)

    def test_perceptual_settle_gate(self):
        stream = LiveManifoldStream(capture_source=self.mock_source, fps=60)
        stream.start()

        # Settled gate should resolve within timeout
        settled = stream.wait_for_settled(max_velocity=10.0, min_dwell_ms=10.0, timeout=0.5)
        self.assertTrue(settled)

        # Visual effect check between identical frames
        ref = stream.get_live_frame_view()
        effect = stream.wait_for_visual_effect(reference_frame=ref, timeout=0.1)
        # Identical frame has no delta
        self.assertFalse(effect)

        stream.stop()

    def test_tfb_suite_dry_run_execution(self):
        suite = TaskFinishedBenchmarkSuite(dry_run=True)
        results = suite.run_all()

        self.assertEqual(len(results), 4)
        for res in results:
            self.assertEqual(res["status"], "success")
            self.assertIn("time_to_finish_s", res)
            self.assertIn("speedup_vs_conventional", res)
            self.assertGreater(res["speedup_vs_conventional"], 1.0)


if __name__ == "__main__":
    unittest.main()
