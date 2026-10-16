"""
Milli-Browser: Ultra-Lightweight, In-Loop Agent-First Browser Subsystem.
Inspired by Cypress in-loop execution and Laya single-pass decision principles.
"""

from .cdp_fast import FastCDPClient
from .engine import MilliBrowserEngine

__all__ = ["FastCDPClient", "MilliBrowserEngine"]
