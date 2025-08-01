"""
Enhanced DQN Agent for Quantum Routing Engine

This module implements a Deep Q-Network agent for intelligent AI model routing,
building on proven patterns from the monkey1 project and adapted for the 
Monkey Coder platform's quantum routing requirements.
"""

import json
import logging
import random
from collections import deque
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from monkey_coder.models import ProviderType

logger = logging.getLogger(__name__)


@dataclass
class RoutingState:
    """Represents the state for routing decisions in the DQN."""
    
    task_complexity: float  # 0.0-1.0 scale
    context_type: str  # e.g., "code_generation", "analysis", "debugging"
    provider_availability: Dict[str, bool]  # Available providers
    historical_performance: Dict[str, float]  # Provider performance history
    resource_constraints: Dict[str, Any]  # Cost, time, quality constraints
    user_preferences: Dict[str, Any]  # User-specific preferences
    
    def to_vector(self) -> np.ndarray:
        """Convert state to numerical vector for neural network input."""
        # Create a fixed-size vector representation
        vector = [
            self.task_complexity,
            # Context type as one-hot encoding (simplified to 10 categories)
            1.0 if self.context_type == "code_generation" else 0.0,
            1.0 if self.context_type == "analysis" else 0.0,
            1.0 if self.context_type == "debugging" else 0.0,
            1.0 if self.context_type == "documentation" else 0.0,
            1.0 if self.context_type == "testing" else 0.0,
            1.0 if self.context_type == "planning" else 0.0,
            1.0 if self.context_type == "research" else 0.0,
            1.0 if self.context_type == "creative" else 0.0,
            1.0 if self.context_type == "reasoning" else 0.0,
            1.0 if self.context_type == "general" else 0.0,
        ]
        
        # Provider availability (assuming 5 main providers)
        providers = ["openai", "anthropic", "google", "groq", "grok"]
        for provider in providers:
            vector.append(1.0 if self.provider_availability.get(provider, False) else 0.0)
        
        # Historical performance (average of all providers, 0-1 scale)
        avg_performance = np.mean(list(self.historical_performance.values())) if self.historical_performance else 0.5
        vector.append(avg_performance)
        
        # Resource constraints (simplified to 3 values: cost_weight, time_weight, quality_weight)
        vector.extend([
            self.resource_constraints.get("cost_weight", 0.33),
            self.resource_constraints.get("time_weight", 0.33),
            self.resource_constraints.get("quality_weight", 0.33),
        ])
        
        # User preferences (simplified to preference strength 0-1)
        vector.append(self.user_preferences.get("preference_strength", 0.5))
        
        return np.array(vector, dtype=np.float32)


