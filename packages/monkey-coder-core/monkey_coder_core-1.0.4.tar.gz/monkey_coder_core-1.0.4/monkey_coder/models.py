"""
Pydantic models for Monkey Coder Core API.

This module defines all the data models used for API requests and responses,
including validation, serialization, and documentation.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class TaskStatus(str, Enum):
    """Task execution status enumeration."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(str, Enum):
    """Task type enumeration."""

    CODE_GENERATION = "code_generation"
    CODE_ANALYSIS = "code_analysis"
    CODE_REVIEW = "code_review"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    DEBUGGING = "debugging"
    REFACTORING = "refactoring"
    CUSTOM = "custom"


class ProviderType(str, Enum):
    """AI provider type enumeration."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    GROK = "grok"
    GROQ = "groq"  # Hardware-accelerated inference provider


class PersonaType(str, Enum):
    """SuperClaude persona types."""

    DEVELOPER = "developer"
    ARCHITECT = "architect"
    REVIEWER = "reviewer"
    SECURITY_ANALYST = "security_analyst"
    PERFORMANCE_EXPERT = "performance_expert"
    TESTER = "tester"
    TECHNICAL_WRITER = "technical_writer"
    CUSTOM = "custom"


class ExecutionContext(BaseModel):
    """Execution context for task processing."""

    user_id: str = Field(..., description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    workspace_id: Optional[str] = Field(None, description="Workspace identifier")
    environment: str = Field(default="production", description="Execution environment")
    timeout: int = Field(default=300, description="Execution timeout in seconds")
    max_tokens: int = Field(default=4096, description="Maximum tokens for generation")
    temperature: float = Field(default=0.1, description="Model temperature")

    @field_validator("timeout")
    @classmethod
    def validate_timeout(cls, v):
        if v < 1 or v > 3600:
            raise ValueError("Timeout must be between 1 and 3600 seconds")
        return v

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v):
        if v < 0.0 or v > 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return v


class SuperClaudeConfig(BaseModel):
    """Configuration for SuperClaude slash-command & persona router."""

    persona: PersonaType = Field(..., description="Persona type for task execution")
    slash_commands: List[str] = Field(
        default_factory=list, description="Enabled slash commands"
    )
    context_window: int = Field(default=32768, description="Context window size")
    use_markdown_spec: bool = Field(
        default=True, description="Use markdown specification"
    )
    custom_instructions: Optional[str] = Field(
        None, description="Custom persona instructions"
    )


class Monkey1Config(BaseModel):
    """Configuration for monkey1 multi-agent orchestrator."""

    agent_count: int = Field(default=3, description="Number of agents")
    coordination_strategy: str = Field(
        default="collaborative", description="Agent coordination strategy"
    )
    consensus_threshold: float = Field(
        default=0.7, description="Consensus threshold for decisions"
    )
    enable_reflection: bool = Field(default=True, description="Enable agent reflection")
    max_iterations: int = Field(
        default=5, description="Maximum orchestration iterations"
    )

    @field_validator("agent_count")
    @classmethod
    def validate_agent_count(cls, v):
        if v < 1 or v > 10:
            raise ValueError("Agent count must be between 1 and 10")
        return v


class Gary8DConfig(BaseModel):
    """Configuration for Gary8D functional-quantum executor."""

    parallel_futures: bool = Field(
        default=True, description="Enable parallel execution"
    )
    collapse_strategy: str = Field(
        default="weighted_average", description="Quantum collapse strategy"
    )
    quantum_coherence: float = Field(default=0.8, description="Quantum coherence level")
    execution_branches: int = Field(
        default=3, description="Number of execution branches"
    )
    uncertainty_threshold: float = Field(
        default=0.1, description="Uncertainty threshold"
    )

    @field_validator("quantum_coherence")
    @classmethod
    def validate_coherence(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError("Quantum coherence must be between 0.0 and 1.0")
        return v


class ExecuteRequest(BaseModel):
    """Request model for task execution."""

    task_id: str = Field(
        default_factory=lambda: str(uuid4()), description="Unique task identifier"
    )
    task_type: TaskType = Field(..., description="Type of task to execute")
    prompt: str = Field(..., description="Task prompt or description")
    files: Optional[List[Dict[str, Any]]] = Field(None, description="Associated files")

    # Configuration sections
    context: ExecutionContext = Field(..., description="Execution context")
    superclaude_config: SuperClaudeConfig = Field(
        ..., description="SuperClaude configuration"
    )
    monkey1_config: Monkey1Config = Field(
        default_factory=Monkey1Config, description="Monkey1 configuration"
    )
    gary8d_config: Gary8DConfig = Field(
        default_factory=Gary8DConfig, description="Gary8D configuration"
    )

    # Provider preferences
    preferred_providers: List[ProviderType] = Field(
        default_factory=list, description="Preferred AI providers"
    )
    model_preferences: Dict[ProviderType, str] = Field(
        default_factory=dict, description="Model preferences by provider"
    )

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Prompt cannot be empty")
        # Allow short prompts - they will be enhanced by PersonaValidator
        # Minimum length reduced from 10 to 1 to handle single-word inputs
        if len(v.strip()) < 1:
            raise ValueError("Prompt must contain at least one character")
        return v.strip()


class UsageMetrics(BaseModel):
    """Usage metrics for task execution."""

    tokens_used: int = Field(..., description="Total tokens consumed")
    tokens_input: int = Field(..., description="Input tokens")
    tokens_output: int = Field(..., description="Output tokens")
    provider_breakdown: Dict[str, int] = Field(
        ..., description="Token usage by provider"
    )
    cost_estimate: float = Field(..., description="Estimated cost in USD")
    execution_time: float = Field(..., description="Execution time in seconds")


class ExecutionResult(BaseModel):
    """Result of task execution."""

    result: Any = Field(..., description="Execution result")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Execution metadata"
    )
    artifacts: List[Dict[str, Any]] = Field(
        default_factory=list, description="Generated artifacts"
    )
    confidence_score: float = Field(..., description="Confidence score (0.0-1.0)")
    quantum_collapse_info: Dict[str, Any] = Field(
        default_factory=dict, description="Quantum collapse information"
    )


class ExecuteResponse(BaseModel):
    """Response model for task execution."""

    execution_id: str = Field(..., description="Execution identifier")
    task_id: str = Field(..., description="Task identifier")
    status: TaskStatus = Field(..., description="Execution status")
    result: Optional[ExecutionResult] = Field(None, description="Execution result")
    error: Optional[str] = Field(None, description="Error message if failed")

    # Metadata
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    usage: Optional[UsageMetrics] = Field(None, description="Usage metrics")
    execution_time: Optional[float] = Field(None, description="Total execution time")

    # Integration info
    superclause_routing: Dict[str, Any] = Field(
        default_factory=dict, description="SuperClaude routing info"
    )
    monkey1_orchestration: Dict[str, Any] = Field(
        default_factory=dict, description="Monkey1 orchestration info"
    )
    gary8d_execution: Dict[str, Any] = Field(
        default_factory=dict, description="Gary8D execution info"
    )


class UsageRequest(BaseModel):
    """Request model for usage metrics."""

    start_date: Optional[datetime] = Field(None, description="Start date for metrics")
    end_date: Optional[datetime] = Field(None, description="End date for metrics")
    granularity: str = Field(default="daily", description="Metrics granularity")
    include_details: bool = Field(
        default=False, description="Include detailed breakdown"
    )

    @field_validator("granularity")
    @classmethod
    def validate_granularity(cls, v):
        if v not in ["hourly", "daily", "weekly", "monthly"]:
            raise ValueError(
                "Granularity must be one of: hourly, daily, weekly, monthly"
            )
        return v


class ProviderUsage(BaseModel):
    """Usage metrics for a specific provider."""

    provider: ProviderType = Field(..., description="Provider type")
    model_usage: Dict[str, int] = Field(..., description="Usage by model")
    total_tokens: int = Field(..., description="Total tokens used")
    total_requests: int = Field(..., description="Total requests made")
    total_cost: float = Field(..., description="Total cost in USD")
    average_latency: float = Field(..., description="Average response latency")
    error_rate: float = Field(..., description="Error rate percentage")


class RateLimitStatus(BaseModel):
    """Rate limiting status information."""

    provider: ProviderType = Field(..., description="Provider type")
    current_usage: int = Field(..., description="Current usage count")
    limit: int = Field(..., description="Rate limit")
    reset_time: datetime = Field(..., description="Reset timestamp")
    remaining: int = Field(..., description="Remaining requests")


class UsageResponse(BaseModel):
    """Response model for usage metrics."""

    api_key_hash: str = Field(..., description="Hashed API key identifier")
    period: Dict[str, datetime] = Field(..., description="Query period")
    total_requests: int = Field(..., description="Total requests in period")
    total_tokens: int = Field(..., description="Total tokens consumed")
    total_cost: float = Field(..., description="Total cost in USD")

    # Detailed breakdowns
    provider_breakdown: List[ProviderUsage] = Field(
        ..., description="Usage by provider"
    )
    execution_stats: Dict[str, Any] = Field(..., description="Execution statistics")
    rate_limit_status: List[RateLimitStatus] = Field(
        ..., description="Rate limit status"
    )

    # Trends and insights
    daily_usage: List[Dict[str, Any]] = Field(
        default_factory=list, description="Daily usage breakdown"
    )
    cost_trends: Dict[str, Any] = Field(
        default_factory=dict, description="Cost trend analysis"
    )
    performance_metrics: Dict[str, Any] = Field(
        default_factory=dict, description="Performance metrics"
    )


class ProviderInfo(BaseModel):
    """Information about an AI provider."""

    name: str = Field(..., description="Provider name")
    type: ProviderType = Field(..., description="Provider type")
    status: str = Field(..., description="Provider status")
    available_models: List[str] = Field(..., description="Available models")
    rate_limits: Dict[str, Any] = Field(..., description="Rate limit information")
    pricing: Dict[str, Any] = Field(..., description="Pricing information")
    capabilities: List[str] = Field(..., description="Provider capabilities")
    last_updated: datetime = Field(..., description="Last update timestamp")


class ModelInfo(BaseModel):
    """Information about an AI model."""

    name: str = Field(..., description="Model name")
    provider: ProviderType = Field(..., description="Provider type")
    type: str = Field(..., description="Model type (e.g., 'text-generation', 'chat')")
    context_length: int = Field(..., description="Maximum context length")
    input_cost: float = Field(..., description="Input cost per token")
    output_cost: float = Field(..., description="Output cost per token")
    capabilities: List[str] = Field(..., description="Model capabilities")
    description: str = Field(..., description="Model description")
    version: Optional[str] = Field(None, description="Model version")
    release_date: Optional[datetime] = Field(None, description="Release date")


# Exception models
class ExecutionError(Exception):
    """Custom exception for task execution errors."""

    def __init__(
        self,
        message: str,
        error_code: str = "EXECUTION_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ProviderError(Exception):
    """Custom exception for provider-related errors."""

    def __init__(
        self,
        message: str,
        provider: str,
        error_code: str = "PROVIDER_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.provider = provider
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(Exception):
    """Custom exception for validation errors."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        error_code: str = "VALIDATION_ERROR",
    ):
        self.message = message
        self.field = field
        self.error_code = error_code
        super().__init__(self.message)


