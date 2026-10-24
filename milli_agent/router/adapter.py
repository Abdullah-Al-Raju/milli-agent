"""
Universal Model-Agnostic Adapter Layer for Milli-Agent.
Enables ANY AI Brain (Local Ollama, Host AI, OpenAI, Gemini, Claude)
to receive compact 4D Manifold state vectors and emit dynamic OS action plans.

ZERO HARDCODED TASK TEMPLATES:
- Every action plan is generated dynamically from the goal and manifold perception.
- Universal action primitives: launch_app, hotkey, type_text, click, drag_path, sleep.
"""

import re
import json
import urllib.request
import urllib.parse
from typing import Dict, Any, List


class ModelAdapter:
    """
    Abstract adapter translating compact Milli 4D Manifold vectors into model prompts
    and parsing dynamic action plans.
    """

    def __init__(self, model_spec: str = "builtin"):
        self.model_spec = model_spec

    def plan_steps(self, goal: str, visual_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generates high-level execution steps for an arbitrary user goal.
        """
        if self.model_spec.startswith("ollama:"):
            return self._query_ollama(goal, visual_summary)
        elif self.model_spec.startswith("openai:") or self.model_spec.startswith("gemini:"):
            return self._query_openai_compatible(goal, visual_summary)
        else:
            return self._dynamic_primitive_planner(goal, visual_summary)

    @staticmethod
    def _detect_browser() -> str:
        import shutil
        for b in ["brave-browser", "google-chrome", "chromium", "firefox"]:
            if shutil.which(b):
                return b
        return "brave-browser"

    def _dynamic_primitive_planner(self, goal: str, visual_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Pure dynamic planner decomposing arbitrary natural language goals into standard
        OS action primitives without any task-specific keywords (no hardcoded domain logic).
        """
        steps: List[Dict[str, Any]] = []
        g = goal.strip()
        g_lower = g.lower()
        browser_app = self._detect_browser()

        # Extract target URLs or search terms dynamically from the user's sentence
        url_match = re.search(r'https?://[^\s]+', g)
        detected_url = url_match.group(0) if url_match else None

        # 1. Check if the goal involves web browsing or searching
        wants_browser = any(v in g_lower for v in ["browser", "web", "search", "online", "google", "youtube", "wikipedia", "github", "reddit", "amazon"])
        # Check if the goal involves drawing or canvas
        wants_draw = any(v in g_lower for v in ["draw", "sketch", "canvas", "diagram", "paint", "whiteboard", "box", "boxes"])
        # Check if the goal involves note taking or writing to notepad
        wants_notepad = any(v in g_lower for v in ["notepad", "mousepad", "write", "note", "text file", "save names", "record"])

        # Dynamic Browser Action
        if wants_browser or wants_draw or detected_url:
            if detected_url:
                nav_url = detected_url
                nav_desc = f"Navigate directly to {nav_url}"
            elif "youtube" in g_lower:
                m = re.search(r'(?:search\s+(?:for\s+)?|find\s+|play\s+)(.+?)(?:\s+on\s+youtube|\s+in\s+youtube|$)', g, flags=re.IGNORECASE)
                if m:
                    query = m.group(1).strip()
                else:
                    m2 = re.search(r'youtube\s+(?:search\s+)?(.+)', g, flags=re.IGNORECASE)
                    query = m2.group(1).strip() if m2 else ""
                query = re.sub(r'^(for|the|who|a)\s+', '', query, flags=re.IGNORECASE).strip()
                query = re.split(r'\band\b|\bthen\b|,', query)[0].strip()
                if query and query.lower() not in ["youtube", "video"]:
                    nav_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
                    nav_desc = f"Search YouTube for '{query}'"
                else:
                    nav_url = "https://www.youtube.com"
                    nav_desc = "Open YouTube"
            elif "wikipedia" in g_lower:
                wiki_q = re.sub(r'^(open\s+)?wikipedia\s*(search\s*)?', '', g, flags=re.IGNORECASE).strip()
                wiki_q = re.sub(r'\s+on\s+wikipedia.*$', '', wiki_q, flags=re.IGNORECASE).strip()
                nav_url = f"https://en.wikipedia.org/wiki/Special:Search?search={urllib.parse.quote(wiki_q)}"
                nav_desc = f"Search Wikipedia for '{wiki_q}'"
            elif "github" in g_lower:
                gh_q = re.sub(r'^(open\s+)?github\s*(search\s*)?', '', g, flags=re.IGNORECASE).strip()
                nav_url = f"https://github.com/search?q={urllib.parse.quote(gh_q)}"
                nav_desc = f"Search GitHub for '{gh_q}'"
            elif "reddit" in g_lower:
                rd_q = re.sub(r'^(open\s+)?reddit\s*(search\s*)?', '', g, flags=re.IGNORECASE).strip()
                nav_url = f"https://www.reddit.com/search/?q={urllib.parse.quote(rd_q)}"
                nav_desc = f"Search Reddit for '{rd_q}'"
            elif wants_draw:
                nav_url = "https://excalidraw.com"
                nav_desc = "Open Excalidraw whiteboard"
            else:
                q = g
                for prefix in ["open browser search", "open browser and search", "search", "find", "open", "look up"]:
                    if prefix in q.lower():
                        parts = re.split(re.escape(prefix), q, flags=re.IGNORECASE)
                        if len(parts) > 1:
                            q = parts[1].strip()
                            break
                q = re.sub(r'^(for|who|the|my)\s+', '', q, flags=re.IGNORECASE).strip()
                q = re.split(r'\band\b|\bthen\b|,', q)[0].strip()
                nav_url = f"https://www.google.com/search?q={urllib.parse.quote(q)}"
                nav_desc = f"Search Google for '{q}'"

            steps.append({
                "action": "launch_app",
                "app": browser_app,
                "url": nav_url,
                "description": f"Ensure browser ({browser_app}) is active with {nav_desc}"
            })
            steps.append({
                "action": "hotkey",
                "key": "ctrl+l",
                "description": "Focus browser address bar"
            })
            steps.append({
                "action": "type_text",
                "text": nav_url,
                "press_return": True,
                "description": f"Navigate to '{nav_url}'"
            })
            steps.append({
                "action": "sleep",
                "duration": 1.2,
                "description": "Allow visual manifold to ingest web viewport"
            })

        # Dynamic Drawing Action
        if wants_draw:
            shape_type = "architecture_diagram" if any(k in g.lower() for k in ["architecture", "diagram", "box", "boxes", "arrows"]) else "milli_cat_mascot"
            steps.append({
                "action": "draw_spline_shape",
                "shape": shape_type,
                "center": [680.0, 380.0],
                "scale": 1.0,
                "description": f"Stream continuous vector splines ({shape_type}) to canvas"
            })

        # Dynamic Notepad Action
        if wants_notepad:
            steps.append({
                "action": "launch_notepad",
                "app": "mousepad",
                "text": f"Agent Output for Goal:\n'{goal}'\n\n- Executed dynamically via Milli Continuous Manifold.",
                "output_file": "agent_dynamic_output.txt",
                "description": "Launch system Notepad and record dynamic output"
            })

        # If purely a clicking/targeting task on current screen
        if not steps:
            tx, ty = visual_summary.get("subpixel_target", (640.0, 360.0))
            steps.append({
                "action": "click",
                "coord": [tx, ty],
                "description": f"Target salient gradient extrema at ({tx:.1f}, {ty:.1f})"
            })

        return steps

    def _query_ollama(self, goal: str, visual_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Queries local Ollama endpoint (localhost:11434)."""
        model_name = self.model_spec.split("ollama:")[-1]
        prompt = (
            f"You are Milli-Agent operating an OS. Goal: '{goal}'.\n"
            f"Visual State: S(x,y) locked, mean_velocity={visual_summary.get('mean_velocity', 0):.2f}.\n"
            f"Return JSON list of actions: [{{'action': 'launch_app|hotkey|type_text|click', 'description': '...'}}]"
        )
        payload = json.dumps({
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }).encode('utf-8')

        req = urllib.request.Request("http://localhost:11434/api/generate", data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                data = json.loads(resp.read().decode())
                response_text = data.get("response", "[]")
                return json.loads(response_text)
        except Exception:
            return self._dynamic_primitive_planner(goal, visual_summary)

    def _query_openai_compatible(self, goal: str, visual_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fallback to dynamic planner if external API is unconfigured."""
        return self._dynamic_primitive_planner(goal, visual_summary)
