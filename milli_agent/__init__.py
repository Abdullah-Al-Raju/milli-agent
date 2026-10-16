"""
Milli-Agent: Autonomous OS-Level Computer-Use Agent.
"""

from .agent import MilliAgent
from .engine.manifold import ManifoldEngine
from .capture.base import CaptureSource
from .router.typed_decisions import TypedDecision, FastDecisionRouter
from .router.adapter import ModelAdapter

__version__ = "0.1.0"
__all__ = ["MilliAgent", "ManifoldEngine", "CaptureSource", "TypedDecision", "FastDecisionRouter", "ModelAdapter"]
