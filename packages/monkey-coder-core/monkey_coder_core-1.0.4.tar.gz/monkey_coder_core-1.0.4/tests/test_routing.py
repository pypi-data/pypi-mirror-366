"""
Unit tests for the AdvancedRouter system.

This module contains comprehensive tests for the routing system including:
- Complexity analysis
- Context extraction
- Persona selection
- Model scoring and selection
- Slash command parsing
- Integration tests
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

import sys
from pathlib import Path

# Add the package to Python path
package_root = Path(__file__).parent.parent
sys.path.insert(0, str(package_root))

from monkey_coder.core.routing import (
    AdvancedRouter,
    ComplexityLevel,
    ContextType,
    RoutingDecision
)
from monkey_coder.models import (
    ExecuteRequest,
    TaskType,
    PersonaType,
    ProviderType,
    ExecutionContext,
    SuperClaudeConfig,
)


class TestAdvancedRouter:
    """Test suite for AdvancedRouter functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.router = AdvancedRouter()
        self.context = ExecutionContext(user_id="test_user")
        self.superclaude_config = SuperClaudeConfig(persona=PersonaType.DEVELOPER)
        
    def create_request(self, prompt: str, task_type: TaskType = TaskType.CODE_GENERATION, files=None):
        """Helper to create test requests."""
        return ExecuteRequest(
            prompt=prompt,
            task_type=task_type,
            context=self.context,
            superclaude_config=self.superclaude_config,
            files=files or []
        )
    
    def test_complexity_analysis_trivial(self):
        """Test complexity analysis for trivial prompts."""
        request = self.create_request("Hello world")
        score = self.router._analyze_complexity(request)
        level = self.router._classify_complexity(score)
        
        assert score < 0.2
        assert level == ComplexityLevel.TRIVIAL
    
    def test_complexity_analysis_simple(self):
        """Test complexity analysis for simple coding tasks."""
        request = self.create_request("Write a function to add two numbers")
        score = self.router._analyze_complexity(request)
        level = self.router._classify_complexity(score)
        
        assert 0.2 <= score < 0.4
        assert level == ComplexityLevel.SIMPLE
    
    def test_complexity_analysis_moderate(self):
        """Test complexity analysis for moderate tasks."""
        request = self.create_request(
            "Create a class for managing user authentication with "
            "methods for login, logout, and session validation"
        )
        score = self.router._analyze_complexity(request)
        level = self.router._classify_complexity(score)
        
        assert 0.4 <= score < 0.6
        assert level == ComplexityLevel.MODERATE
    
    def test_complexity_analysis_complex(self):
        """Test complexity analysis for complex tasks."""
        request = self.create_request(
            "Design a distributed microservices architecture for an e-commerce platform "
            "with scalability, performance optimization, database sharding, and async processing. "
            "Include detailed system design patterns, data structures, and algorithm considerations."
        )
        score = self.router._analyze_complexity(request)
        level = self.router._classify_complexity(score)
        
        assert 0.6 <= score < 0.8
        assert level == ComplexityLevel.COMPLEX
    
    def test_complexity_analysis_critical(self):
        """Test complexity analysis for critical tasks."""
        request = self.create_request(
            "Implement a comprehensive machine learning pipeline with distributed training, "
            "neural network architecture optimization, concurrent data processing, async I/O, "
            "performance profiling, security hardening, scalability testing, algorithm design, "
            "system architecture, microservices integration, database optimization, and threading. "
            "This is a multi-step, multi-phase project requiring deep technical expertise.",
            files=[{"name": f"file{i}.py", "content": "code"} for i in range(10)]
        )
        score = self.router._analyze_complexity(request)
        level = self.router._classify_complexity(score)
        
        assert score >= 0.8
        assert level == ComplexityLevel.CRITICAL
    
    def test_context_extraction_code_generation(self):
        """Test context extraction for code generation tasks."""
        request = self.create_request(
            "Generate a Python function to create a REST API endpoint",
            TaskType.CODE_GENERATION
        )
        context_type = self.router._extract_context_type(request)
        
        assert context_type == ContextType.CODE_GENERATION
    
    def test_context_extraction_debugging(self):
        """Test context extraction for debugging tasks."""
        request = self.create_request(
            "Fix this error: TypeError: 'int' object is not callable",
            TaskType.DEBUGGING
        )
        context_type = self.router._extract_context_type(request)
        
        assert context_type == ContextType.DEBUGGING
    
    def test_context_extraction_architecture(self):
        """Test context extraction for architecture tasks."""
        request = self.create_request(
            "Design the overall architecture and structure for a web application"
        )
        context_type = self.router._extract_context_type(request)
        
        assert context_type == ContextType.ARCHITECTURE
    
    def test_context_extraction_security(self):
        """Test context extraction for security tasks."""
        request = self.create_request(
            "Analyze security vulnerabilities and implement authentication"
        )
        context_type = self.router._extract_context_type(request)
        
        assert context_type == ContextType.SECURITY
    
    def test_slash_command_parsing(self):
        """Test slash command parsing from prompts."""
        # Test various slash commands
        assert self.router._parse_slash_commands("/dev create a function") == "dev"
        assert self.router._parse_slash_commands("/arch design system") == "arch"
        assert self.router._parse_slash_commands("/security audit code") == "security"
        assert self.router._parse_slash_commands("no slash command here") is None
        assert self.router._parse_slash_commands("/test write unit tests") == "test"
    
    def test_persona_selection_from_config(self):
        """Test persona selection from explicit config."""
        request = self.create_request("Write code", TaskType.CODE_GENERATION)
        request.superclaude_config.persona = PersonaType.ARCHITECT
        
        persona = self.router._select_persona(request, None, ContextType.CODE_GENERATION)
        
        assert persona == PersonaType.ARCHITECT
    
    def test_persona_selection_from_slash_command(self):
        """Test persona selection from slash commands."""
        request = self.create_request("/dev create a function")
        
        persona = self.router._select_persona(
            request, "dev", ContextType.CODE_GENERATION
        )
        
        assert persona == PersonaType.DEVELOPER
    
    def test_persona_selection_from_context(self):
        """Test persona selection from context type."""
        request = self.create_request("Review this code for issues")
        
        persona = self.router._select_persona(
            request, None, ContextType.CODE_REVIEW
        )
        
        assert persona == PersonaType.REVIEWER
    
    def test_model_scoring(self):
        """Test model scoring against requirements."""
        requirements = {
            'code_generation': 0.8,
            'reasoning': 0.7,
            'context_window': 16384,
            'reliability': 0.9,
        }
        
        scores = self.router._score_models(requirements)
        
        # Should have scores for available models
        assert len(scores) > 0
        
        # All scores should be between 0 and 1
        for score in scores.values():
            assert 0 <= score <= 1
        
        # GPT-4.1 should score highly for these requirements
        gpt41_score = scores.get((ProviderType.OPENAI, "gpt-4.1"))
        if gpt41_score:
            assert gpt41_score > 0.7
    
    def test_full_routing_simple_task(self):
        """Test full routing for a simple coding task."""
        request = self.create_request(
            "Write a Python function to calculate factorial"
        )
        
        decision = self.router.route_request(request)
        
        assert isinstance(decision, RoutingDecision)
        assert decision.provider in [p for p in ProviderType]
        assert decision.model is not None
        assert decision.persona == PersonaType.DEVELOPER  # Should default to developer
        assert 0 <= decision.complexity_score <= 1
        assert 0 <= decision.context_score <= 1
        assert decision.capability_score > 0  # Capability scores can exceed 1.0
        assert 0 <= decision.confidence <= 1
        assert decision.reasoning is not None
    
    def test_full_routing_complex_architecture_task(self):
        """Test full routing for a complex architecture task."""
        request = self.create_request(
            "/arch Design a scalable microservices architecture for a social media platform "
            "with performance optimization, security considerations, and database design"
        )
        
        decision = self.router.route_request(request)
        
        assert isinstance(decision, RoutingDecision)
        assert decision.persona == PersonaType.ARCHITECT  # Should select architect
        assert decision.complexity_score > 0.6  # Should be complex
        assert decision.provider in [ProviderType.OPENAI, ProviderType.ANTHROPIC]  # Prefer capable models
        assert "arch" in decision.metadata.get("slash_command", "")
    
    def test_full_routing_security_task(self):
        """Test full routing for a security-focused task."""
        request = self.create_request(
            "/security Audit this authentication system for vulnerabilities and implement secure session management"
        )
        
        decision = self.router.route_request(request)
        
        assert decision.persona == PersonaType.SECURITY_ANALYST
        assert decision.metadata.get("context_type") == ContextType.SECURITY.value
        assert decision.capability_score > 0.7  # Should require high capability
    
    def test_routing_with_preferred_providers(self):
        """Test routing respects user provider preferences."""
        request = self.create_request("Write a function")
        request.preferred_providers = [ProviderType.ANTHROPIC]
        
        decision = self.router.route_request(request)
        
        assert decision.provider == ProviderType.ANTHROPIC
    
    def test_routing_debug_info(self):
        """Test routing debug information generation."""
        request = self.create_request("Create a web API")
        
        debug_info = self.router.get_routing_debug_info(request)
        
        assert "routing_decision" in debug_info
        assert "scoring_breakdown" in debug_info
        assert "metadata" in debug_info
        assert "available_models" in debug_info
        
        # Check routing decision structure
        routing_decision = debug_info["routing_decision"]
        assert "provider" in routing_decision
        assert "model" in routing_decision
        assert "persona" in routing_decision
        assert "confidence" in routing_decision
        assert "reasoning" in routing_decision
        
        # Check scoring breakdown
        scoring = debug_info["scoring_breakdown"]
        assert "complexity_score" in scoring
        assert "context_score" in scoring
        assert "capability_score" in scoring
    
    def test_routing_history_tracking(self):
        """Test that routing decisions are tracked in history."""
        request1 = self.create_request("Create a simple function for testing")
        request2 = self.create_request("Write another function for validation")
        
        initial_count = len(self.router.routing_history)
        
        self.router.route_request(request1)
        assert len(self.router.routing_history) == initial_count + 1
        
        self.router.route_request(request2)
        assert len(self.router.routing_history) == initial_count + 2
    
    def test_cost_optimization_for_simple_tasks(self):
        """Test that simple tasks prefer cost-effective models."""
        request = self.create_request("What is 2+2?")  # Very simple task
        
        decision = self.router.route_request(request)
        
        # Should prefer cheaper models for simple tasks
        assert decision.complexity_score < 0.4
        # Check if a cost-effective model was selected (like gpt-4.1-mini or claude-haiku)
        cost_effective_models = ["gpt-4.1-mini", "claude-3.5-haiku"]
        assert decision.model in cost_effective_models or decision.capability_score > 0.8
    
    def test_high_complexity_prefers_capable_models(self):
        """Test that high complexity tasks prefer more capable models."""
        request = self.create_request(
            "Design and implement a distributed machine learning training system "
            "with fault tolerance, auto-scaling, and real-time model serving",
            files=[{"name": f"component_{i}.py", "content": "complex code"} for i in range(8)]
        )
        
        decision = self.router.route_request(request)
        
        # Should have high complexity score
        assert decision.complexity_score > 0.7
        
        # Should prefer capable models (GPT-4.1, Claude-4-Opus, Claude-4-Sonnet)
        capable_models = ["gpt-4.1", "claude-4-opus", "claude-4-sonnet"]
        assert decision.model in capable_models or decision.capability_score > 0.9


