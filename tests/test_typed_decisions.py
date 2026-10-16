import unittest
import time
from milli_agent.router.typed_decisions import FastDecisionRouter


class TestTypedDecisions(unittest.TestCase):

    def test_single_pass_choice_latency(self):
        router = FastDecisionRouter()
        state = {"subpixel_target": (450.0, 320.0), "mean_velocity": 1.2, "residual_norm": 0.5}
        candidates = ["draw_brush", "text_box", "color_picker", "select_tool"]

        t0 = time.perf_counter()
        dec = router.decide_choice(state, candidates, "select draw_brush tool")
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        self.assertEqual(dec.action, "draw_brush")
        self.assertLess(elapsed_ms, 15.0)  # Must be faster than 15ms target
        self.assertEqual(dec.target_coord, [450.0, 320.0])

    def test_fast_bool_trigger(self):
        router = FastDecisionRouter()
        stable_state = {"residual_norm": 2.0, "mean_velocity": 0.5, "event_triggered": False}
        shock_state = {"residual_norm": 45.0, "mean_velocity": 28.0, "event_triggered": True}

        self.assertTrue(router.decide_bool("Is canvas stable?", stable_state))
        self.assertFalse(router.decide_bool("Is canvas stable?", shock_state))
        self.assertTrue(router.decide_bool("Did anomaly occur?", shock_state))


if __name__ == '__main__':
    unittest.main()