@dataclass
class RoutingAction:
    """Represents a routing action (provider + model selection)."""
    
    provider: ProviderType
    model: str
    strategy: str  # "task_optimized", "cost_efficient", "performance", "balanced"
    
    @classmethod
    def from_action_index(cls, action_index: int) -> "RoutingAction":
        """Convert action index to routing action."""
        # Define action space (simplified for initial implementation)
        actions = [
            # OpenAI actions
            (ProviderType.OPENAI, "chatgpt-4.1", "performance"),
            (ProviderType.OPENAI, "o4-mini", "cost_efficient"),
            (ProviderType.OPENAI, "o1-mini", "task_optimized"),
            # Anthropic actions
            (ProviderType.ANTHROPIC, "claude-3-7-sonnet-20250219", "performance"),
            (ProviderType.ANTHROPIC, "claude-3-5-sonnet-latest", "balanced"),
            (ProviderType.ANTHROPIC, "claude-3-5-haiku-latest", "cost_efficient"),
            # Google actions
            (ProviderType.GOOGLE, "gemini-2.0-pro-experimental", "performance"),
            (ProviderType.GOOGLE, "gemini-2.0-flash", "balanced"),
            (ProviderType.GOOGLE, "gemini-2.0-flash-lite", "cost_efficient"),
            # Groq actions
            (ProviderType.GROQ, "llama-3.1-70b-versatile", "task_optimized"),
            (ProviderType.GROQ, "llama-3.2-11b-text-preview", "balanced"),
            # Grok actions
            (ProviderType.GROK, "grok-2-latest", "performance"),
        ]
        
        if action_index >= len(actions):
            # Default fallback action
            action_index = 0
            
        provider, model, strategy = actions[action_index]
        return cls(provider=provider, model=model, strategy=strategy)
    
    def to_action_index(self) -> int:
        """Convert routing action to action index."""
        # This is the reverse mapping - simplified for initial implementation
        action_map = {
            (ProviderType.OPENAI, "chatgpt-4.1", "performance"): 0,
            (ProviderType.OPENAI, "o4-mini", "cost_efficient"): 1,
            (ProviderType.OPENAI, "o1-mini", "task_optimized"): 2,
            (ProviderType.ANTHROPIC, "claude-3-7-sonnet-20250219", "performance"): 3,
            (ProviderType.ANTHROPIC, "claude-3-5-sonnet-latest", "balanced"): 4,
            (ProviderType.ANTHROPIC, "claude-3-5-haiku-latest", "cost_efficient"): 5,
            (ProviderType.GOOGLE, "gemini-2.0-pro-experimental", "performance"): 6,
            (ProviderType.GOOGLE, "gemini-2.0-flash", "balanced"): 7,
            (ProviderType.GOOGLE, "gemini-2.0-flash-lite", "cost_efficient"): 8,
            (ProviderType.GROQ, "llama-3.1-70b-versatile", "task_optimized"): 9,
            (ProviderType.GROQ, "llama-3.2-11b-text-preview", "balanced"): 10,
            (ProviderType.GROK, "grok-2-latest", "performance"): 11,
        }
        
        return action_map.get((self.provider, self.model, self.strategy), 0)


