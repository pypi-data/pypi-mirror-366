"""
Enhanced Orchestration Coordinator

Implements advanced orchestration patterns from reference projects monkey1 and Gary8D
for improved task coordination, agent handoff, and execution strategies.
"""

import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple, Union
from uuid import uuid4

from ..models import ExecuteRequest, ExecuteResponse, TaskStatus, ExecutionResult
from ..config.env_config import get_config

logger = logging.getLogger(__name__)


class OrchestrationStrategy(Enum):
    """Orchestration strategies for different task types."""

    SIMPLE = "simple"           # Single agent execution
    SEQUENTIAL = "sequential"   # Sequential agent handoff
    PARALLEL = "parallel"       # Parallel agent execution
    QUANTUM = "quantum"         # Quantum-inspired execution
    HYBRID = "hybrid"          # Combination approach


class OrchestrationPhase(Enum):
    """Phases of orchestration execution."""

    PLANNING = "planning"
    PREPARATION = "preparation"
    EXECUTION = "execution"
    COORDINATION = "coordination"
    VALIDATION = "validation"
    COMPLETION = "completion"


class TaskContext:
    """Enhanced task context with orchestration metadata."""

    def __init__(
        self,
        request: ExecuteRequest,
        strategy: OrchestrationStrategy = OrchestrationStrategy.SIMPLE
    ):
        self.request = request
        self.strategy = strategy
        self.orchestration_id = f"orch_{uuid4().hex[:12]}"
        self.created_at = datetime.utcnow()
        self.phase = OrchestrationPhase.PLANNING
        self.agent_assignments = {}
        self.execution_history = []
        self.shared_context = {}
        self.metadata = {}

        logger.info(f"TaskContext created: {self.orchestration_id} with strategy {strategy.value}")

    def add_execution_event(self, event: Dict[str, Any]):
        """Add event to execution history."""
        event["timestamp"] = datetime.utcnow().isoformat()
        event["phase"] = self.phase.value
        self.execution_history.append(event)

    def update_shared_context(self, key: str, value: Any, agent_id: str = "system"):
        """Update shared context with source tracking."""
        self.shared_context[key] = {
            "value": value,
            "source": agent_id,
            "updated_at": datetime.utcnow().isoformat()
        }

    def get_context_summary(self) -> Dict[str, Any]:
        """Get context summary for logging."""
        return {
            "orchestration_id": self.orchestration_id,
            "strategy": self.strategy.value,
            "phase": self.phase.value,
            "task_type": self.request.task_type.value,
            "agents_assigned": len(self.agent_assignments),
            "execution_events": len(self.execution_history),
            "shared_context_keys": list(self.shared_context.keys())
        }


