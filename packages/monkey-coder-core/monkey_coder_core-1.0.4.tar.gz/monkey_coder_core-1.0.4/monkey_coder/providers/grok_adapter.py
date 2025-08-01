"""
Grok (xAI) Provider Adapter for Monkey Coder Core.

This adapter provides integration with xAI's Grok API.
All model names are validated against official xAI documentation.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

try:
    from openai import AsyncOpenAI  # xAI uses OpenAI-compatible API
except ImportError:
    AsyncOpenAI = None
    logging.warning(
        "OpenAI package not installed. Install it with: pip install openai"
    )

from . import BaseProvider
from ..models import ProviderType, ProviderError, ModelInfo

logger = logging.getLogger(__name__)


class GrokProvider(BaseProvider):
    """
    Grok (xAI) provider adapter implementing the BaseProvider interface.

    Provides access to xAI's Grok models including Grok-3 and Grok-4 variants.
    """

    # Official xAI Grok model names
    VALIDATED_MODELS: Dict[str, Dict[str, Any]] = {
        "grok-4-latest": {
            "name": "grok-4-latest",
            "type": "chat",
            "context_length": 131072,
            "input_cost": 5.00,  # per 1M tokens (estimate)
            "output_cost": 15.00,  # per 1M tokens (estimate)
            "description": "Grok-4 Latest - xAI's most advanced reasoning model",
            "capabilities": ["text", "reasoning", "analysis", "conversation"],
            "version": "4-latest",
            "release_date": datetime(2025, 1, 1),
        },
        "grok-3": {
            "name": "grok-3",
            "type": "chat",
            "context_length": 100000,
            "input_cost": 2.00,  # per 1M tokens (estimate)
            "output_cost": 8.00,  # per 1M tokens (estimate)
            "description": "Grok-3 - Advanced model with strong reasoning capabilities",
            "capabilities": ["text", "reasoning", "conversation"],
            "version": "3",
            "release_date": datetime(2024, 11, 1),
        },
        "grok-3-mini": {
            "name": "grok-3-mini",
            "type": "chat",
            "context_length": 32768,
            "input_cost": 0.25,  # per 1M tokens (estimate)
            "output_cost": 1.00,  # per 1M tokens (estimate)
            "description": "Grok-3 Mini - Efficient model for everyday tasks",
            "capabilities": ["text", "conversation"],
            "version": "3-mini",
            "release_date": datetime(2024, 11, 1),
        },
        "grok-3-mini-fast": {
            "name": "grok-3-mini-fast",
            "type": "chat",
            "context_length": 16384,
            "input_cost": 0.10,  # per 1M tokens (estimate)
            "output_cost": 0.40,  # per 1M tokens (estimate)
            "description": "Grok-3 Mini Fast - Ultra-fast responses for simple tasks",
            "capabilities": ["text", "conversation", "streaming"],
            "version": "3-mini-fast",
            "release_date": datetime(2024, 12, 1),
        },
        "grok-3-fast": {
            "name": "grok-3-fast",
            "type": "chat",
            "context_length": 65536,
            "input_cost": 1.00,  # per 1M tokens (estimate)
            "output_cost": 4.00,  # per 1M tokens (estimate)
            "description": "Grok-3 Fast - Balance of speed and capability",
            "capabilities": ["text", "conversation", "streaming"],
            "version": "3-fast",
            "release_date": datetime(2024, 12, 1),
        },
    }

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.base_url = kwargs.get("base_url", "https://api.x.ai/v1")

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.GROK

    @property
    def name(self) -> str:
        return "Grok (xAI)"

    async def initialize(self) -> None:
        """Initialize the Grok client using OpenAI-compatible API."""
        if AsyncOpenAI is None:
            raise ProviderError(
                "OpenAI package not installed. Install it with: pip install openai",
                provider="Grok",
                error_code="PACKAGE_NOT_INSTALLED",
            )

        try:
            # xAI uses OpenAI-compatible endpoint
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )

            # Test the connection
            await self._test_connection()
            logger.info("Grok provider initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Grok provider: {e}")
            raise ProviderError(
                f"Grok initialization failed: {e}",
                provider="Grok",
                error_code="INIT_FAILED",
            )

    async def cleanup(self) -> None:
        """Cleanup Grok client resources."""
        if self.client:
            await self.client.close()
            self.client = None
        logger.info("Grok provider cleaned up")

    async def _test_connection(self) -> None:
        """Test the Grok API connection."""
        if not self.client:
            raise ProviderError(
                "Grok client not available for testing",
                provider="Grok",
                error_code="CLIENT_NOT_INITIALIZED",
            )

        try:
            # Simple API call to test connection
            response = await self.client.chat.completions.create(
                model="grok-3-mini-fast",
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=1,
            )
            if not response:
                raise ProviderError(
                    "No response from Grok API",
                    provider="Grok",
                    error_code="NO_RESPONSE",
                )
        except Exception as e:
            raise ProviderError(
                f"Grok API connection test failed: {e}",
                provider="Grok",
                error_code="CONNECTION_FAILED",
            )

    async def validate_model(self, model_name: str) -> bool:
        """Validate model name against official Grok documentation."""
        return model_name in self.VALIDATED_MODELS

    async def get_available_models(self) -> List[ModelInfo]:
        """Get list of available models from Grok."""
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
        if model_name in self.VALIDATED_MODELS:
            info = self.VALIDATED_MODELS[model_name]
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
            f"Model {model_name} not found",
            provider="Grok",
            error_code="MODEL_NOT_FOUND",
        )

    async def generate_completion(
        self, model: str, messages: List[Dict[str, Any]], **kwargs
    ) -> Dict[str, Any]:
        """Generate completion using Grok's OpenAI-compatible API."""
        if not self.client:
            raise ProviderError(
                "Grok client not initialized",
                provider="Grok",
                error_code="CLIENT_NOT_INITIALIZED",
            )

        try:
            # Validate model
            if not await self.validate_model(model):
                raise ProviderError(
                    f"Invalid model: {model}",
                    provider="Grok",
                    error_code="INVALID_MODEL",
                )

            # Make the API call
            start_time = datetime.utcnow()
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 2048),
                **kwargs,
            )
            end_time = datetime.utcnow()

            # Calculate metrics
            usage = response.usage
            execution_time = (end_time - start_time).total_seconds()

            return {
                "content": response.choices[0].message.content,
                "role": "assistant",
                "finish_reason": response.choices[0].finish_reason,
                "usage": {
                    "prompt_tokens": usage.prompt_tokens if usage else 0,
                    "completion_tokens": usage.completion_tokens if usage else 0,
                    "total_tokens": usage.total_tokens if usage else 0,
                },
                "model": response.model,
                "execution_time": execution_time,
                "provider": "grok",
            }

        except Exception as e:
            logger.error(f"Grok completion failed: {e}")
            raise ProviderError(
                f"Completion generation failed: {e}",
                provider="Grok",
                error_code="COMPLETION_FAILED",
            )

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on Grok provider."""
        if not self.client:
            return {
                "status": "unhealthy",
                "error": "Grok client not initialized",
                "last_updated": datetime.utcnow().isoformat(),
            }

        try:
            # Test a simple completion
            test_response = await self.client.chat.completions.create(
                model="grok-3-mini-fast",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5,
            )

            return {
                "status": "healthy",
                "model_count": len(self.VALIDATED_MODELS),
                "available_models": list(self.VALIDATED_MODELS.keys()),
                "test_completion": test_response.choices[0].message.content,
                "api_type": "OpenAI-compatible",
                "provider": "xAI",
                "last_updated": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Grok health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_updated": datetime.utcnow().isoformat(),
            }
