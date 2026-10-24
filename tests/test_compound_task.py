"""
Unit tests for CompoundTaskWorkflow in Milli-Agent.
Verifies multi-step compound goal decomposition, prompt extraction, and execution.
"""

import unittest
from milli_agent.workflows.compound_task import CompoundTaskWorkflow


class TestCompoundTaskWorkflow(unittest.TestCase):

    def setUp(self):
        self.workflow = CompoundTaskWorkflow(dry_run=True)

    def test_detection_of_compound_goals(self):
        goal = "search gemini web chat, open a chat, prompt it to generate a image of lamborgini, after that whne the image generation is finished download it and open it."
        self.assertTrue(self.workflow.is_compound_generative_goal(goal))

        simple_goal = "open youtube, search mr beast"
        self.assertFalse(self.workflow.is_compound_generative_goal(simple_goal))

    def test_parse_compound_goal_details(self):
        goal = "prompt it to generate an image of a red ferrari, after that when finished download and open it"
        spec = self.workflow.parse_compound_goal(goal)
        self.assertIn("ferrari", spec["prompt"].lower())
        self.assertTrue(spec["output_path"].endswith(".jpg"))
        self.assertIn(spec["viewer"], ["ristretto", "eog", "feh", "viewnior", "xdg-open", "display"])
        self.assertTrue(spec["wants_download"])
        self.assertTrue(spec["wants_open"])

    def test_execute_compound_pipeline_dry_run(self):
        goal = "generate an image of a cyber truck, wait until finished, download it and open it"
        res = self.workflow.execute_compound_pipeline(goal=goal)
        self.assertEqual(res["status"], "success")
        self.assertEqual(len(res["stages"]), 5)
        self.assertIn("cyber truck", res["prompt"].lower())


if __name__ == "__main__":
    unittest.main()
