import unittest
from milli_agent.eval.system1_benchmark import MilliBenchmarkSuite


class TestSystem1BenchmarkSuite(unittest.TestCase):

    def test_system1_exact_evaluation_accuracy_and_latency(self):
        suite = MilliBenchmarkSuite()
        res = suite.run_benchmark()
        self.assertEqual(res["status"], "completed")
        self.assertEqual(res["accuracy"], 1.0)
        self.assertLess(res["p50_latency_ms"], 30.0)
        self.assertGreater(res["speedup_vs_baseline"], 1.2)


if __name__ == '__main__':
    unittest.main()
