"""
ImitateAI: Inverse Reinforcement Learning for LLMs.
"""
__version__ = "0.1.0"

from .modeling import RewardModeler
from .refinement import RecursiveRefiner

__all__ = ["RewardModeler", "RecursiveRefiner"]