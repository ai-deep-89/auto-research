"""
AutoResearch Multi-Agent System

A production-ready autonomous research agent framework featuring:
- Multi-agent collaboration
- Task planning and execution
- Self-evolution mechanisms
- Automated evaluation
"""

__version__ = "0.1.0"

from src.core.system import AutoResearchSystem
from src.core.multi_agent import MultiAgentCrew
from src.agents.base_agent import BaseAgent
from src.evolution.evolution_engine import EvolutionEngine

__all__ = [
    "AutoResearchSystem",
    "MultiAgentCrew",
    "BaseAgent",
    "EvolutionEngine",
]
