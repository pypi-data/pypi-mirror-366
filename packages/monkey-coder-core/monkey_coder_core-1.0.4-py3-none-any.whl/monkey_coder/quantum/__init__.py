"""
Quantum Routing Engine

This module implements the quantum routing capabilities for the Monkey Coder
platform, providing intelligent AI model selection using Deep Q-Network (DQN)
algorithms and multi-strategy parallel execution patterns.

Built on proven patterns from the monkey1 project and adapted for the
Monkey Coder platform's specific routing requirements.
"""

from .dqn_agent import DQNRoutingAgent, RoutingAction, RoutingState

__all__ = [
    "DQNRoutingAgent",
    "RoutingAction", 
    "RoutingState",
]

__version__ = "1.0.0"