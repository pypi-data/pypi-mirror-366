"""
Model Validator - Ensures only approved models are used
Prevents reversion to legacy or deprecated models
"""

import logging
from typing import List, Dict, Optional, Set, Any
from enum import Enum

logger = logging.getLogger(__name__)


class ModelStatus(Enum):
    """Model approval status"""
    APPROVED = "approved"
    DEPRECATED = "deprecated"
    BLOCKED = "blocked"
    LEGACY = "legacy"


class ModelValidator:
    """
    Validates model names against approved list from ai-models-api-docs
    Prevents use of deprecated or legacy models
    """
    
    # Strictly blocked models that should never be used
    BLOCKED_MODELS = {
        "gpt-4o",  # Use gpt-4.1 instead
        "gpt-4o-mini",  # Use gpt-4.1-mini instead
        "gpt-4",  # Use gpt-4.1 instead
        "gpt-4-turbo",  # Use gpt-4.1 instead
        "claude-3-opus",  # Use claude-opus-4-20250514 instead
        "claude-3-sonnet",  # Use claude-sonnet-4-20250514 instead
    }
    
    # Approved flagship models
    FLAGSHIP_MODELS = {
        "gpt-4.1",  # OpenAI flagship
        "claude-opus-4-20250514",  # Anthropic flagship
        "gemini-2.5-pro",  # Google flagship
        "grok-4-latest",  # xAI flagship
    }
    
    # Model replacement mapping
    MODEL_REPLACEMENTS = {
        # OpenAI replacements
        "gpt-4o": "gpt-4.1",
        "gpt-4o-mini": "gpt-4.1-mini",
        "gpt-4o-nano": "gpt-4.1-nano",
        "gpt-4": "gpt-4.1",
        "gpt-4-turbo": "gpt-4.1",
        "gpt-4-32k": "gpt-4.1",
        
        # Anthropic replacements
        "claude-3-opus": "claude-opus-4-20250514",
        "claude-3-sonnet": "claude-sonnet-4-20250514",
        "claude-3.5-sonnet": "claude-3-5-sonnet-20241022",
        "claude-3-haiku": "claude-3-5-haiku-20241022",
        
        # Google replacements
        "gemini-1.5-pro": "gemini-2.5-pro",
        "gemini-1.5-flash": "models/gemini-2.5-flash",
        "gemini-pro": "gemini-2.5-pro",
        "gemini-pro-vision": "gemini-2.5-pro",
        
        # Grok replacements
        "grok-2": "grok-3",
        "grok-1": "grok-3-mini",
    }
    
    @classmethod
    def validate_model(cls, model_name: str) -> tuple[bool, str, Optional[str]]:
        """
        Validate a model name and suggest replacement if needed
        
        Args:
            model_name: The model name to validate
            
        Returns:
            Tuple of (is_valid, status_message, replacement_model)
        """
        # Check if model is explicitly blocked
        if model_name in cls.BLOCKED_MODELS:
            replacement = cls.MODEL_REPLACEMENTS.get(model_name)
            return (
                False,
                f"Model '{model_name}' is deprecated and blocked.",
                replacement
            )
        
        # Check if model needs replacement
        if model_name in cls.MODEL_REPLACEMENTS:
            replacement = cls.MODEL_REPLACEMENTS[model_name]
            logger.warning(
                f"Model '{model_name}' is legacy. Automatically using '{replacement}' instead."
            )
            return (
                True,  # Allow but with replacement
                f"Legacy model replaced: {model_name} → {replacement}",
                replacement
            )
        
        # Model is approved
        return (
            True,
            f"Model '{model_name}' is approved.",
            None
        )
    
    @classmethod
    def get_safe_model(cls, requested_model: str) -> str:
        """
        Get a safe, approved model name
        
        Args:
            requested_model: The requested model name
            
        Returns:
            Safe model name to use
        """
        is_valid, message, replacement = cls.validate_model(requested_model)
        
        if replacement:
            logger.info(f"Model replacement: {requested_model} → {replacement}")
            return replacement
        
        if not is_valid:
            # Return default flagship model if blocked
            default = "gpt-4.1"
            logger.error(
                f"Blocked model '{requested_model}' requested. Using default '{default}'"
            )
            return default
        
        return requested_model
    
    @classmethod
    def validate_model_list(cls, models: List[str]) -> Dict[str, str]:
        """
        Validate a list of models and return mapping of replacements
        
        Args:
            models: List of model names to validate
            
        Returns:
            Dictionary mapping original to safe model names
        """
        result = {}
        for model in models:
            safe_model = cls.get_safe_model(model)
            result[model] = safe_model
            
        return result
    
    @classmethod
    def is_flagship_model(cls, model_name: str) -> bool:
        """Check if model is a flagship model"""
        return model_name in cls.FLAGSHIP_MODELS
    
    @classmethod
    def get_model_info(cls, model_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a model
        
        Args:
            model_name: The model name
            
        Returns:
            Dictionary with model information
        """
        is_valid, message, replacement = cls.validate_model(model_name)
        
        return {
            "model": model_name,
            "is_valid": is_valid,
            "status": ModelStatus.APPROVED.value if is_valid and not replacement else ModelStatus.LEGACY.value,
            "message": message,
            "replacement": replacement,
            "is_flagship": cls.is_flagship_model(model_name),
            "documentation": "https://ai1docs.abacusai.app/"
        }


def enforce_model_compliance(func):
    """
    Decorator to enforce model compliance on functions that accept model parameters
    """
    def wrapper(*args, **kwargs):
        # Check for 'model' parameter
        if 'model' in kwargs:
            original_model = kwargs['model']
            safe_model = ModelValidator.get_safe_model(original_model)
            if safe_model != original_model:
                logger.warning(
                    f"Model compliance enforced: {original_model} → {safe_model}"
                )
            kwargs['model'] = safe_model
        
        # Check for 'models' parameter (list)
        if 'models' in kwargs and isinstance(kwargs['models'], list):
            original_models = kwargs['models']
            mapping = ModelValidator.validate_model_list(original_models)
            kwargs['models'] = list(mapping.values())
            if any(k != v for k, v in mapping.items()):
                logger.warning(f"Model compliance enforced on list: {mapping}")
        
        return func(*args, **kwargs)
    
    return wrapper


# Validation functions for use in the codebase
def assert_approved_model(model_name: str):
    """
    Assert that a model is approved for use
    Raises ValueError if model is blocked
    """
    is_valid, message, replacement = ModelValidator.validate_model(model_name)
    
    if not is_valid and not replacement:
        raise ValueError(f"Model '{model_name}' is blocked and cannot be used. {message}")
    

def get_approved_models() -> Set[str]:
    """Get set of all approved models"""
    from ..models import MODEL_REGISTRY
    
    approved = set()
    for provider_models in MODEL_REGISTRY.values():
        approved.update(provider_models)
    
    return approved


def validate_config_models(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and fix models in a configuration dictionary
    
    Args:
        config: Configuration dictionary that may contain model references
        
    Returns:
        Updated configuration with validated models
    """
    import copy
    updated_config = copy.deepcopy(config)
    
    def recursive_validate(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in ['model', 'model_name', 'default_model', 'preferred_model']:
                    if isinstance(value, str):
                        safe_model = ModelValidator.get_safe_model(value)
                        if safe_model != value:
                            logger.info(f"Config validation: {path}.{key}: {value} → {safe_model}")
                            obj[key] = safe_model
                elif key in ['models', 'model_list', 'available_models']:
                    if isinstance(value, list):
                        mapping = ModelValidator.validate_model_list(value)
                        obj[key] = list(mapping.values())
                        if any(k != v for k, v in mapping.items()):
                            logger.info(f"Config validation: {path}.{key}: {mapping}")
                else:
                    recursive_validate(value, f"{path}.{key}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                recursive_validate(item, f"{path}[{i}]")
    
    recursive_validate(updated_config)
    return updated_config
