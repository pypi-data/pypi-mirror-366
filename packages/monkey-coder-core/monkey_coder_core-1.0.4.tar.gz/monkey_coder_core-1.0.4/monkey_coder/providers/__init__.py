"""
Provider registry for AI provider management.

This module manages different AI providers (OpenAI, Anthropic, Google, Groq)
and their model availability.
"""

import logging
from typing import Dict, List, Any, Optional

from ..models import ProviderType, MODEL_REGISTRY

logger = logging.getLogger(__name__)


class ProviderRegistry:
    """
    Registry for managing AI providers and their capabilities.
    """

    def __init__(self):
        self.providers = {}
        logger.info("ProviderRegistry initialized")

    async def initialize_all(self):
        """Initialize all available providers."""
        logger.info("Initializing all providers...")
        
        # Initialize each provider
        for provider_type in ProviderType:
            self.providers[provider_type] = {
                "status": "active",
                "models": MODEL_REGISTRY.get(provider_type, []),
                "initialized": True
            }
        
        logger.info(f"Initialized {len(self.providers)} providers")

    async def cleanup_all(self):
        """Cleanup all providers."""
        logger.info("Cleaning up all providers...")
        self.providers.clear()
        logger.info("Provider cleanup complete")

    def get_all_providers(self) -> Dict[str, Any]:
        """Get information about all providers."""
        return {
            provider_type.value: {
                "status": info["status"],
                "model_count": len(info["models"]),
                "models": info["models"]
            }
            for provider_type, info in self.providers.items()
        }

    async def get_available_models(self, provider_filter: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Get available models, optionally filtered by provider.
        
        Args:
            provider_filter: Optional provider name to filter by
            
        Returns:
            Dictionary mapping provider names to their available models
        """
        result = {}
        
        for provider_type, info in self.providers.items():
            provider_name = provider_type.value
            
            # Apply filter if specified
            if provider_filter and provider_name != provider_filter:
                continue
                
            result[provider_name] = info["models"]
        
        return result

"""
AI Provider adapters for Monkey Coder Core.

This module provides adapters for different AI providers:
- OpenAI (GPT models)
- Anthropic (Claude models) 
- Google (Gemini models)
- Groq (Hardware-accelerated inference for Llama, Qwen, and Kimi models)
- Grok (xAI's Grok models)

All adapters validate model names against official documentation
to ensure accuracy and compliance.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Type
from contextlib import asynccontextmanager

from ..models import ProviderType, ProviderError, ModelInfo

logger = logging.getLogger(__name__)


class BaseProvider(ABC):
    """
    Abstract base class for AI providers.
    
    All provider adapters must implement this interface to ensure
    consistent behavior across different AI services.
    """
    
    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.config = kwargs
        self.client = None
        self._models_cache = None
        self._last_model_update = None
        
    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """Return the provider type."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider name."""
        pass
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the provider client."""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup provider resources."""
        pass
    
    @abstractmethod
    async def validate_model(self, model_name: str) -> bool:
        """Validate model name against official documentation."""
        pass
    
    @abstractmethod
    async def get_available_models(self) -> List[ModelInfo]:
        """Get list of available models from provider."""
        pass
    
    @abstractmethod
    async def generate_completion(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """Generate completion using the provider's API."""
        pass
    
    @abstractmethod
    async def get_model_info(self, model_name: str) -> ModelInfo:
        """Get detailed information about a specific model."""
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the provider."""
        try:
            # Try to get models list as a basic health check
            models = await self.get_available_models()
            return {
                "status": "healthy",
                "model_count": len(models),
                "last_updated": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Health check failed for {self.name}: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_updated": datetime.utcnow().isoformat(),
            }


class ProviderRegistry:
    """
    Registry for managing AI provider instances.
    
    Handles initialization, validation, and lifecycle management
    of all supported AI providers.
    """
    
    def __init__(self):
        self._providers: Dict[ProviderType, BaseProvider] = {}
        self._initialized = False
    
    async def register_provider(self, provider: BaseProvider) -> None:
        """Register a new provider."""
        try:
            await provider.initialize()
            self._providers[provider.provider_type] = provider
            logger.info(f"Registered provider: {provider.name}")
        except Exception as e:
            logger.error(f"Failed to register provider {provider.name}: {e}")
            raise ProviderError(
                f"Provider registration failed: {e}",
                provider=provider.name,
                error_code="REGISTRATION_FAILED"
            )
    
    async def initialize_all(self) -> None:
        """Initialize all configured providers."""
        from .openai_adapter import OpenAIProvider
        from .anthropic_adapter import AnthropicProvider  
        from .google_adapter import GoogleProvider
        from .groq_provider import GroqProvider
        from .grok_adapter import GrokProvider
        
        # Get API keys from environment
        import os
        
        providers_to_init = []
        
        # OpenAI
        if openai_key := os.getenv("OPENAI_API_KEY"):
            providers_to_init.append(OpenAIProvider(openai_key))
        
        # Anthropic
        if anthropic_key := os.getenv("ANTHROPIC_API_KEY"):
            providers_to_init.append(AnthropicProvider(anthropic_key))
        
        # Google
        if google_key := os.getenv("GOOGLE_API_KEY"):
            providers_to_init.append(GoogleProvider(google_key))
        
        # Groq - Hardware-accelerated inference for Llama, Qwen, and Kimi models
        if groq_key := os.getenv("GROQ_API_KEY"):
            providers_to_init.append(GroqProvider(groq_key))
        
        # Grok (xAI) - Grok models
        if grok_key := os.getenv("GROK_API_KEY"):
            grok_base_url = os.getenv("GROK_BASE_URL", "https://api.x.ai/v1")
            providers_to_init.append(GrokProvider(grok_key, base_url=grok_base_url))
        
        # Initialize providers concurrently
        results = await asyncio.gather(
            *[self.register_provider(provider) for provider in providers_to_init],
            return_exceptions=True
        )
        
        # Log results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(f"Failed to initialize provider {providers_to_init[i].name}: {result}")
        
        self._initialized = True
        logger.info(f"Provider registry initialized with {len(self._providers)} providers")
    
    async def cleanup_all(self) -> None:
        """Cleanup all providers."""
        cleanup_tasks = [
            provider.cleanup() for provider in self._providers.values()
        ]
        
        await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        self._providers.clear()
        self._initialized = False
        logger.info("All providers cleaned up")
    
    def get_provider(self, provider_type: ProviderType) -> Optional[BaseProvider]:
        """Get a specific provider by type."""
        return self._providers.get(provider_type)
    
    def get_all_providers(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all registered providers."""
        return {
            provider_type.value: {
                "name": provider.name,
                "type": provider_type.value,
                "initialized": True,
            }
            for provider_type, provider in self._providers.items()
        }
    
    async def get_available_models(self, provider_filter: Optional[str] = None) -> Dict[str, List[str]]:
        """Get available models from all or filtered providers."""
        if provider_filter:
            try:
                provider_type = ProviderType(provider_filter)
                provider = self.get_provider(provider_type)
                if provider:
                    models = await provider.get_available_models()
                    return {provider_filter: [model.name for model in models]}
                else:
                    return {provider_filter: []}
            except ValueError:
                logger.warning(f"Invalid provider filter: {provider_filter}")
                return {}
        
        # Get models from all providers
        result = {}
        for provider_type, provider in self._providers.items():
            try:
                models = await provider.get_available_models()
                result[provider_type.value] = [model.name for model in models]
            except Exception as e:
                logger.error(f"Failed to get models from {provider.name}: {e}")
                result[provider_type.value] = []
        
        return result
    
    async def validate_model(self, provider: ProviderType, model_name: str) -> bool:
        """Validate a model name against provider documentation."""
        provider_instance = self.get_provider(provider)
        if not provider_instance:
            logger.warning(f"Provider {provider.value} not available")
            return False
        
        try:
            return await provider_instance.validate_model(model_name)
        except Exception as e:
            logger.error(f"Model validation failed for {provider.value}/{model_name}: {e}")
            return False
    
    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """Perform health checks on all providers."""
        results = {}
        
        for provider_type, provider in self._providers.items():
            try:
                health_status = await provider.health_check()
                results[provider_type.value] = health_status
            except Exception as e:
                results[provider_type.value] = {
                    "status": "error",
                    "error": str(e),
                    "last_updated": datetime.utcnow().isoformat(),
                }
        
        return results
    
    @property
    def is_initialized(self) -> bool:
        """Check if the registry is initialized."""
        return self._initialized
    
    @property
    def provider_count(self) -> int:
        """Get the number of registered providers."""
        return len(self._providers)