# Model registry for dynamic model discovery
# Models from https://github.com/GaryOcean428/ai-models-api-docs.git
# Full documentation at https://ai1docs.abacusai.app/
# Add to top of MODEL_REGISTRY section
DEFAULT_MODELS = {
    ProviderType.ANTHROPIC: "claude-sonnet-4-20250514",  # Default as per user spec
    # Defaults for other providers
    ProviderType.OPENAI: "gpt-4.1",
    ProviderType.GOOGLE: "gemini-2.5-pro",
    ProviderType.GROK: "grok-4-latest",
    ProviderType.GROQ: "llama-3.3-70b-versatile",
}

MODEL_REGISTRY = {
    ProviderType.OPENAI: [
        # GPT-4.1 Family (Flagship models - always use these instead of gpt-4o)
        "gpt-4.1",
        "gpt-4.1-mini",
        "gpt-4.1-nano",
        # Reasoning models
        "o1",
        "o1-mini",
        "o3",
        "o3-pro",
        "o4-mini",
        "o3-deep-research",
        "o4-mini-deep-research",
        # Search models
        "gpt-4o-search-preview",
        "gpt-4o-mini-search-preview",
        # Specialized
        "codex-mini-latest",
        # Legacy (deprecated - DO NOT USE)
        # "gpt-4o",  # Use gpt-4.1 instead
        # "gpt-4o-mini",  # Use gpt-4.1-mini instead
        # "chatgpt-4o-latest",  # Use gpt-4.1 instead
    ],
    ProviderType.ANTHROPIC: [
        # Claude 4 Family
        "claude-opus-4-20250514",
        "claude-sonnet-4-20250514",
        # Claude 3.7
        "claude-3-7-sonnet-20250219",
        # Claude 3.5
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
    ],
    ProviderType.GOOGLE: [
        # Gemini 2.5 Family
        "gemini-2.5-pro",
        "models/gemini-2.5-flash",
        "models/gemini-2.5-flash-lite",
        # Gemini 2.0 Family
        "models/gemini-2.0-flash",
        "models/gemini-2.0-flash-lite",
        # Live models
        "models/gemini-live-2.5-flash-preview",
        "models/gemini-2.0-flash-live-001",
    ],
    ProviderType.GROK: [
        # xAI Grok models
        "grok-4-latest",
        "grok-3",
        "grok-3-mini",
        "grok-3-mini-fast",
        "grok-3-fast",
    ],
    ProviderType.GROQ: [
        # Llama models (excluding R1)
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "meta-llama/llama-4-maverick-17b-128e-instruct",
        "meta-llama/llama-4-scout-17b-16e-instruct",
        # Kimi model
        "moonshotai/kimi-k2-instruct",
        # Qwen model
        "qwen/qwen3-32b",
    ],
}

