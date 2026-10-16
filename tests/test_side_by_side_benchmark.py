"""
Unit tests for side-by-side empirical benchmark runner.
"""

import unittest
import os
import json
from milli_agent.eval.side_by_side_benchmark import SideBySideBenchmarkRunner


class TestSideBySideBenchmark(unittest.TestCase):

    def test_benchmark_simulation_and_report_generation(self):
        runner = SideBySideBenchmarkRunner(dry_run=True)
        results = runner.run_all_benchmarks()

        self.assertIn("task_a", results)
        self.assertIn("task_b", results)
        self.assertIn("task_c", results)
        self.assertIn("task_d", results)

        # Ensure speedup is significant across tasks
        for tid, data in results.items():
            self.assertGreater(data["speedup_factor"], 10.0)
            self.assertEqual(data["milli_agent"]["tokens_consumed"], 0)
            self.assertEqual(data["milli_agent"]["disk_bytes_written"], 0)

        # Generate report to test path
        test_report = "test_benchmark_report.md"
        try:
            content = runner.generate_markdown_report(results, output_path=test_report)
            self.assertTrue(os.path.exists(test_report))
            self.assertIn("Empirical Benchmark Report", content)
            self.assertIn("Milli-Agent", content)
        finally:
            if os.path.exists(test_report):
                os.remove(test_report)


if __name__ == "__main__":
    unittest.main()
