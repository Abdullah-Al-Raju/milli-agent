import unittest
from milli_agent.agent import MilliAgent
from milli_agent.capture.mock import MockCanvaDesktopSource


class TestReactiveReflex(unittest.TestCase):

    def test_reactive_reflex_loop_zero_storage(self):
        source = MockCanvaDesktopSource()
        agent = MilliAgent(capture_source=source, model="builtin", dry_run=True, use_live_stream=True)

        res = agent.execute_reactive_loop(task="flappy", duration_seconds=0.5)
        self.assertEqual(res["status"], "success")
        self.assertGreater(res["frames_tracked"], 0)
        self.assertEqual(res["disk_writes_bytes"], 0)
        agent.close()


if __name__ == '__main__':
    unittest.main()