# Cross-provider model mapping
# Some models are available through multiple providers
CROSS_PROVIDER_MODELS = {
    # Currently all models are accessed through their primary providers
    # Groq hosts models from other vendors but we track them under Groq
}

# Model aliases for backward compatibility
# Maps old names to new approved names
MODEL_ALIASES = {
    "gpt-4o": "gpt-4.1",
    "gpt-4o-mini": "gpt-4.1-mini",
    "gpt-4": "gpt-4.1",
    "gpt-4-turbo": "gpt-4.1",
    "claude-3-5-sonnet-latest": "claude-3-5-sonnet-20241022",  # Non-default alias
    "claude-sonnet-4-0": "claude-opus-4-20250514",  # Alias for latest Claude 4 (Opus)
    "opus": "claude-opus-4-20250514",  # Alias for Opus/latest
    "claude-4-latest": "claude-opus-4-20250514",  # General latest
}

# New resolve_model function
def resolve_model(model_name: str, provider: ProviderType) -> str:
    """Resolve model name with aliases and latest handling."""
    if model_name in MODEL_ALIASES:
        return MODEL_ALIASES[model_name]
    # Latest handling example
    if model_name == "claude-4-latest":
        return "claude-opus-4-20250514"  # Or dynamic based on registry
    return model_name  # Fallback


def get_available_models(
    provider: Optional[ProviderType] = None,
) -> Dict[str, List[str]]:
    """
    Get available models, optionally filtered by provider.

    Args:
        provider: Optional provider filter

    Returns:
        Dictionary mapping provider names to model lists
    """
    if provider:
        return {provider.value: MODEL_REGISTRY.get(provider, [])}

    return {p.value: models for p, models in MODEL_REGISTRY.items()}


class HealthResponse(BaseModel):
    """Health check response model for Railway deployment."""
    
    status: str = Field(..., description="Overall service health status")
    version: str = Field(..., description="Application version")
    timestamp: str = Field(..., description="Health check timestamp (ISO format)")
    components: Dict[str, str] = Field(
        default_factory=dict, 
        description="Status of individual components"
    )
