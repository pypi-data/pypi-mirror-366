"""
Groq AI Provider for Monkey Coder
Supports Llama, Qwen and Kimi models via Groq API
"""

import os
import asyncio
from typing import Dict, Any, List, Optional, AsyncGenerator
import logging
from datetime import datetime
from groq import AsyncGroq, Groq
from . import BaseProvider
from ..models import ProviderType, ProviderError, ModelInfo

logger = logging.getLogger(__name__)


class GroqProvider(BaseProvider):
    """Groq AI provider for hardware-accelerated model inference."""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        api_key = api_key or os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY is required")
        
        super().__init__(api_key, **kwargs)

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.GROQ

    @property
    def name(self) -> str:
        return "Groq"

    async def initialize(self) -> None:
        """Initialize the Groq client."""
        try:
            self.client = AsyncGroq(api_key=self.api_key)
            self.sync_client = Groq(api_key=self.api_key)

            # Test the connection
            await self._test_connection()
            logger.info("Groq provider initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Groq provider: {e}")
            raise ProviderError(
                f"Groq initialization failed: {e}",
                provider="Groq",
                error_code="INIT_FAILED",
            )

    async def cleanup(self) -> None:
        """Cleanup Groq client resources."""
        self.client = None
        self.sync_client = None
        logger.info("Groq provider cleaned up")

    async def _test_connection(self) -> None:
        """Test the Groq API connection."""
        if not self.client:
            raise ProviderError(
                "Groq client not available for testing",
                provider="Groq",
                error_code="CLIENT_NOT_INITIALIZED",
            )

        try:
            # Simple API call to test connection
            response = await self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=1,
            )
            if not response:
                raise ProviderError(
                    "No response from Groq API",
                    provider="Groq",
                    error_code="NO_RESPONSE",
                )
        except Exception as e:
            raise ProviderError(
                f"Groq API connection test failed: {e}",
                provider="Groq",
                error_code="CONNECTION_FAILED",
            )

    # Groq-available models from Production and Preview lists
    VALIDATED_MODELS: Dict[str, Dict[str, Any]] = {
            # Production Llama models
            "llama-3.1-8b-instant": {
                "name": "llama-3.1-8b-instant",
                "type": "chat",
                "context_length": 131072,
                "max_output_tokens": 131072,
                "input_cost": 0.05,  # per 1M tokens
                "output_cost": 0.08,  # per 1M tokens
                "description": "Llama 3.1 8B - Fast, lightweight model",
                "capabilities": ["text", "streaming"],
                "version": "3.1",
                "release_date": datetime(2024, 7, 1),
            },
            "llama-3.3-70b-versatile": {
                "name": "llama-3.3-70b-versatile",
                "type": "chat",
                "context_length": 131072,
                "max_output_tokens": 32768,
                "input_cost": 0.59,  # per 1M tokens
                "output_cost": 0.79,  # per 1M tokens
                "description": "Llama 3.3 70B - Versatile language model",
                "capabilities": ["text", "streaming"],
                "version": "3.3",
                "release_date": datetime(2024, 9, 1),
            },
            # Preview Llama models
            "meta-llama/llama-4-maverick-17b-128e-instruct": {
                "name": "meta-llama/llama-4-maverick-17b-128e-instruct",
                "type": "chat",
                "context_length": 131072,
                "max_output_tokens": 8192,
                "input_cost": 0.20,  # per 1M tokens (estimate)
                "output_cost": 0.30,  # per 1M tokens (estimate)
                "description": "Llama 4 Maverick 17B Instruct",
                "capabilities": ["text", "streaming"],
                "version": "4-maverick",
                "release_date": datetime(2024, 12, 1),
            },
            "meta-llama/llama-4-scout-17b-16e-instruct": {
                "name": "meta-llama/llama-4-scout-17b-16e-instruct",
                "type": "chat",
                "context_length": 131072,
                "max_output_tokens": 8192,
                "input_cost": 0.20,  # per 1M tokens (estimate)
                "output_cost": 0.30,  # per 1M tokens (estimate)
                "description": "Llama 4 Scout 17B Instruct",
                "capabilities": ["text", "streaming"],
                "version": "4-scout",
                "release_date": datetime(2024, 12, 1),
            },
            # Preview Kimi model
            "moonshotai/kimi-k2-instruct": {
                "name": "moonshotai/kimi-k2-instruct",
                "type": "chat",
                "context_length": 131072,
                "max_output_tokens": 16384,
                "input_cost": 0.80,  # per 1M tokens (estimate)
                "output_cost": 1.20,  # per 1M tokens (estimate)
                "description": "Kimi K2 Instruct - Advanced MoE model",
                "capabilities": ["text", "streaming"],
                "version": "k2",
                "release_date": datetime(2024, 11, 1),
            },
            # Preview Qwen model
            "qwen/qwen3-32b": {
                "name": "qwen/qwen3-32b",
                "type": "chat",
                "context_length": 131072,
                "max_output_tokens": 40960,
                "input_cost": 0.40,  # per 1M tokens (estimate)
                "output_cost": 0.60,  # per 1M tokens (estimate)
                "description": "Qwen 3 32B - Advanced reasoning and multilingual",
                "capabilities": ["text", "streaming"],
                "version": "3",
                "release_date": datetime(2024, 10, 1),
            },
        }

    async def validate_model(self, model_name: str) -> bool:
        """Validate model name against available Groq models."""
        return model_name in self.VALIDATED_MODELS

    async def get_available_models(self) -> List[ModelInfo]:
        """Get list of available models from Groq."""
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
            provider="Groq",
            error_code="MODEL_NOT_FOUND",
        )

    async def generate_completion(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """Generate completion using Groq's API."""
        if not self.client:
            raise ProviderError(
                "Groq client not initialized",
                provider="Groq",
                error_code="CLIENT_NOT_INITIALIZED",
            )

        try:
            # Validate model
            if not await self.validate_model(model):
                raise ProviderError(
                    f"Invalid model: {model}",
                    provider="Groq",
                    error_code="INVALID_MODEL",
                )

            # Make the API call
            start_time = datetime.utcnow()
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 2048),
                stream=False,
                **{k: v for k, v in kwargs.items() if k not in ["temperature", "max_tokens"]}
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
                "provider": "groq",
            }


        except Exception as e:
            logger.error(f"Groq completion failed: {e}")
            raise ProviderError(
                f"Completion generation failed: {e}",
                provider="Groq",
                error_code="COMPLETION_FAILED",
            )

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on Groq provider."""
        if not self.client:
            return {
                "status": "unhealthy",
                "error": "Groq client not initialized",
                "last_updated": datetime.utcnow().isoformat(),
            }

        try:
            # Test a simple completion
            test_response = await self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5,
            )

            return {
                "status": "healthy",
                "model_count": len(self.VALIDATED_MODELS),
                "available_models": list(self.VALIDATED_MODELS.keys()),
                "test_completion": test_response.choices[0].message.content,
                "hardware_accelerated": True,
                "last_updated": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Groq health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_updated": datetime.utcnow().isoformat(),
            }