class OrchestrationCoordinator:
    """
    Enhanced orchestration coordinator with advanced patterns from reference projects.

    Implements multi-agent coordination, intelligent task decomposition,
    and sophisticated execution strategies.
    """

    def __init__(self):
        self.active_orchestrations = {}
        self.orchestration_templates = self._init_orchestration_templates()
        self.strategy_selectors = self._init_strategy_selectors()
        self.config = get_config()

        logger.info("OrchestrationCoordinator initialized with enhanced patterns")

    def _init_orchestration_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize orchestration templates for different task patterns."""
        return {
            "code_generation": {
                "strategy": OrchestrationStrategy.SEQUENTIAL,
                "phases": [
                    {"name": "analysis", "agent_types": ["reviewer"], "parallel": False},
                    {"name": "planning", "agent_types": ["architect"], "parallel": False},
                    {"name": "implementation", "agent_types": ["developer"], "parallel": False},
                    {"name": "testing", "agent_types": ["tester"], "parallel": True}
                ],
                "handoff_criteria": {
                    "analysis_to_planning": ["code_understanding", "requirements_clear"],
                    "planning_to_implementation": ["architecture_defined", "design_approved"],
                    "implementation_to_testing": ["code_complete", "documentation_ready"]
                }
            },

            "code_analysis": {
                "strategy": OrchestrationStrategy.PARALLEL,
                "phases": [
                    {"name": "static_analysis", "agent_types": ["reviewer"], "parallel": True},
                    {"name": "security_scan", "agent_types": ["reviewer"], "parallel": True},
                    {"name": "performance_analysis", "agent_types": ["architect"], "parallel": True},
                    {"name": "synthesis", "agent_types": ["reviewer"], "parallel": False}
                ],
                "handoff_criteria": {
                    "analysis_to_synthesis": ["all_analyses_complete", "findings_available"]
                }
            },

            "testing": {
                "strategy": OrchestrationStrategy.HYBRID,
                "phases": [
                    {"name": "test_planning", "agent_types": ["tester"], "parallel": False},
                    {"name": "unit_testing", "agent_types": ["tester"], "parallel": True},
                    {"name": "integration_testing", "agent_types": ["tester"], "parallel": True},
                    {"name": "validation", "agent_types": ["reviewer"], "parallel": False}
                ],
                "handoff_criteria": {
                    "planning_to_execution": ["test_plan_complete", "resources_available"],
                    "execution_to_validation": ["tests_complete", "results_available"]
                }
            },

            "custom": {
                "strategy": OrchestrationStrategy.QUANTUM,
                "phases": [
                    {"name": "discovery", "agent_types": ["reviewer", "architect"], "parallel": True},
                    {"name": "planning", "agent_types": ["architect"], "parallel": False},
                    {"name": "execution", "agent_types": ["developer", "tester"], "parallel": True},
                    {"name": "review", "agent_types": ["reviewer"], "parallel": False}
                ],
                "handoff_criteria": {
                    "discovery_to_planning": ["requirements_clear", "scope_defined"],
                    "planning_to_execution": ["plan_approved", "resources_allocated"],
                    "execution_to_review": ["deliverables_ready", "criteria_met"]
                }
            }
        }

    def _init_strategy_selectors(self) -> Dict[str, Any]:
        """Initialize strategy selection criteria."""
        return {
            "complexity_thresholds": {
                "simple": 0.3,      # Single agent sufficient
                "sequential": 0.6,   # Sequential coordination needed
                "parallel": 0.7,     # Parallel execution beneficial
                "quantum": 0.8,      # Complex quantum approach needed
                "hybrid": 0.9        # Hybrid approach required
            },

            "task_type_preferences": {
                "code_generation": OrchestrationStrategy.SEQUENTIAL,
                "code_analysis": OrchestrationStrategy.PARALLEL,
                "testing": OrchestrationStrategy.HYBRID,
                "custom": OrchestrationStrategy.QUANTUM
            },

            "resource_considerations": {
                "high_concurrency": OrchestrationStrategy.PARALLEL,
                "limited_resources": OrchestrationStrategy.SEQUENTIAL,
                "complex_dependencies": OrchestrationStrategy.QUANTUM,
                "time_critical": OrchestrationStrategy.HYBRID
            }
        }

    async def coordinate_execution(
        self,
        request: ExecuteRequest,
        strategy_hint: Optional[OrchestrationStrategy] = None
    ) -> ExecuteResponse:
        """
        Coordinate task execution using appropriate orchestration strategy.

        Args:
            request: The execution request
            strategy_hint: Optional strategy override

        Returns:
            ExecuteResponse with orchestration results
        """
        # Determine orchestration strategy
        strategy = strategy_hint or self._select_strategy(request)

        # Create task context
        context = TaskContext(request, strategy)
        self.active_orchestrations[context.orchestration_id] = context

        try:
            logger.info(f"Starting orchestrated execution: {context.orchestration_id}")

            # Execute orchestration based on strategy
            if strategy == OrchestrationStrategy.SIMPLE:
                result = await self._execute_simple_strategy(context)
            elif strategy == OrchestrationStrategy.SEQUENTIAL:
                result = await self._execute_sequential_strategy(context)
            elif strategy == OrchestrationStrategy.PARALLEL:
                result = await self._execute_parallel_strategy(context)
            elif strategy == OrchestrationStrategy.QUANTUM:
                result = await self._execute_quantum_strategy(context)
            elif strategy == OrchestrationStrategy.HYBRID:
                result = await self._execute_hybrid_strategy(context)
            else:
                raise ValueError(f"Unknown orchestration strategy: {strategy}")

            # Create successful response
            response = ExecuteResponse(
                execution_id=context.orchestration_id,
                task_id=request.task_id,
                status=TaskStatus.COMPLETED,
                result=result,
                error=None,
                completed_at=datetime.utcnow(),
                usage=None,  # Will be populated by actual execution
                execution_time=None,  # Will be populated by actual execution
                superclause_routing=context.shared_context.get("persona_routing", {}),
                monkey1_orchestration=context.get_context_summary(),
                gary8d_execution=context.metadata
            )

            logger.info(f"Orchestration completed successfully: {context.orchestration_id}")
            return response

        except Exception as e:
            logger.exception(f"Orchestration failed: {context.orchestration_id}")

            # Create error response
            return ExecuteResponse(
                execution_id=context.orchestration_id,
                task_id=request.task_id,
                status=TaskStatus.FAILED,
                result=None,
                error=str(e),
                completed_at=datetime.utcnow(),
                usage=None,  # No usage for failed execution
                execution_time=None,  # Will be populated by actual execution
                superclause_routing={},  # Empty for error case
                monkey1_orchestration=context.get_context_summary(),
                gary8d_execution={}  # Empty for error case
            )

        finally:
            # Cleanup orchestration context
            if context.orchestration_id in self.active_orchestrations:
                del self.active_orchestrations[context.orchestration_id]

    def _select_strategy(self, request: ExecuteRequest) -> OrchestrationStrategy:
        """Select appropriate orchestration strategy for request."""

        # Get base strategy from task type
        base_strategy = self.strategy_selectors["task_type_preferences"].get(
            request.task_type.value,
            OrchestrationStrategy.SIMPLE
        )

        # Calculate complexity score
        complexity_score = self._calculate_complexity_score(request)

        # Adjust strategy based on complexity
        thresholds = self.strategy_selectors["complexity_thresholds"]

        if complexity_score >= thresholds["hybrid"]:
            strategy = OrchestrationStrategy.HYBRID
        elif complexity_score >= thresholds["quantum"]:
            strategy = OrchestrationStrategy.QUANTUM
        elif complexity_score >= thresholds["parallel"]:
            strategy = OrchestrationStrategy.PARALLEL
        elif complexity_score >= thresholds["sequential"]:
            strategy = OrchestrationStrategy.SEQUENTIAL
        else:
            strategy = OrchestrationStrategy.SIMPLE

        # Consider resource constraints
        if self.config.environment == "development":
            # Prefer simpler strategies in development
            if strategy in [OrchestrationStrategy.QUANTUM, OrchestrationStrategy.HYBRID]:
                strategy = OrchestrationStrategy.SEQUENTIAL

        logger.info(
            f"Selected orchestration strategy: {strategy.value} "
            f"(complexity: {complexity_score:.2f}, base: {base_strategy.value})"
        )

        return strategy

    def _calculate_complexity_score(self, request: ExecuteRequest) -> float:
        """Calculate complexity score for strategy selection."""
        score = 0.0

        # Prompt complexity
        prompt_length = len(request.prompt)
        score += min(prompt_length / 1000, 0.3)  # Max 0.3 for prompt length

        # File complexity
        if request.files:
            file_count = len(request.files)
            score += min(file_count / 10, 0.2)  # Max 0.2 for file count

        # Configuration complexity
        config_sections = [
            request.superclaude_config,
            request.monkey1_config,
            request.gary8d_config
        ]

        active_configs = sum(1 for config in config_sections if config is not None)
        score += active_configs * 0.15  # Max 0.45 for all configs

        # Provider preferences complexity
        if request.preferred_providers:
            score += min(len(request.preferred_providers) / 5, 0.1)

        # Model preferences complexity
        if request.model_preferences:
            score += min(len(request.model_preferences) / 3, 0.1)

        return min(score, 1.0)  # Cap at 1.0

    async def _execute_simple_strategy(self, context: TaskContext) -> ExecutionResult:
        """Execute simple single-agent strategy."""
        context.phase = OrchestrationPhase.EXECUTION
        context.add_execution_event({
            "type": "strategy_start",
            "strategy": "simple",
            "message": "Starting simple single-agent execution"
        })

        # Simulate single agent execution
        await asyncio.sleep(0.1)  # Simulate processing

        result = ExecutionResult(
            result={"message": "Simple execution completed", "strategy": "simple"},
            confidence_score=0.8,
            metadata={"execution_type": "simple", "agents_used": 1},
            artifacts=[],
            quantum_collapse_info={}
        )

        context.phase = OrchestrationPhase.COMPLETION
        context.add_execution_event({
            "type": "strategy_complete",
            "message": "Simple strategy execution completed"
        })

        return result

    async def _execute_sequential_strategy(self, context: TaskContext) -> ExecutionResult:
        """Execute sequential agent handoff strategy."""
        context.phase = OrchestrationPhase.PLANNING

        template = self.orchestration_templates.get(
            context.request.task_type.value,
            self.orchestration_templates["custom"]
        )

        phases = template["phases"]
        handoff_criteria = template["handoff_criteria"]

        context.add_execution_event({
            "type": "strategy_start",
            "strategy": "sequential",
            "phases": len(phases),
            "message": "Starting sequential agent coordination"
        })

        phase_results = {}

        for i, phase in enumerate(phases):
            if phase["parallel"]:
                # Handle parallel sub-phases within sequential strategy
                phase_result = await self._execute_parallel_phase(context, phase)
            else:
                phase_result = await self._execute_sequential_phase(context, phase)

            phase_results[phase["name"]] = phase_result

            # Check handoff criteria for next phase
            if i < len(phases) - 1:
                next_phase_key = f"{phase['name']}_to_{phases[i+1]['name']}"
                if next_phase_key in handoff_criteria:
                    criteria_met = await self._check_handoff_criteria(
                        context, handoff_criteria[next_phase_key], phase_result
                    )
                    if not criteria_met:
                        logger.warning(f"Handoff criteria not met for {next_phase_key}")

        context.phase = OrchestrationPhase.COMPLETION
        context.add_execution_event({
            "type": "strategy_complete",
            "message": "Sequential strategy execution completed",
            "phases_completed": len(phase_results)
        })

        return ExecutionResult(
            result={
                "message": "Sequential execution completed",
                "strategy": "sequential",
                "phase_results": phase_results
            },
            confidence_score=0.85,
            metadata={
                "execution_type": "sequential",
                "phases_executed": len(phases),
                "handoff_checks": len(handoff_criteria)
            },
            artifacts=[],
            quantum_collapse_info={}
        )

    async def _execute_parallel_strategy(self, context: TaskContext) -> ExecutionResult:
        """Execute parallel agent coordination strategy."""
        context.phase = OrchestrationPhase.COORDINATION

        context.add_execution_event({
            "type": "strategy_start",
            "strategy": "parallel",
            "message": "Starting parallel agent coordination"
        })

        # Simulate parallel execution tasks
        parallel_tasks = []
        for i in range(3):  # Simulate 3 parallel agents
            task = self._simulate_agent_task(context, f"agent_{i}")
            parallel_tasks.append(task)

        # Wait for all parallel tasks to complete
        results = await asyncio.gather(*parallel_tasks, return_exceptions=True)

        # Process results
        successful_results = [r for r in results if not isinstance(r, Exception)]
        failed_results = [r for r in results if isinstance(r, Exception)]

        context.phase = OrchestrationPhase.COMPLETION
        context.add_execution_event({
            "type": "strategy_complete",
            "message": "Parallel strategy execution completed",
            "successful_agents": len(successful_results),
            "failed_agents": len(failed_results)
        })

        return ExecutionResult(
            result={
                "message": "Parallel execution completed",
                "strategy": "parallel",
                "results": successful_results,
                "failures": len(failed_results)
            },
            confidence_score=0.9,
            metadata={
                "execution_type": "parallel",
                "agents_executed": len(parallel_tasks),
                "success_rate": len(successful_results) / len(parallel_tasks)
            },
            artifacts=[],
            quantum_collapse_info={}
        )

    async def _execute_quantum_strategy(self, context: TaskContext) -> ExecutionResult:
        """Execute quantum-inspired orchestration strategy."""
        context.phase = OrchestrationPhase.EXECUTION

        context.add_execution_event({
            "type": "strategy_start",
            "strategy": "quantum",
            "message": "Starting quantum-inspired execution"
        })

        # Simulate quantum superposition - multiple solution approaches
        quantum_tasks = []
        for approach in ["conservative", "innovative", "hybrid"]:
            task = self._simulate_quantum_approach(context, approach)
            quantum_tasks.append(task)

        # Execute in quantum superposition (parallel)
        approach_results = await asyncio.gather(*quantum_tasks, return_exceptions=True)

        # Filter out exceptions before passing to collapse function
        valid_results = [r for r in approach_results if not isinstance(r, Exception)]

        # Quantum collapse - select best result
        best_result = self._collapse_quantum_results(valid_results)

        context.phase = OrchestrationPhase.COMPLETION
        context.add_execution_event({
            "type": "quantum_collapse",
            "message": "Quantum state collapsed to optimal solution",
            "approaches_evaluated": len(approach_results),
            "selected_approach": best_result.get("approach", "unknown")
        })

        return ExecutionResult(
            result={
                "message": "Quantum execution completed",
                "strategy": "quantum",
                "selected_result": best_result,
                "evaluated_approaches": len(approach_results)
            },
            confidence_score=0.95,
            quantum_collapse_info={
                "approaches": ["conservative", "innovative", "hybrid"],
                "collapse_criteria": "confidence_and_quality",
                "selected": best_result.get("approach", "unknown")
            },
            metadata={
                "execution_type": "quantum",
                "superposition_size": len(quantum_tasks),
                "collapse_successful": True
            },
            artifacts=[]
        )

    async def _execute_hybrid_strategy(self, context: TaskContext) -> ExecutionResult:
        """Execute hybrid orchestration strategy."""
        context.phase = OrchestrationPhase.COORDINATION

        context.add_execution_event({
            "type": "strategy_start",
            "strategy": "hybrid",
            "message": "Starting hybrid orchestration execution"
        })

        # Phase 1: Parallel discovery
        discovery_tasks = [
            self._simulate_agent_task(context, "discovery_agent_1"),
            self._simulate_agent_task(context, "discovery_agent_2")
        ]
        discovery_results = await asyncio.gather(*discovery_tasks)

        # Phase 2: Sequential planning based on discovery
        planning_result = await self._simulate_planning_phase(context, discovery_results)

        # Phase 3: Quantum execution of planned approaches
        execution_tasks = []
        for approach in planning_result.get("planned_approaches", ["primary", "backup"]):
            task = self._simulate_quantum_approach(context, approach)
            execution_tasks.append(task)

        execution_results = await asyncio.gather(*execution_tasks, return_exceptions=True)

        # Filter out exceptions before passing to collapse function
        valid_results = [r for r in execution_results if not isinstance(r, Exception)]
        final_result = self._collapse_quantum_results(valid_results)

        context.phase = OrchestrationPhase.COMPLETION
        context.add_execution_event({
            "type": "strategy_complete",
            "message": "Hybrid strategy execution completed",
            "phases": ["discovery", "planning", "execution"],
            "final_approach": final_result.get("approach", "unknown")
        })

        return ExecutionResult(
            result={
                "message": "Hybrid execution completed",
                "strategy": "hybrid",
                "discovery_results": discovery_results,
                "planning_result": planning_result,
                "final_result": final_result
            },
            confidence_score=0.92,
            metadata={
                "execution_type": "hybrid",
                "phases_executed": 3,
                "agents_coordination": "discovery->planning->quantum_execution"
            },
            artifacts=[],
            quantum_collapse_info={}
        )

    async def _execute_sequential_phase(self, context: TaskContext, phase: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a sequential phase with specified agents."""
        context.add_execution_event({
            "type": "phase_start",
            "phase": phase["name"],
            "agents": phase["agent_types"]
        })

        await asyncio.sleep(0.1)  # Simulate phase execution

        result = {
            "phase": phase["name"],
            "agents_used": phase["agent_types"],
            "status": "completed",
            "duration": 0.1
        }

        context.add_execution_event({
            "type": "phase_complete",
            "phase": phase["name"],
            "result": result
        })

        return result

    async def _execute_parallel_phase(self, context: TaskContext, phase: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a parallel phase with multiple agents."""
        context.add_execution_event({
            "type": "parallel_phase_start",
            "phase": phase["name"],
            "agents": phase["agent_types"]
        })

        # Create parallel tasks for each agent type
        tasks = []
        for agent_type in phase["agent_types"]:
            task = self._simulate_agent_task(context, f"{phase['name']}_{agent_type}")
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        phase_result = {
            "phase": phase["name"],
            "execution_mode": "parallel",
            "agent_results": results,
            "status": "completed"
        }

        context.add_execution_event({
            "type": "parallel_phase_complete",
            "phase": phase["name"],
            "agents_completed": len(results)
        })

        return phase_result

    async def _simulate_agent_task(self, context: TaskContext, agent_id: str) -> Dict[str, Any]:
        """Simulate agent task execution."""
        await asyncio.sleep(0.05)  # Simulate work
        return {
            "agent_id": agent_id,
            "status": "completed",
            "confidence": 0.8,
            "output": f"Result from {agent_id}"
        }

    async def _simulate_quantum_approach(self, context: TaskContext, approach: str) -> Dict[str, Any]:
        """Simulate quantum approach execution."""
        await asyncio.sleep(0.08)  # Simulate quantum processing

        # Simulate different confidence levels for different approaches
        confidence_map = {
            "conservative": 0.85,
            "innovative": 0.75,
            "hybrid": 0.90,
            "primary": 0.88,
            "backup": 0.82
        }

        return {
            "approach": approach,
            "confidence": confidence_map.get(approach, 0.8),
            "result": f"Quantum result for {approach} approach",
            "quantum_metrics": {"entanglement": 0.7, "coherence": 0.9}
        }

    async def _simulate_planning_phase(self, context: TaskContext, discovery_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Simulate planning phase based on discovery results."""
        await asyncio.sleep(0.06)  # Simulate planning

        return {
            "planned_approaches": ["primary", "backup"],
            "discovery_insights": len(discovery_results),
            "planning_confidence": 0.87,
            "execution_strategy": "quantum_dual_approach"
        }

    def _collapse_quantum_results(self, results: List[Any]) -> Dict[str, Any]:
        """Collapse quantum results to select optimal solution."""
        # Filter out exceptions and ensure confidence exists
        valid_results = [r for r in results if isinstance(r, dict) and "confidence" in r]

        if not valid_results:
            return {"approach": "fallback", "confidence": 0.5, "result": "No valid results"}

        # Select result with highest confidence
        best_result = max(valid_results, key=lambda x: x.get("confidence", 0))
        return best_result

    async def _check_handoff_criteria(
        self,
        context: TaskContext,
        criteria: List[str],
        phase_result: Dict[str, Any]
    ) -> bool:
        """Check if handoff criteria are met for phase transition."""
        # Simulate criteria checking
        await asyncio.sleep(0.02)

        # For simulation, assume criteria are met if phase completed successfully
        criteria_met = phase_result.get("status") == "completed"

        context.add_execution_event({
            "type": "handoff_check",
            "criteria": criteria,
            "criteria_met": criteria_met,
            "phase_result": phase_result.get("phase", "unknown")
        })

        return criteria_met

    def get_orchestration_status(self, orchestration_id: str) -> Optional[Dict[str, Any]]:
        """Get status of active orchestration."""
        context = self.active_orchestrations.get(orchestration_id)
        if context:
            return context.get_context_summary()
        return None

    def get_active_orchestrations(self) -> List[Dict[str, Any]]:
        """Get list of all active orchestrations."""
        return [
            context.get_context_summary()
            for context in self.active_orchestrations.values()
        ]
