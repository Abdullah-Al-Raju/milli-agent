import unittest
from milli_agent.agent import MilliAgent
from milli_agent.capture.mock import MockCanvaDesktopSource
from milli_agent.controller.breakout_player import BreakoutPhysicsPlayer


class TestBreakoutPhysicsPlayer(unittest.TestCase):

    def test_wall_bounce_folding(self):
        player = BreakoutPhysicsPlayer(live_stream=None, dry_run=True)
        # Trajectory inside [0, 800]
        self.assertEqual(player._fold_wall_bounces(400, 800), 400)
        # Bounce off right wall at 850 (exceeds 800 by 50 -> reflects to 750)
        self.assertEqual(player._fold_wall_bounces(850, 800), 750)
        # Bounce off left wall at -50 -> reflects to 50
        self.assertEqual(player._fold_wall_bounces(-50, 800), 50)

    def test_breakout_reactive_loop(self):
        source = MockCanvaDesktopSource()
        agent = MilliAgent(capture_source=source, model="builtin", dry_run=True, use_live_stream=True)
        res = agent.execute_reactive_loop(task="breakout", duration_seconds=0.5)
        self.assertEqual(res["status"], "success")
        self.assertGreater(res["frames_tracked"], 0)
        self.assertEqual(res["disk_writes_bytes"], 0)
        agent.close()


if __name__ == '__main__':
    unittest.main()
