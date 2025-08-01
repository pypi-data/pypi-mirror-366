"""
PersonaRouter module for SuperClaude slash-command & persona integration.

This module provides the interface between the main application and the 
AdvancedRouter system, focusing on persona-based routing decisions with
enhanced validation for edge cases.
"""

import logging
from typing import Dict, Any, Optional

from .routing import AdvancedRouter, RoutingDecision
from .persona_validation import PersonaValidator, ValidationResult
from ..models import ExecuteRequest, PersonaType

logger = logging.getLogger(__name__)


class PersonaRouter:
    """
    Persona-focused router interface for SuperClaude integration.
    
    This class wraps the AdvancedRouter to provide persona-specific 
    routing functionality with SuperClaude slash-command support and
    enhanced validation for edge cases like single-word inputs.
    """
    
    def __init__(self):
        self.advanced_router = AdvancedRouter()
        self.persona_validator = PersonaValidator()
        logger.info("PersonaRouter initialized with AdvancedRouter and PersonaValidator")
    
    async def route_request(self, request: ExecuteRequest, context_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Route request through advanced routing system with enhanced validation.
        
        Args:
            request: The execution request to route
            context_hint: Optional context hint for validation enhancement
            
        Returns:
            Dictionary containing persona context and routing information
        """
        logger.info(f"Routing request through persona system: {request.task_type}")
        
        # Enhanced validation and prompt enhancement for edge cases
        validation_result = self.persona_validator.validate_and_enhance(request, context_hint)
        
        # If prompt was enhanced, create a modified request for routing
        if validation_result.enrichment_applied:
            logger.info(
                f"Prompt enhanced from {validation_result.original_length} to "
                f"{validation_result.enhanced_length} characters"
            )
            
            # Create enhanced request copy
            enhanced_request = request.copy()
            enhanced_request.prompt = validation_result.enhanced_prompt
            routing_request = enhanced_request
        else:
            routing_request = request
        
        # Use AdvancedRouter for sophisticated routing decision
        routing_decision = self.advanced_router.route_request(routing_request)
        
        # Override persona suggestion if validation provided a better match
        if validation_result.suggested_persona and validation_result.confidence_score > routing_decision.confidence:
            logger.info(
                f"Using validation-suggested persona: {validation_result.suggested_persona.value} "
                f"(confidence: {validation_result.confidence_score:.2f})"
            )
            final_persona = validation_result.suggested_persona
        else:
            final_persona = routing_decision.persona
        
        # Create persona context for downstream systems
        persona_context = {
            "selected_persona": final_persona,
            "provider": routing_decision.provider,
            "model": routing_decision.model,
            "confidence": max(routing_decision.confidence, validation_result.confidence_score),
            "reasoning": routing_decision.reasoning,
            "complexity_analysis": {
                "complexity_score": routing_decision.complexity_score,
                "context_score": routing_decision.context_score,
                "capability_score": routing_decision.capability_score,
            },
            "routing_metadata": routing_decision.metadata,
            
            # Enhanced validation metadata
            "validation_result": {
                "original_prompt": request.prompt,
                "enhanced_prompt": validation_result.enhanced_prompt,
                "enrichment_applied": validation_result.enrichment_applied,
                "validation_warnings": validation_result.validation_warnings,
                "validation_confidence": validation_result.confidence_score
            }
        }
        
        logger.info(
            f"Persona routing complete: {final_persona.value} "
            f"via {routing_decision.provider.value}/{routing_decision.model}"
        )
        
        return persona_context
    
    def get_available_personas(self) -> Dict[str, Any]:
        """Get information about available personas."""
        return {
            "personas": [persona.value for persona in PersonaType],
            "slash_commands": self.advanced_router.slash_commands,
            "persona_mappings": self.advanced_router.persona_mappings,
        }
    
    def get_routing_debug_info(self, request: ExecuteRequest) -> Dict[str, Any]:
        """Get detailed debug information for routing decision."""
        return self.advanced_router.get_routing_debug_info(request)
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get persona validation statistics and capabilities."""
        return self.persona_validator.get_validation_stats()
