"""New LangGraph Agent.

This module defines a custom graph.
"""
from agent.Extend import extend_graph
from agent.graph import graph
from agent.Recommend import recommend_graph
from agent.Reserve import reserve_graph
__all__ = ["graph","recommend_graph","reserve_graph","extend_graph"]