class DQNRoutingAgent:
    """
    Enhanced Deep Q-Network agent for intelligent AI model routing.
    
    Built on proven patterns from monkey1's DQN implementation and adapted
    for the Monkey Coder platform's quantum routing engine.
    """
    
    def __init__(
        self,
        state_size: int = 21,  # Size of state vector from RoutingState.to_vector()
        action_size: int = 12,  # Number of possible routing actions
        learning_rate: float = 0.001,
        discount_factor: float = 0.99,
        exploration_rate: float = 1.0,
        exploration_decay: float = 0.995,
        exploration_min: float = 0.01,
        memory_size: int = 2000,
        batch_size: int = 64,
        target_update_frequency: int = 10,  # Update target network every N training steps
    ):
        """
        Initialize the DQN routing agent.
        
        Args:
            state_size: Dimension of the state space
            action_size: Number of possible actions
            learning_rate: Learning rate for neural network training
            discount_factor: Discount factor for future rewards
            exploration_rate: Initial exploration rate (epsilon)
            exploration_decay: Decay rate for exploration
            exploration_min: Minimum exploration rate
            memory_size: Size of experience replay buffer
            batch_size: Batch size for training
            target_update_frequency: How often to update target network
        """
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.exploration_min = exploration_min
        self.batch_size = batch_size
        self.target_update_frequency = target_update_frequency
        
        # Experience replay buffer (following monkey1 pattern)
        self.memory = deque(maxlen=memory_size)
        
        # Training step counter for target network updates
        self.training_step = 0
        
        # Performance tracking
        self.training_history = []
        self.routing_performance = {}  # Track performance by provider/model
        
        # Initialize Q-network and target Q-network
        # Note: Actual neural network implementation will be added in T2.1.3
        self.q_network = None  # Will be initialized when neural network is implemented
        self.target_q_network = None  # Will be initialized when neural network is implemented
        
        logger.info(f"Initialized DQN routing agent with state_size={state_size}, action_size={action_size}")
    
    def remember(
        self,
        state: RoutingState,
        action: RoutingAction,
        reward: float,
        next_state: RoutingState,
        done: bool,
    ) -> None:
        """
        Store experience in replay buffer.
        
        Args:
            state: Current routing state
            action: Action taken
            reward: Reward received
            next_state: Resulting state
            done: Whether episode is complete
        """
        experience = (
            state.to_vector(),
            action.to_action_index(),
            reward,
            next_state.to_vector(),
            done
        )
        self.memory.append(experience)
        
        logger.debug(f"Stored experience: reward={reward}, action={action.provider}:{action.model}")
    
    def act(self, state: RoutingState) -> RoutingAction:
        """
        Choose an action based on the current state using epsilon-greedy policy.
        
        Args:
            state: Current routing state
            
        Returns:
            Selected routing action
        """
        # Epsilon-greedy action selection
        if np.random.rand() <= self.exploration_rate:
            # Explore: choose random action
            action_index = random.randrange(self.action_size)
            logger.debug(f"Exploration: selected random action {action_index}")
        else:
            # Exploit: choose best action based on Q-values
            if self.q_network is None:
                # Fallback to random action if network not initialized
                action_index = random.randrange(self.action_size)
                logger.warning("Q-network not initialized, using random action")
            else:
                # This will be implemented when neural network is ready (T2.1.3)
                state_vector = state.to_vector().reshape(1, -1)
                q_values = self.q_network.predict(state_vector, verbose=0)
                action_index = np.argmax(q_values[0])
                logger.debug(f"Exploitation: selected action {action_index} with Q-value {q_values[0][action_index]:.3f}")
        
        return RoutingAction.from_action_index(action_index)
    
    def calculate_reward(
        self,
        action: RoutingAction,
        routing_result: Dict[str, Any],
        execution_metrics: Dict[str, float]
    ) -> float:
        """
        Calculate reward for a routing decision based on performance metrics.
        
        Args:
            action: The routing action taken
            routing_result: Result of the routing decision
            execution_metrics: Performance metrics from execution
            
        Returns:
            Reward value (higher is better)
        """
        reward = 0.0
        
        # Base reward for successful routing
        if routing_result.get("success", False):
            reward += 1.0
        else:
            reward -= 0.5
        
        # Performance-based rewards
        response_time = execution_metrics.get("response_time", 5.0)  # seconds
        if response_time < 1.0:
            reward += 0.3  # Fast response bonus
        elif response_time > 10.0:
            reward -= 0.3  # Slow response penalty
        
        # Quality-based rewards
        quality_score = execution_metrics.get("quality_score", 0.5)  # 0-1 scale
        reward += (quality_score - 0.5) * 0.5  # Bonus/penalty for quality
        
        # Cost efficiency rewards
        cost_efficiency = execution_metrics.get("cost_efficiency", 0.5)  # 0-1 scale
        if action.strategy == "cost_efficient":
            reward += cost_efficiency * 0.2
        
        # Strategy alignment rewards
        if action.strategy == "performance" and quality_score > 0.8:
            reward += 0.2
        elif action.strategy == "balanced" and 0.6 <= quality_score <= 0.8:
            reward += 0.1
        
        # Provider-specific adjustments based on historical performance
        provider_key = f"{action.provider}:{action.model}"
        historical_performance = self.routing_performance.get(provider_key, 0.5)
        reward += (historical_performance - 0.5) * 0.1  # Small adjustment based on history
        
        logger.debug(f"Calculated reward {reward:.3f} for {provider_key} (strategy: {action.strategy})")
        return reward
    
    def replay(self) -> Optional[float]:
        """
        Train the DQN using experience replay.
        
        Returns:
            Average loss from training batch, or None if not enough experiences
        """
        if len(self.memory) < self.batch_size:
            return None
        
        if self.q_network is None or self.target_q_network is None:
            logger.warning("Neural networks not initialized, skipping replay")
            return None
        
        # Sample random minibatch from experience buffer
        minibatch = random.sample(self.memory, self.batch_size)
        
        total_loss = 0.0
        
        for state, action, reward, next_state, done in minibatch:
            # Calculate target Q-value
            target = reward
            if not done:
                # Use target network for stable learning (Double DQN approach)
                next_q_values = self.target_q_network.predict(
                    next_state.reshape(1, -1), verbose=0
                )
                target += self.discount_factor * np.amax(next_q_values[0])
            
            # Get current Q-values
            current_q_values = self.q_network.predict(state.reshape(1, -1), verbose=0)
            current_q_values[0][action] = target
            
            # Train the network
            history = self.q_network.fit(
                state.reshape(1, -1),
                current_q_values,
                epochs=1,
                verbose=0
            )
            total_loss += history.history.get('loss', [0.0])[0]
        
        # Decay exploration rate
        if self.exploration_rate > self.exploration_min:
            self.exploration_rate *= self.exploration_decay
        
        # Update target network periodically
        self.training_step += 1
        if self.training_step % self.target_update_frequency == 0:
            self.update_target_network()
            logger.debug(f"Updated target network at training step {self.training_step}")
        
        avg_loss = total_loss / self.batch_size
        self.training_history.append({
            "step": self.training_step,
            "loss": avg_loss,
            "exploration_rate": self.exploration_rate,
            "memory_size": len(self.memory)
        })
        
        logger.debug(f"Training step {self.training_step}: avg_loss={avg_loss:.4f}, exploration_rate={self.exploration_rate:.3f}")
        return avg_loss
    
    def update_target_network(self) -> None:
        """Update target Q-network with weights from main Q-network."""
        if self.q_network is None or self.target_q_network is None:
            return
        
        # Copy weights from main network to target network
        self.target_q_network.set_weights(self.q_network.get_weights())
        logger.debug("Updated target network weights")
    
    def update_routing_performance(
        self,
        action: RoutingAction,
        performance_score: float
    ) -> None:
        """
        Update historical performance tracking for routing decisions.
        
        Args:
            action: The routing action taken
            performance_score: Performance score (0-1 scale)
        """
        provider_key = f"{action.provider}:{action.model}"
        
        # Update running average of performance
        if provider_key in self.routing_performance:
            current_avg = self.routing_performance[provider_key]
            # Weighted average with recent performance getting higher weight
            self.routing_performance[provider_key] = 0.8 * current_avg + 0.2 * performance_score
        else:
            self.routing_performance[provider_key] = performance_score
        
        logger.debug(f"Updated performance for {provider_key}: {self.routing_performance[provider_key]:.3f}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get current performance metrics and statistics.
        
        Returns:
            Dictionary containing performance metrics
        """
        return {
            "exploration_rate": self.exploration_rate,
            "training_steps": self.training_step,
            "memory_utilization": len(self.memory) / self.memory.maxlen,
            "routing_performance": dict(self.routing_performance),
            "recent_training_loss": self.training_history[-10:] if self.training_history else [],
            "action_space_size": self.action_size,
            "state_space_size": self.state_size,
        }
    
    def save_model(self, filepath: str) -> None:
        """
        Save the trained model to disk.
        
        Args:
            filepath: Path to save the model
        """        
        try:
            # Save neural network weights (if available)
            if self.q_network is not None:
                self.q_network.save_weights(f"{filepath}_weights.h5")
            
            # Save agent configuration and performance data
            config_data = {
                "state_size": self.state_size,
                "action_size": self.action_size,
                "learning_rate": self.learning_rate,
                "discount_factor": self.discount_factor,
                "exploration_rate": self.exploration_rate,
                "exploration_decay": self.exploration_decay,
                "exploration_min": self.exploration_min,
                "batch_size": self.batch_size,
                "target_update_frequency": self.target_update_frequency,
                "training_step": self.training_step,
                "routing_performance": self.routing_performance,
                "training_history": self.training_history[-100:],  # Keep last 100 entries
            }
            
            with open(f"{filepath}_config.json", "w") as f:
                json.dump(config_data, f, indent=2, default=str)
            
            logger.info(f"Saved DQN model to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
    
    def load_model(self, filepath: str) -> bool:
        """
        Load a trained model from disk.
        
        Args:
            filepath: Path to load the model from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load configuration first
            with open(f"{filepath}_config.json", "r") as f:
                config_data = json.load(f)
            
            # Update agent configuration
            self.exploration_rate = config_data.get("exploration_rate", self.exploration_rate)
            self.training_step = config_data.get("training_step", 0)
            self.routing_performance = config_data.get("routing_performance", {})
            self.training_history = config_data.get("training_history", [])
            
            # Load neural network weights (when network is implemented)
            if self.q_network is not None:
                self.q_network.load_weights(f"{filepath}_weights.h5")
                self.update_target_network()
            
            logger.info(f"Loaded DQN model from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False