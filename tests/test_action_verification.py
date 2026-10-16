"""
Unit Tests for Localized Spatiotemporal Delta Action Feedback.
"""

import unittest
import numpy as np
from milli_agent.engine.manifold import ManifoldEngine


class TestActionVerification(unittest.TestCase):

    def setUp(self):
        self.engine = ManifoldEngine()

    def test_no_effect_detected_when_frames_identical(self):
        f0 = np.zeros((100, 100), dtype=np.uint8)
        f1 = np.zeros((100, 100), dtype=np.uint8)
        feedback = self.engine.verify_action_effect(f0, f1, target_coord=(50, 50))
        self.assertFalse(feedback["effect_detected"])
        self.assertEqual(feedback["local_delta"], 0.0)

    def test_local_effect_detected_on_click_perturbation(self):
        f0 = np.zeros((100, 100), dtype=np.uint8)
        f1 = np.zeros((100, 100), dtype=np.uint8)
        # Simulate click ripple or button highlight at (50, 50)
        f1[45:55, 45:55] = 200

        feedback = self.engine.verify_action_effect(f0, f1, target_coord=(50, 50), radius=10)
        self.assertTrue(feedback["effect_detected"])
        self.assertGreater(feedback["local_delta"], 10.0)

    def test_remote_perturbation_does_not_trigger_tight_local_target(self):
        f0 = np.zeros((200, 200), dtype=np.uint8)
        f1 = np.zeros((200, 200), dtype=np.uint8)
        # Perturbation far away at (180, 180)
        f1[175:185, 175:185] = 100

        # Checking at (20, 20) with small radius 15
        feedback = self.engine.verify_action_effect(f0, f1, target_coord=(20, 20), radius=15)
        self.assertEqual(feedback["local_delta"], 0.0)


if __name__ == "__main__":
    unittest.main()
