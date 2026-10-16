import unittest
from milli_agent.network.vman import VisualManifoldActionNetwork, ActionDecision, ACTION_TYPES


class TestVisualManifoldActionNetwork(unittest.TestCase):

    def setUp(self):
        self.net = VisualManifoldActionNetwork()
        # Single warmup pass to eliminate cold module loading jitter
        mock_init = {
            "mean_velocity": 0.0,
            "residual_norm": 0.0,
            "subpixel_target": (0.0, 0.0),
            "base_signature": {"harmonic_coeffs": [0.0] * 16}
        }
        self.net.forward(mock_init, "warmup")

    def test_single_pass_latency(self):
        mock_manifold = {
            "mean_velocity": 3.5,
            "residual_norm": 1.2,
            "subpixel_target": (500.0, 300.0),
            "base_signature": {"harmonic_coeffs": [0.5] * 16}
        }
        # Warmup and measure
        for _ in range(3):
            self.net.forward(mock_manifold, "Jump through gap")
        res = self.net.forward(mock_manifold, "Jump through gap")
        self.assertIsInstance(res, ActionDecision)
        self.assertIn(res.action_type, ACTION_TYPES)
        # Verify sub-38.4ms latency target
        self.assertLess(res.latency_ms, 38.4)
        self.assertGreaterEqual(res.confidence, 0.0)
        self.assertLessEqual(res.confidence, 1.0)
        self.assertEqual(len(res.coords), 2)
        self.assertGreaterEqual(res.coords[0], 0.0)
        self.assertLessEqual(res.coords[0], 1.0)


if __name__ == '__main__':
    unittest.main()
