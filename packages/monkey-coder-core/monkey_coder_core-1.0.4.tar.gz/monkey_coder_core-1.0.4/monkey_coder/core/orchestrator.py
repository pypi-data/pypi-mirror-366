"""
MultiAgentOrchestrator for monkey1 multi-agent system.

This module orchestrates multiple agents in a collaborative manner
for complex task execution and coordination with enhanced orchestration patterns.
"""

import logging
from typing import Any, Dict, List, Optional

from .orchestration_coordinator import OrchestrationCoordinator, OrchestrationStrategy
from ..models import ExecuteRequest, ExecuteResponse

logger = logging.getLogger(__name__)


class MultiAgentOrchestrator:
    """
    Enhanced multi-agent orchestrator with advanced coordination patterns.
    
    Features:
    - Collaborative agent coordination  
    - Consensus-based decision making
    - Reflection and iteration capabilities
    - Advanced orchestration strategies (sequential, parallel, quantum, hybrid)
    - Intelligent task decomposition and agent handoff
    """

    def __init__(self):
        self.agents = []
        self.coordination_engine = OrchestrationCoordinator()
        logger.info("MultiAgentOrchestrator initialized with enhanced coordination engine")

    async def orchestrate(
        self, 
        request: ExecuteRequest, 
        persona_context: Dict[str, Any],
        strategy_hint: Optional[OrchestrationStrategy] = None
    ) -> ExecuteResponse:
        """
        Orchestrate task execution using advanced coordination patterns.
        
        Args:
            request: The original execution request
            persona_context: Context from persona routing
            strategy_hint: Optional orchestration strategy override
            
        Returns:
            ExecuteResponse with orchestration results
        """
        logger.info(f"Orchestrating task: {request.task_type}")
        
        # Extract persona routing information
        selected_persona = persona_context.get("selected_persona")
        provider = persona_context.get("provider")
        model = persona_context.get("model")
        confidence = persona_context.get("confidence", 0.0)
        
        logger.info(
            f"Orchestrating with persona: {selected_persona.value if selected_persona else 'None'}, "
            f"provider: {provider.value if provider else 'None'}, "
            f"model: {model}, confidence: {confidence:.2f}"
        )
        
        # Determine orchestration strategy based on context
        if not strategy_hint:
            strategy_hint = self._suggest_strategy_from_persona(selected_persona, confidence)
        
        # Execute orchestration using coordination engine
        try:
            response = await self.coordination_engine.coordinate_execution(
                request, strategy_hint
            )
            
            # Enhance response with persona context
            response.superclause_routing = persona_context
            
            # Add orchestration metadata
            if not response.monkey1_orchestration:
                response.monkey1_orchestration = {}
            
            response.monkey1_orchestration.update({
                "persona_influence": {
                    "selected_persona": selected_persona.value if selected_persona else None,
                    "confidence": confidence,
                    "strategy_suggested": strategy_hint.value if strategy_hint else None
                },
                "orchestrator_version": "enhanced_v1.0"
            })
            
            logger.info(f"Enhanced orchestration completed: {response.status}")
            return response
            
        except Exception as e:
            logger.exception(f"Orchestration failed: {e}")
            raise
    
    def _suggest_strategy_from_persona(
        self, 
        persona, 
        confidence: float
    ) -> Optional[OrchestrationStrategy]:
        """Suggest orchestration strategy based on persona and confidence."""
        
        if not persona:
            return None
        
        # Map persona types to preferred strategies
        persona_strategy_map = {
            "developer": OrchestrationStrategy.SEQUENTIAL,
            "reviewer": OrchestrationStrategy.PARALLEL,
            "architect": OrchestrationStrategy.QUANTUM,
            "tester": OrchestrationStrategy.HYBRID
        }
        
        base_strategy = persona_strategy_map.get(
            persona.value, 
            OrchestrationStrategy.SIMPLE
        )
        
        # Adjust based on confidence
        if confidence < 0.6:
            # Low confidence - use simpler strategy
            if base_strategy in [OrchestrationStrategy.QUANTUM, OrchestrationStrategy.HYBRID]:
                return OrchestrationStrategy.SEQUENTIAL
            elif base_strategy == OrchestrationStrategy.PARALLEL:
                return OrchestrationStrategy.SEQUENTIAL
        elif confidence > 0.9:
            # High confidence - can use more complex strategy
            if base_strategy == OrchestrationStrategy.SIMPLE:
                return OrchestrationStrategy.SEQUENTIAL
            elif base_strategy == OrchestrationStrategy.SEQUENTIAL:
                return OrchestrationStrategy.PARALLEL
        
        return base_strategy
    
    def get_orchestration_capabilities(self) -> Dict[str, Any]:
        """Get information about orchestration capabilities."""
        return {
            "strategies": [strategy.value for strategy in OrchestrationStrategy],
            "persona_mappings": {
                "developer": "sequential",
                "reviewer": "parallel", 
                "architect": "quantum",
                "tester": "hybrid"
            },
            "features": [
                "adaptive_strategy_selection",
                "persona_aware_orchestration",
                "confidence_based_adjustment",
                "multi_phase_execution",
                "intelligent_agent_handoff"
            ],
            "active_orchestrations": len(self.coordination_engine.active_orchestrations)
        }
    
    def get_active_orchestrations(self) -> List[Dict[str, Any]]:
        """Get list of active orchestrations."""
        return self.coordination_engine.get_active_orchestrations()