class TestRouterIntegration:
    """Integration tests for the routing system."""
    
    def setup_method(self):
        """Setup integration test fixtures."""
        self.router = AdvancedRouter()
    
    @pytest.mark.parametrize("prompt,expected_persona,expected_context", [
        ("Write a Python function", PersonaType.DEVELOPER, ContextType.CODE_GENERATION),
        ("Review this code for bugs", PersonaType.REVIEWER, ContextType.CODE_REVIEW),
        ("Fix this error message", PersonaType.DEVELOPER, ContextType.DEBUGGING),
        ("Design system architecture", PersonaType.ARCHITECT, ContextType.ARCHITECTURE),
        ("Audit for security issues", PersonaType.SECURITY_ANALYST, ContextType.SECURITY),
        ("Optimize performance", PersonaType.PERFORMANCE_EXPERT, ContextType.PERFORMANCE),
        ("Write unit tests", PersonaType.TESTER, ContextType.TESTING),
        ("Document this API", PersonaType.TECHNICAL_WRITER, ContextType.DOCUMENTATION),
    ])
    def test_routing_scenarios(self, prompt, expected_persona, expected_context):
        """Test various routing scenarios with expected outcomes."""
        context = ExecutionContext(user_id="test_user")
        superclaude_config = SuperClaudeConfig(persona=PersonaType.DEVELOPER)
        
        request = ExecuteRequest(
            prompt=prompt,
            task_type=TaskType.CUSTOM,
            context=context,
            superclaude_config=superclaude_config,
        )
        
        decision = self.router.route_request(request)
        
        # Check persona selection (unless overridden by config)
        if not hasattr(request, 'superclaude_config') or not request.superclaude_config:
            assert decision.persona == expected_persona
        
        # Check context extraction
        extracted_context = self.router._extract_context_type(request)
        assert extracted_context == expected_context
    
    def test_slash_command_integration(self):
        """Test slash command integration with full routing."""
        test_cases = [
            ("/dev create function", PersonaType.DEVELOPER),
            ("/arch design system", PersonaType.ARCHITECT),
            ("/security audit code", PersonaType.SECURITY_ANALYST),
            ("/test write tests", PersonaType.TESTER),
            ("/docs write documentation", PersonaType.TECHNICAL_WRITER),
        ]
        
        for prompt, expected_persona in test_cases:
            context = ExecutionContext(user_id="test_user")
            # Don't set explicit persona so slash commands can override
            superclaude_config = SuperClaudeConfig(persona=PersonaType.DEVELOPER)
            
            request = ExecuteRequest(
                prompt=prompt,
                task_type=TaskType.CUSTOM,
                context=context,
                superclaude_config=SuperClaudeConfig(persona=PersonaType.DEVELOPER),  # Will be overridden by slash commands
            )
            
            decision = self.router.route_request(request)
            assert decision.persona == expected_persona
    
    def test_routing_consistency(self):
        """Test that routing is consistent for identical requests."""
        context = ExecutionContext(user_id="test_user")
        superclaude_config = SuperClaudeConfig(persona=PersonaType.DEVELOPER)
        
        request = ExecuteRequest(
            prompt="Write a sorting algorithm",
            task_type=TaskType.CODE_GENERATION,
            context=context,
            superclaude_config=superclaude_config,
        )
        
        decision1 = self.router.route_request(request)
        decision2 = self.router.route_request(request)
        
        # Should route to same provider and model for identical requests
        assert decision1.provider == decision2.provider
        assert decision1.model == decision2.model
        assert decision1.persona == decision2.persona
        
        # Scores should be identical
        assert decision1.complexity_score == decision2.complexity_score
        assert decision1.context_score == decision2.context_score
        assert abs(decision1.capability_score - decision2.capability_score) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
