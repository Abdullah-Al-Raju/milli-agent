import unittest
import numpy as np
from milli_agent.engine.manifold import ManifoldEngine
from milli_agent.engine.fourier import FourierCoordinateProjector
from milli_agent.engine.flow import OpticalSplineFlow


class TestManifoldEngine(unittest.TestCase):

    def test_fourier_projection(self):
        projector = FourierCoordinateProjector(num_frequencies=8, scale=5.0)
        coords = np.array([[0.1, 0.2], [0.5, 0.8]], dtype=np.float32)
        feats = projector.project(coords)
        self.assertEqual(feats.shape, (2, 16))
        self.assertTrue(np.all(np.isfinite(feats)))

    def test_flow_and_subpixel(self):
        flow = OpticalSplineFlow()
        f0 = np.zeros((100, 100), dtype=np.float32)
        f1 = np.zeros((100, 100), dtype=np.float32)
        f0[40:60, 40:60] = 200.0
        f1[42:62, 42:62] = 200.0  # shifted by +2, +2

        Ix, Iy, It = flow.compute_gradients(f0, f1)
        u, v = flow.estimate_velocity_field(Ix, Iy, It)
        self.assertEqual(u.shape, (100, 100))
        self.assertEqual(v.shape, (100, 100))

        tx, ty, conf = flow.find_subpixel_target(f1)
        self.assertTrue(38.0 <= tx <= 62.0)
        self.assertTrue(38.0 <= ty <= 62.0)

    def test_manifold_ingestion(self):
        engine = ManifoldEngine()
        frame = np.ones((100, 100), dtype=np.uint8) * 50
        res1 = engine.ingest_frame(frame)
        self.assertTrue(res1["is_key_manifold"])
        self.assertEqual(res1["tokens_emitted"], 160)

        # Small motion
        frame[40:50, 40:50] = 220
        res2 = engine.ingest_frame(frame)
        self.assertTrue(res2["tokens_emitted"] <= 18)
        self.assertTrue(res2["token_savings_percent"] > 0)


if __name__ == '__main__':
    unittest.main()
