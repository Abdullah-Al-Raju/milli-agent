"""
Milli-Agent Autonomous Decision Bridge.

Connects Milli's Live Eye (Maya zero-copy continuous visual manifold)
with Milli's Non-Autoregressive System 1 Reflex Engine.
"""

import time
from typing import Dict, Any, List, Optional, Tuple


class MilliDecisionBridge:
    """
    Interfaces visual manifold observations directly with Milli's System 1
    decision architecture, emitting structured actions in a single forward pass.
    """

    def __init__(self, mode: str = "fast_saliency"):
        self.mode = mode
        self._cached_decisions: List[Dict[str, Any]] = []

    def evaluate_scene(
        self,
        frame_features: Dict[str, Any],
        goal: str = "Execute optimal action"
    ) -> Dict[str, Any]:
        """
        Takes raw spatial features (from Maya live optical manifold) or
        DOM interactive elements (from MilliBrowserEngine) and outputs
        a typed non-autoregressive decision with confidence score (< 15ms).
        """
        t0 = time.perf_counter()
        targets = frame_features.get("targets", [])
        elements = frame_features.get("elements", [])

        # Priority 1: Check DOM interactive elements if present
        if elements:
            action = self._decide_from_elements(elements, goal, t0)
            self._cached_decisions.append(action)
            return action

        # Priority 2: Check spatial optical targets
        if not targets:
            action = {
                "operation": "WAIT",
                "target_pos": None,
                "confidence": 0.99,
                "latency_ms": (time.perf_counter() - t0) * 1000.0,
                "engine": "milli_system1"
            }
            self._cached_decisions.append(action)
            return action

        # Select highest-saliency candidate
        best_target = targets[0]
        latency = (time.perf_counter() - t0) * 1000.0

        action = {
            "operation": "CLICK",
            "target_pos": (best_target["screen_x"], best_target["screen_y"]),
            "confidence": best_target.get("confidence", 0.95),
            "latency_ms": latency,
            "engine": "milli_system1"
        }
        self._cached_decisions.append(action)
        return action

    def evaluate_browser_action(
        self,
        browser_state: Dict[str, Any],
        goal: str = "submit"
    ) -> Dict[str, Any]:
        """
        Specialized single-pass non-autoregressive browser decision maker.
        Maps DOM interactive states + high-level goals directly to Cypress primitives.
        Latency: < 5 ms.
        """
        return self.evaluate_scene(browser_state, goal=goal)

    def _decide_from_elements(
        self,
        elements: List[Dict[str, Any]],
        goal: str,
        t0: float
    ) -> Dict[str, Any]:
        """
        Single-pass rule and heuristic matching on interactive DOM elements.
        Zero token-by-token autoregressive generation.
        """
        goal_lower = goal.lower()
        best_element: Optional[Dict[str, Any]] = None
        best_score = -1.0
        for el in elements:
            score = 0.0
            tag = el.get("tag", "").lower()
            text = el.get("text", "").lower()
            el_id = el.get("id", "").lower()
            selector = el.get("selector", "")

            # Exact or partial keyword match in text, ID, or selector
            for word in goal_lower.split():
                if word in ("click", "type", "fill", "press", "in", "the", "a", "an"):
                    continue
                if word and word in text:
                    score += 4.0
                if word and word in el_id:
                    score += 3.0
                if word and word in selector.lower():
                    score += 2.0

            # Action intent matching
            is_type_intent = any(k in goal_lower for k in ("type", "fill", "write", "enter"))
            is_click_intent = any(k in goal_lower for k in ("click", "press", "submit", "button"))

            if is_type_intent:
                if tag in ("input", "textarea"):
                    score += 3.0
            elif is_click_intent:
                if tag in ("button", "a", "select") or el.get("role") == "button":
                    score += 3.0

            if score > best_score:
                best_score = score
                best_element = el

        latency = (time.perf_counter() - t0) * 1000.0

        if best_element and best_score > 0:
            target_pos = None
            if "center" in best_element:
                target_pos = (best_element["center"]["x"], best_element["center"]["y"])
            elif "x" in best_element and "y" in best_element:
                target_pos = (best_element["x"], best_element["y"])

            tag = best_element.get("tag", "").lower()
            is_type_intent = any(k in goal_lower for k in ("type", "fill", "write", "enter"))
            if tag in ("input", "textarea") and (is_type_intent or "click" not in goal_lower):
                op = "TYPE"
            else:
                op = "CLICK"

            return {
                "operation": op,
                "target_element": best_element,
                "selector": best_element.get("selector"),
                "target_pos": target_pos,
                "confidence": min(0.99, 0.70 + (best_score * 0.05)),
                "latency_ms": latency,
                "engine": "milli_system1"
            }

        # Fallback to first interactive element or WAIT
        if elements:
            fallback = elements[0]
            target_pos = None
            if "center" in fallback:
                target_pos = (fallback["center"]["x"], fallback["center"]["y"])
            elif "x" in fallback and "y" in fallback:
                target_pos = (fallback["x"], fallback["y"])
            return {
                "operation": "CLICK",
                "target_element": fallback,
                "selector": fallback.get("selector"),
                "target_pos": target_pos,
                "confidence": 0.65,
                "latency_ms": latency,
                "engine": "milli_system1"
            }

        return {
            "operation": "WAIT",
            "target_pos": None,
            "confidence": 0.90,
            "latency_ms": latency,
            "engine": "milli_system1"
        }

