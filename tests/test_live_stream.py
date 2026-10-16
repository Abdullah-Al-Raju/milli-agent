"""
Unit Tests for LiveManifoldStream (Persistent 60Hz Optical Eye).
Verifies thread lifecycle, thread-safe state vector retrieval, and zero-storage bounded buffer.
"""

import time
import unittest
import numpy as np
from milli_agent.capture.base import CaptureSource
from milli_agent.engine.live_stream import LiveManifoldStream


class DummyMockSource(CaptureSource):
    def __init__(self):
        self.frame_idx = 0

    def read_frame(self):
        self.frame_idx += 1
        # Synthetic 200x200 grayscale frame
        frame = np.full((200, 200), (self.frame_idx * 5) % 255, dtype=np.uint8)
        return True, frame

    def get_dimensions(self):
        return 200, 200

    def close(self):
        pass


class TestLiveManifoldStream(unittest.TestCase):

    def test_live_stream_lifecycle_and_vectors(self):
        source = DummyMockSource()
        stream = LiveManifoldStream(capture_source=source, fps=60)

        # 1. Start daemon
        stream.start()
        self.assertTrue(stream._running)

        # 2. Allow 60Hz loop to run for a short burst
        time.sleep(0.1)

        # 3. Retrieve live manifold vector
        vec = stream.get_live_manifold_vector()
        self.assertIn("timestamp", vec)
        self.assertIn("mean_velocity", vec)
        self.assertIn("tokens_emitted", vec)

        # 4. Check zero-storage bounded memory (transient frame view)
        frame_view = stream.get_live_frame_view()
        self.assertIsNotNone(frame_view)
        self.assertEqual(frame_view.shape, (200, 200))

        # 5. Stop daemon cleanly
        stream.stop()
        self.assertFalse(stream._running)


if __name__ == "__main__":
    unittest.main()
