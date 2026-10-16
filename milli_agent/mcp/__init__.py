"""
Model Context Protocol (MCP) server integration for Milli-Agent.
Enables LLMs and autonomous agents (Claude Desktop, Cursor, LangChain)
to actuate operating systems and web browsers at microsecond speed.
"""

from .server import MilliMCPServer

__all__ = ["MilliMCPServer"]
