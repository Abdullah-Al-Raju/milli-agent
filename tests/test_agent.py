import unittest
from milli_agent.agent import MilliAgent
from milli_agent.capture.mock import MockCanvaDesktopSource


class TestMilliAgent(unittest.TestCase):

    def test_end_to_end_canva_mascot_drawing(self):
        source = MockCanvaDesktopSource()
        agent = MilliAgent(capture_source=source, model="builtin", dry_run=True)

        res = agent.execute_goal("Open Canva moodboard and draw a Milli mascot cat")
        self.assertEqual(res["status"], "completed")
        self.assertGreater(res["steps_executed"], 0)
        self.assertGreater(len(source.drawn_strokes), 0)
        self.assertGreaterEqual(res["telemetry"]["token_savings_percent"], 38.0)


if __name__ == '__main__':
    unittest.main()
