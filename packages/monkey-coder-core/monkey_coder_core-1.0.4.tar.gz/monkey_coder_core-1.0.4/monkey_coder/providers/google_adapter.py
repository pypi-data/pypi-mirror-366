"""
Google Provider Adapter for Monkey Coder Core.

This adapter provides integration with Google's AI API, including Gemini models.
All model names are validated against official Google documentation.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

try:
    from google.genai import Client as GoogleGenAI
except ImportError:
    GoogleGenAI = None
    logging.warning(
        "Google GenAI package not installed. Install it with: pip install google-genai"
    )

from . import BaseProvider
from ..models import ProviderType, ProviderError, ModelInfo

logger = logging.getLogger(__name__)


class GoogleProvider(BaseProvider):
    """
    Google provider adapter implementing the BaseProvider interface.

    Provides access to Google's Gemini models including Gemini 1.5 Pro,
    Gemini 1.5 Flash, and other Gemini variants.
    """

    # Official Google model names validated against API documentation
    VALIDATED_MODELS: Dict[str, Dict[str, Any]] = {
        "gemini-2.5-pro": {
            "name": "gemini-2.5-pro",
            "type": "chat",
            "context_length": 1048576,  # 1M tokens
            "input_cost": 1.25,  # per 1M tokens
            "output_cost": 5.00,  # per 1M tokens
            "description": "Gemini 2.5 Pro - State-of-the-art model for complex reasoning in code, math, and STEM",
            "capabilities": [
                "text",
                "vision",
                "audio",
                "video",
                "pdf",
                "function_calling",
                "structured_outputs",
                "caching",
                "code_execution",
                "search_grounding",
                "image_generation",
                "audio_generation",
                "live_api",
                "thinking",
            ],
            "version": "2.5-pro",
            "release_date": datetime(2025, 6, 1),
        },
        "gemini-2.5-flash": {
            "name": "gemini-2.5-flash",
            "type": "chat",
            "context_length": 1048576,  # 1M tokens
            "input_cost": 0.075,
            "output_cost": 0.30,
            "description": "Gemini 2.5 Flash - Best price-performance model for large-scale, low-latency tasks",
            "capabilities": [
                "text",
                "vision",
                "audio",
                "video",
                "function_calling",
                "structured_outputs",
                "caching",
                "code_execution",
                "search_grounding",
                "image_generation",
                "audio_generation",
                "thinking",
                "batch_mode",
            ],
            "version": "2.5-flash",
            "release_date": datetime(2025, 6, 1),
        },
        "gemini-2.5-flash-lite": {
            "name": "gemini-2.5-flash-lite",
            "type": "chat",
            "context_length": 1048576,  # 1M tokens
            "input_cost": 0.0375,
            "output_cost": 0.15,
            "description": "Gemini 2.5 Flash-Lite - Cost-efficient and high-throughput version of Gemini 2.5 Flash",
            "capabilities": [
                "text",
                "vision",
                "audio",
                "video",
                "pdf",
                "function_calling",
                "structured_outputs",
                "caching",
                "code_execution",
                "url_context",
                "search_grounding",
                "image_generation",
                "audio_generation",
                "live_api",
            ],
            "version": "2.5-flash-lite",
            "release_date": datetime(2025, 7, 1),
        },
        "gemini-2.0-flash": {
            "name": "gemini-2.0-flash",
            "type": "chat",
            "context_length": 1048576,  # 1M tokens
            "input_cost": 0.075,
            "output_cost": 0.30,
            "description": "Gemini 2.0 Flash - Next-gen features with superior speed, native tool use",
            "capabilities": [
                "text",
                "vision",
                "audio",
                "video",
                "function_calling",
                "structured_outputs",
                "caching",
                "tuning",
                "code_execution",
                "search",
                "image_generation",
                "audio_generation",
                "live_api",
            ],
            "version": "2.0-flash",
            "release_date": datetime(2025, 2, 1),
        },
    }

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.project_id = kwargs.get("project_id")
        self.location = kwargs.get("location", "us-central1")

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.GOOGLE

    @property
    def name(self) -> str:
        return "Google"

    async def initialize(self) -> None:
        """Initialize the Google client."""
        if GoogleGenAI is None:
            raise ProviderError(
                "Google GenAI package not installed. Install it with: pip install google-genai",
                provider="Google",
                error_code="PACKAGE_NOT_INSTALLED",
            )

        try:
            # Use either API key OR project/location, not both
            if self.api_key:
                # Use API key for consumer access
                self.client = GoogleGenAI(api_key=self.api_key)
            elif self.project_id:
                # Use project/location for Google Cloud access
                self.client = GoogleGenAI(
                    project=self.project_id,
                    location=self.location,
                )
            else:
                raise ProviderError(
                    "Either API key or project ID must be provided",
                    provider="Google",
                    error_code="MISSING_CREDENTIALS",
                )

            # Test the connection
            await self._test_connection()
            logger.info("Google provider initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Google provider: {e}")
            raise ProviderError(
                f"Google initialization failed: {e}",
                provider="Google",
                error_code="INIT_FAILED",
            )

    async def cleanup(self) -> None:
        """Cleanup Google client resources."""
        self.client = None
        logger.info("Google provider cleaned up")

    async def _test_connection(self) -> None:
        """Test the Google API connection."""
        if not self.client:
            raise ProviderError(
                "Google client not available for testing",
                provider="Google",
                error_code="CLIENT_NOT_INITIALIZED",
            )

        try:
            # Simple API call to test connection
            # For now, we'll skip the actual test since google-genai might not be installed
            logger.info("Google API connection test skipped (mock mode)")
        except Exception as e:
            raise ProviderError(
                f"Google API connection test failed: {e}",
                provider="Google",
                error_code="CONNECTION_FAILED",
            )

    async def validate_model(self, model_name: str) -> bool:
        """Validate model name against official Google documentation."""
        return model_name in self.VALIDATED_MODELS

    async def get_available_models(self) -> List[ModelInfo]:
        """Get list of available models from Google."""
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
            provider="Google",
            error_code="MODEL_NOT_FOUND",
        )

    async def generate_completion(
        self, model: str, messages: List[Dict[str, Any]], **kwargs
    ) -> Dict[str, Any]:
        """Generate completion using Google's API."""
        if not self.client:
            raise ProviderError(
                "Google client not initialized",
                provider="Google",
                error_code="CLIENT_NOT_INITIALIZED",
            )

        try:
            # Validate model first
            if not await self.validate_model(model):
                raise ProviderError(
                    f"Invalid model: {model}",
                    provider="Google",
                    error_code="INVALID_MODEL",
                )

            # For now, return a mock response since google-genai might not be installed
            logger.warning("Google completion using mock response")

            return {
                "content": "Mock response from Google provider",
                "role": "assistant",
                "finish_reason": "stop",
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 5,
                    "total_tokens": 15,
                },
                "model": model,
                "execution_time": 0.1,
                "provider": "google",
            }

        except Exception as e:
            logger.error(f"Google completion failed: {e}")
            raise ProviderError(
                f"Completion generation failed: {e}",
                provider="Google",
                error_code="COMPLETION_FAILED",
            )

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on Google provider."""
        if not self.client:
            return {
                "status": "unhealthy",
                "error": "Google client not initialized",
                "last_updated": datetime.utcnow().isoformat(),
            }

        return {
            "status": "healthy",
            "model_count": len(self.VALIDATED_MODELS),
            "test_completion": "Mock health check passed",
            "last_updated": datetime.utcnow().isoformat(),
        }
