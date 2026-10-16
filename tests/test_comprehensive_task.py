"""
Unit tests for ComprehensiveMultiStepBenchmark workflow.
"""

import unittest
import asyncio
from milli_agent.workflows.comprehensive_task import ComprehensiveMultiStepBenchmark


class TestComprehensiveMultiStepBenchmark(unittest.TestCase):

    def test_end_to_end_lifecycle_dry_run(self):
        """Tests the full thinking -> deciding -> doing -> verifying lifecycle."""
        async def _run():
            runner = ComprehensiveMultiStepBenchmark(dry_run=True, browser_port=9888)
            goal = "Automate frontier AI research dossier generation and persistence."
            res = await runner.execute_task(goal)

            self.assertEqual(res["status"], "success")
            telemetry = res["telemetry"]
            self.assertIn("thinking_ms", telemetry)
            self.assertIn("web_decision_ms", telemetry)
            self.assertIn("total_wall_clock_s", telemetry)
            self.assertGreater(res["speedup"], 1.0)
            self.assertGreaterEqual(len(res["diagnostics"]), 1)

        asyncio.run(_run())


if __name__ == "__main__":
    unittest.main()
