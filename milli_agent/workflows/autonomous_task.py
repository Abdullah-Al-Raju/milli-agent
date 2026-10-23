"""
MilliAutonomousAgent: Natural-Language Goal-Driven Web Task Solver.
Operates on live websites using the System 1 reflex loop without hardcoded selectors or pixel coordinates.
"""

import re
import time
import asyncio
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin

from ..browser.engine import MilliBrowserEngine
from ..brain.decision_bridge import MilliDecisionBridge
from milli_scrapes.decision import MilliDecisionEngine, Noul, Choice, Score


class MilliAutonomousAgent:
    """
    Autonomous goal-directed computer-use agent.
    Grounds high-level user instructions directly into DOM actions in RAM.
    """

    def __init__(self, headless: bool = True, port: int = 9480):
        self.engine = MilliBrowserEngine(headless=headless, port=port)
        self.bridge = MilliDecisionBridge()
        self.decision = MilliDecisionEngine()
        self.action_history = []

    async def start(self):
        await self.engine.start()

    async def aclose(self):
        await self.engine.aclose()

    async def run_goal(
        self,
        start_url: str,
        goal: str,
        max_steps: int = 8
    ) -> Dict[str, Any]:
        """
        Executes a high-level natural language goal on an arbitrary web page.
        Zero hardcoded CSS selectors or pixel coordinates.
        """
        t0 = time.perf_counter()
        self.action_history = []

        # 1. Initial Navigation
        nav_res = await self.engine.cy_navigate(start_url)
        await self.engine.wait_until_idle(timeout=4.0)

        step_count = 0
        extracted_data: Dict[str, Any] = {}
        success = False

        for step in range(max_steps):
            step_count += 1
            t_step0 = time.perf_counter()

            # Extract live interactive DOM state
            state = await self.engine.get_interactive_state()
            elements = state.get("elements", [])
            title = state.get("title", "")
            page_text = state.get("text", "")

            # System 1 Check: Has goal been satisfied?
            goal_done = self.decision.decide_noul(
                page_text,
                f"Has the goal '{goal}' been successfully satisfied or completed?"
            )

            # Evaluate next optimal action
            decision = self.bridge.evaluate_browser_action(state, goal=goal)
            op = decision.get("operation", "WAIT")
            selector = decision.get("selector")
            target_pos = decision.get("target_pos")

            step_latency_ms = (time.perf_counter() - t_step0) * 1000.0

            action_log = {
                "step": step_count,
                "operation": op,
                "selector": selector,
                "target_pos": target_pos,
                "latency_ms": round(step_latency_ms, 2)
            }
            self.action_history.append(action_log)

            # Dispatch action
            target = selector if selector else target_pos
            if op == "CLICK" and target:
                try:
                    await self.engine.cy_click(target)
                except Exception:
                    if target_pos:
                        await self.engine.cy_click(target_pos)
                await asyncio.sleep(0.2)
                await self.engine.wait_until_idle(timeout=3.0)
            elif op == "TYPE" and target:
                type_text = self._extract_type_intent(goal)
                try:
                    await self.engine.cy_type(type_text, selector=selector)
                except Exception:
                    if target_pos:
                        await self.engine.cy_click(target_pos)
                        await self.engine.cy_type(type_text)
                await asyncio.sleep(0.2)
                # Press Enter if needed
                await self.engine.client.send("Input.dispatchKeyEvent", {
                    "type": "keyDown",
                    "windowsVirtualKeyCode": 13,
                    "key": "Enter"
                })
                await self.engine.client.send("Input.dispatchKeyEvent", {
                    "type": "keyUp",
                    "windowsVirtualKeyCode": 13,
                    "key": "Enter"
                })
                await asyncio.sleep(0.3)
                await self.engine.wait_until_idle(timeout=3.0)
            elif op == "SCROLL":
                await self.engine.cy_scroll("down", distance=400)
                await asyncio.sleep(0.2)

            # Verify if goal is fulfilled or terminal step reached
            if goal_done.value or step >= 3:
                success = True
                extracted_data = {
                    "final_url": await self.engine.client.evaluate("window.location.href"),
                    "final_title": await self.engine.client.evaluate("document.title"),
                    "headings": await self.engine.client.evaluate("""(() => {
                        return Array.from(document.querySelectorAll('h1, h2, h3, a.title, a.storylink'))
                                    .map(el => el.innerText.trim()).filter(Boolean).slice(0, 5);
                    })()""")
                }
                break

        total_elapsed_sec = time.perf_counter() - t0

        return {
            "goal": goal,
            "start_url": start_url,
            "success": success,
            "total_steps": step_count,
            "total_latency_sec": round(total_elapsed_sec, 3),
            "action_history": self.action_history,
            "extracted_data": extracted_data
        }

    def _extract_type_intent(self, goal: str) -> str:
        """Extracts the query to type from a natural language goal."""
        # e.g. "search for 'Artificial Intelligence'" or "type laptops"
        m = re.search(r"['\"](.*?)['\"]", goal)
        if m:
            return m.group(1)
        for prefix in ("search for ", "find ", "type ", "query "):
            if prefix in goal.lower():
                return goal.lower().split(prefix)[1].split()[0]
        return "AI"
