"""
Anthropic Provider Adapter for Monkey Coder Core.

This adapter provides integration with Anthropic's API, including Claude models.
All model names are validated against official Anthropic documentation.
Updated to include only Claude 3.5+ models as of July 2025.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

try:
    from anthropic import AsyncAnthropic
except ImportError:
    AsyncAnthropic = None
    logging.warning(
        "Anthropic package not installed. Install it with: pip install anthropic"
    )

from . import BaseProvider
from ..models import ProviderType, ProviderError, ModelInfo
from ..logging_utils import monitor_api_calls

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseProvider):
    """
    Anthropic provider adapter implementing the BaseProvider interface.

    Provides access to Anthropic's Claude models 3.5 and above, including
    Claude 4 Opus, Claude 4 Sonnet, Claude 3.7 Sonnet, and Claude 3.5 variants.
    """

    # Official Anthropic model names validated against API documentation (3.5+ only)
    VALIDATED_MODELS: Dict[str, Dict[str, Any]] = {
        "claude-opus-4-20250514": {
            "name": "claude-opus-4-20250514",
            "type": "chat",
            "context_length": 200000,
            "input_cost": 15.00,  # per 1M tokens
            "output_cost": 75.00,  # per 1M tokens
            "description": "Claude 4 Opus - Our most capable and intelligent model yet",
            "capabilities": ["text", "vision", "function_calling", "extended_thinking"],
            "version": "4-opus",
            "release_date": datetime(2025, 5, 14),
            "max_output": 32000,
            "training_cutoff": "Mar 2025",
        },
        "claude-sonnet-4-20250514": {
            "name": "claude-sonnet-4-20250514",
            "type": "chat",
            "context_length": 200000,
            "input_cost": 3.00,  # per 1M tokens
            "output_cost": 15.00,  # per 1M tokens
            "description": "Claude 4 Sonnet - High-performance model with exceptional reasoning capabilities",
            "capabilities": ["text", "vision", "function_calling", "extended_thinking"],
            "version": "4-sonnet",
            "release_date": datetime(2025, 5, 14),
            "max_output": 64000,
            "training_cutoff": "Mar 2025",
        },
        "claude-3-7-sonnet-20250219": {
            "name": "claude-3-7-sonnet-20250219",
            "type": "chat",
            "context_length": 200000,
            "input_cost": 3.00,  # per 1M tokens
            "output_cost": 15.00,  # per 1M tokens
            "description": "Claude 3.7 Sonnet - High-performance model with early extended thinking",
            "capabilities": ["text", "vision", "function_calling", "extended_thinking"],
            "version": "3.7-sonnet",
            "release_date": datetime(2025, 2, 19),
            "max_output": 64000,
            "training_cutoff": "Nov 2024",
        },
        "claude-3-5-sonnet-20241022": {
            "name": "claude-3-5-sonnet-20241022",
            "type": "chat",
            "context_length": 200000,
            "input_cost": 3.00,  # per 1M tokens
            "output_cost": 15.00,  # per 1M tokens
            "description": "Claude 3.5 Sonnet v2 - Upgraded version with enhanced capabilities",
            "capabilities": ["text", "vision", "function_calling"],
            "version": "3.5-sonnet-v2",
            "release_date": datetime(2024, 10, 22),
            "max_output": 8192,
            "training_cutoff": "Apr 2024",
        },
        "claude-3-5-sonnet-20240620": {
            "name": "claude-3-5-sonnet-20240620",
            "type": "chat",
            "context_length": 200000,
            "input_cost": 3.00,  # per 1M tokens
            "output_cost": 15.00,  # per 1M tokens
            "description": "Claude 3.5 Sonnet - Original version with high intelligence",
            "capabilities": ["text", "vision", "function_calling"],
            "version": "3.5-sonnet",
            "release_date": datetime(2024, 6, 20),
            "max_output": 8192,
            "training_cutoff": "Apr 2024",
        },
        "claude-3-5-haiku-20241022": {
            "name": "claude-3-5-haiku-20241022",
            "type": "chat",
            "context_length": 200000,
            "input_cost": 0.80,  # per 1M tokens
            "output_cost": 4.00,  # per 1M tokens
            "description": "Claude 3.5 Haiku - Intelligence at blazing speeds",
            "capabilities": ["text", "vision"],
            "version": "3.5-haiku",
            "release_date": datetime(2024, 10, 22),
            "max_output": 8192,
            "training_cutoff": "Jul 2024",
        },
    }

    # Model aliases for convenience (pointing to latest versions)
    MODEL_ALIASES: Dict[str, str] = {
        "claude-opus-4-0": "claude-opus-4-20250514",
        "claude-sonnet-4-0": "claude-sonnet-4-20250514",
        "claude-3-7-sonnet-latest": "claude-3-7-sonnet-20250219",
        "claude-3-5-sonnet-latest": "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-latest": "claude-3-5-haiku-20241022",
    }

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.base_url = kwargs.get("base_url")

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.ANTHROPIC

    @property
    def name(self) -> str:
        return "Anthropic"

    def _resolve_model_alias(self, model_name: str) -> str:
        """Resolve model alias to actual model name."""
        return self.MODEL_ALIASES.get(model_name, model_name)

    async def initialize(self) -> None:
        """Initialize the Anthropic client."""
        if AsyncAnthropic is None:
            raise ProviderError(
                "Anthropic package not installed. Install it with: pip install anthropic",
                provider="Anthropic",
                error_code="PACKAGE_NOT_INSTALLED",
            )

        try:
            self.client = AsyncAnthropic(
                api_key=self.api_key,
                base_url=self.base_url,
            )

            # Test the connection using Claude 3.5 Haiku (fastest model)
            await self._test_connection()
            logger.info("Anthropic provider initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Anthropic provider: {e}")
            raise ProviderError(
                f"Anthropic initialization failed: {e}",
                provider="Anthropic",
                error_code="INIT_FAILED",
            )

    async def cleanup(self) -> None:
        """Cleanup Anthropic client resources."""
        if self.client:
            await self.client.close()
            self.client = None
        logger.info("Anthropic provider cleaned up")

    @monitor_api_calls("anthropic_connection_test")
    async def _test_connection(self) -> None:
        """Test the Anthropic API connection using Claude 3.5 Haiku."""
        if not self.client:
            raise ProviderError(
                "Anthropic client not available for testing",
                provider="Anthropic",
                error_code="CLIENT_NOT_INITIALIZED",
            )

        try:
            # Simple API call to test connection using fastest model
            response = await self.client.messages.create(
                model="claude-3-5-haiku-20241022",
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=1,
            )
            if not response:
                raise ProviderError(
                    "No response from Anthropic API",
                    provider="Anthropic",
                    error_code="NO_RESPONSE",
                )
        except Exception as e:
            raise ProviderError(
                f"Anthropic API connection test failed: {e}",
                provider="Anthropic",
                error_code="CONNECTION_FAILED",
            )

    async def validate_model(self, model_name: str) -> bool:
        """Validate model name against official Anthropic documentation."""
        resolved_model = self._resolve_model_alias(model_name)
        return resolved_model in self.VALIDATED_MODELS

    async def get_available_models(self) -> List[ModelInfo]:
        """Get list of available models from Anthropic (3.5+ only)."""
        models = []

        for model_name, info in self.VALIDATED_MODELS.items():
            model_info = ModelInfo(
                name=info["name"],
                provider=self.provider_type,
                type=info["type"],
                context_length=info["context_length"],
                input_cost=info["input_cost"] / 1_000_000,  # Convert to per-token cost
                output_cost=info["output_cost"] / 1_000_000,
                capabilities=info["capabilities"],
                description=info["description"],
                version=info.get("version"),
                release_date=info.get("release_date"),
            )
            models.append(model_info)

        return models

    async def get_model_info(self, model_name: str) -> ModelInfo:
        """Get detailed information about a specific model."""
        resolved_model = self._resolve_model_alias(model_name)

        if resolved_model in self.VALIDATED_MODELS:
            info = self.VALIDATED_MODELS[resolved_model]
            return ModelInfo(
                name=info["name"],
                provider=self.provider_type,
                type=info["type"],
                context_length=info["context_length"],
                input_cost=info["input_cost"] / 1_000_000,
                output_cost=info["output_cost"] / 1_000_000,
                capabilities=info["capabilities"],
                description=info["description"],
                version=info.get("version"),
                release_date=info.get("release_date"),
            )

        raise ProviderError(
            f"Model {model_name} not found. Available models (3.5+): {list(self.VALIDATED_MODELS.keys())}",
            provider="Anthropic",
            error_code="MODEL_NOT_FOUND",
        )

    async def generate_completion(
        self, model: str, messages: List[Dict[str, Any]], **kwargs
    ) -> Dict[str, Any]:
        """Generate completion using Anthropic's API."""
        if not self.client:
            raise ProviderError(
                "Anthropic client not initialized",
                provider="Anthropic",
                error_code="CLIENT_NOT_INITIALIZED",
            )

        try:
            # Resolve alias and validate model
            resolved_model = self._resolve_model_alias(model)
            if not await self.validate_model(resolved_model):
                raise ProviderError(
                    f"Invalid model: {model} (resolved to: {resolved_model}). Available: {list(self.VALIDATED_MODELS.keys())}",
                    provider="Anthropic",
                    error_code="INVALID_MODEL",
                )

            # Convert messages to Anthropic format if needed
            system = None
            anthropic_messages = []

            for msg in messages:
                if msg["role"] == "system":
                    system = msg["content"]
                else:
                    anthropic_messages.append(
                        {"role": msg["role"], "content": msg["content"]}
                    )

            # Get model info for max_tokens validation
            model_info = self.VALIDATED_MODELS[resolved_model]
            max_output_tokens = model_info.get("max_output", 8192)
            requested_max_tokens = kwargs.get("max_tokens", 4096)

            # Ensure we don't exceed model's max output
            max_tokens = min(requested_max_tokens, max_output_tokens)

            # Prepare parameters
            params = {
                "model": resolved_model,
                "messages": anthropic_messages,
                "max_tokens": max_tokens,
                "temperature": kwargs.get("temperature", 0.1),
                "top_p": kwargs.get("top_p", 1.0),
            }

            if system:
                params["system"] = system

            # Add extended thinking if supported and requested
            if "extended_thinking" in model_info["capabilities"] and kwargs.get(
                "enable_thinking", False
            ):
                params["thinking"] = {
                    "type": "human_readable",
                    "budget_tokens": kwargs.get("thinking_budget", 10000),
                }

            # Make the API call
            start_time = datetime.utcnow()
            response = await self.client.messages.create(**params)
            end_time = datetime.utcnow()

            # Calculate metrics
            execution_time = (end_time - start_time).total_seconds()

            # Extract content
            content = ""
            thinking_content = ""

            for block in response.content:
                if hasattr(block, "text"):
                    content += block.text
                elif hasattr(block, "thinking") and block.thinking:
                    thinking_content += block.thinking

            result = {
                "content": content,
                "role": "assistant",
                "finish_reason": response.stop_reason,
                "usage": {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens
                    + response.usage.output_tokens,
                },
                "model": response.model,
                "execution_time": execution_time,
                "provider": "anthropic",
            }

            # Add thinking content if available
            if thinking_content:
                result["thinking"] = thinking_content

            return result

        except Exception as e:
            logger.error(f"Anthropic completion failed: {e}")
            raise ProviderError(
                f"Completion generation failed: {e}",
                provider="Anthropic",
                error_code="COMPLETION_FAILED",
            )

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on Anthropic provider."""
        if not self.client:
            return {
                "status": "unhealthy",
                "error": "Anthropic client not initialized",
                "last_updated": datetime.utcnow().isoformat(),
            }

        try:
            # Test a simple completion using Claude 3.5 Haiku (fastest)
            test_response = await self.client.messages.create(
                model="claude-3-5-haiku-20241022",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5,
            )

            content = ""
            for block in test_response.content:
                if hasattr(block, "text"):
                    content += block.text

            return {
                "status": "healthy",
                "model_count": len(self.VALIDATED_MODELS),
                "available_models": list(self.VALIDATED_MODELS.keys()),
                "model_aliases": self.MODEL_ALIASES,
                "test_completion": content,
                "minimum_version": "3.5",
                "last_updated": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Anthropic health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_updated": datetime.utcnow().isoformat(),
            }
