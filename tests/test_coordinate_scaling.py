"""
Unit Tests for Sub-Pixel Coordinate Scaling and Normalization.
"""

import unittest
from milli_agent.capture.base import CaptureSource
from milli_agent.capture.mock import MockCanvaDesktopSource
from milli_agent.capture.x11 import X11CaptureSource


class TestCoordinateScaling(unittest.TestCase):

    def test_mock_coordinate_scaling(self):
        source = MockCanvaDesktopSource(width=1280, height=720)
        px, py = source.to_physical(0.5, 0.5)
        self.assertEqual(px, 640.0)
        self.assertEqual(py, 360.0)

        nx, ny = source.to_normalized(640.0, 360.0)
        self.assertAlmostEqual(nx, 0.5)
        self.assertAlmostEqual(ny, 0.5)

    def test_arbitrary_screen_coordinate_scaling(self):
        class DummyCapture(CaptureSource):
            def read_frame(self):
                return True, None
            def get_dimensions(self):
                return (1366, 768)
            def close(self):
                pass

        source = DummyCapture()
        px, py = source.to_physical(1.0, 1.0)
        self.assertEqual(px, 1366.0)
        self.assertEqual(py, 768.0)

        nx, ny = source.to_normalized(1366.0, 768.0)
        self.assertAlmostEqual(nx, 1.0)
        self.assertAlmostEqual(ny, 1.0)


if __name__ == "__main__":
    unittest.main()
