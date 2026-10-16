import unittest
import os
from milli_agent.workflows.hard_task import MilliHardTaskRunner


class TestHardTaskWorkflow(unittest.TestCase):

    def test_hard_task_execution(self):
        runner = MilliHardTaskRunner(dry_run=True)
        res = runner.run()
        self.assertEqual(res["status"], "success")
        self.assertIn("analytics", res)
        self.assertGreater(res["file_size_bytes"], 500)
        self.assertTrue(os.path.exists(res["file_path"]))


if __name__ == "__main__":
    unittest.main()
