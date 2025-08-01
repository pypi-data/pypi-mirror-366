"""
Agent Orchestrator for coordinating multi-agent execution
Handles agent selection, task distribution, and result aggregation
"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

from .base_agent import BaseAgent, AgentCapability, AgentContext
from ..quantum.manager import QuantumManager, CollapseStrategy, TaskVariation
from ..pricing.models import get_model_pricing

logger = logging.getLogger(__name__)


class OrchestrationStrategy(Enum):
    """Strategies for orchestrating agent execution"""
    SEQUENTIAL = "sequential"      # Agents work one after another
    PARALLEL = "parallel"          # All agents work simultaneously
    PIPELINE = "pipeline"          # Output of one feeds into next
    COLLABORATIVE = "collaborative" # Agents work together with shared context
    QUANTUM = "quantum"           # Quantum superposition of agent approaches


@dataclass
class AgentTask:
    """Task assigned to an agent"""
    task_id: str
    agent_name: str
    description: str
    priority: int = 0
    dependencies: List[str] = field(default_factory=list)
    estimated_cost: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    """Result from agent execution"""
    agent_name: str
    task_id: str
    result: Any
    success: bool = True
    error: Optional[Exception] = None
    execution_time: float = 0.0
    tokens_used: int = 0
    actual_cost: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentOrchestrator:
    """
    Orchestrates multi-agent execution with quantum capabilities
    """
    
    def __init__(self, default_strategy: OrchestrationStrategy = OrchestrationStrategy.COLLABORATIVE):
        self.agents: Dict[str, BaseAgent] = {}
        self.default_strategy = default_strategy
        self.quantum_manager = QuantumManager()
        self._execution_history: List[Dict[str, Any]] = []
        
    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the orchestrator"""
        self.agents[agent.name] = agent
        logger.info(f"Registered agent: {agent.name} with capabilities: {[c.value for c in agent.capabilities]}")
        
    def register_agents(self, agents: List[BaseAgent]) -> None:
        """Register multiple agents"""
        for agent in agents:
            self.register_agent(agent)
            
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get agent by name"""
        return self.agents.get(name)
        
    def find_agents_by_capability(self, capability: AgentCapability) -> List[BaseAgent]:
        """Find all agents with a specific capability"""
        return [
            agent for agent in self.agents.values()
            if capability in agent.capabilities
        ]
        
    async def execute_task(
        self,
        task: str,
        context: AgentContext,
        selected_agents: Optional[List[str]] = None,
        strategy: Optional[OrchestrationStrategy] = None,
        estimate_only: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a task using the orchestrator
        
        Args:
            task: Task description
            context: Execution context
            selected_agents: Specific agents to use (None = auto-select)
            strategy: Orchestration strategy (None = use default)
            estimate_only: Only estimate cost without execution
            
        Returns:
            Execution results including agent outputs and costs
        """
        strategy = strategy or self.default_strategy
        
        # Select agents if not specified
        if not selected_agents:
            selected_agents = await self._auto_select_agents(task, context)
            
        # Validate agents exist
        for agent_name in selected_agents:
            if agent_name not in self.agents:
                raise ValueError(f"Unknown agent: {agent_name}")
                
        # Estimate costs
        cost_estimate = await self._estimate_cost(task, selected_agents, context)
        
        if estimate_only:
            return {
                "estimate_only": True,
                "selected_agents": selected_agents,
                "estimated_cost": cost_estimate,
                "strategy": strategy.value
            }
            
        # Initialize agents and connect MCP servers
        await self._initialize_agents(selected_agents, context.mcp_servers)
        
        # Execute based on strategy
        start_time = datetime.now()
        
        if strategy == OrchestrationStrategy.QUANTUM:
            results = await self._execute_quantum(task, context, selected_agents)
        elif strategy == OrchestrationStrategy.PARALLEL:
            results = await self._execute_parallel(task, context, selected_agents)
        elif strategy == OrchestrationStrategy.SEQUENTIAL:
            results = await self._execute_sequential(task, context, selected_agents)
        elif strategy == OrchestrationStrategy.PIPELINE:
            results = await self._execute_pipeline(task, context, selected_agents)
        else:  # COLLABORATIVE
            results = await self._execute_collaborative(task, context, selected_agents)
            
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Calculate actual costs
        total_cost = sum(r.actual_cost for r in results)
        
        # Record execution
        self._record_execution(task, selected_agents, strategy, results, execution_time)
        
        return {
            "task": task,
            "strategy": strategy.value,
            "agents": selected_agents,
            "results": results,
            "execution_time": execution_time,
            "estimated_cost": cost_estimate,
            "actual_cost": total_cost,
            "cost_difference": total_cost - cost_estimate["total"]
        }
        
    async def _auto_select_agents(self, task: str, context: AgentContext) -> List[str]:
        """Automatically select appropriate agents based on task"""
        # Simple heuristic-based selection
        selected = []
        
        task_lower = task.lower()
        
        # Analyze task to determine needed capabilities
        if any(keyword in task_lower for keyword in ["generate", "create", "implement", "code", "function", "class"]):
            agents = self.find_agents_by_capability(AgentCapability.CODE_GENERATION)
            if agents:
                selected.append(agents[0].name)
                
        if any(keyword in task_lower for keyword in ["analyze", "review", "check", "inspect"]):
            agents = self.find_agents_by_capability(AgentCapability.CODE_ANALYSIS)
            if agents:
                selected.append(agents[0].name)
                
        if any(keyword in task_lower for keyword in ["test", "unit test", "integration"]):
            agents = self.find_agents_by_capability(AgentCapability.TESTING)
            if agents:
                selected.append(agents[0].name)
                
        if any(keyword in task_lower for keyword in ["document", "docs", "readme", "comment"]):
            agents = self.find_agents_by_capability(AgentCapability.DOCUMENTATION)
            if agents:
                selected.append(agents[0].name)
                
        if any(keyword in task_lower for keyword in ["design", "architect", "structure", "pattern"]):
            agents = self.find_agents_by_capability(AgentCapability.ARCHITECTURE_DESIGN)
            if agents:
                selected.append(agents[0].name)
                
        # Default to code generator if nothing selected
        if not selected and self.agents:
            selected = [list(self.agents.keys())[0]]
            
        return selected
        
    async def _estimate_cost(self, task: str, agent_names: List[str], context: AgentContext) -> Dict[str, Any]:
        """Estimate execution cost"""
        estimates = {}
        
        # Rough token estimation based on task complexity
        base_tokens = len(task.split()) * 10  # Very rough estimate
        
        for agent_name in agent_names:
            agent = self.agents[agent_name]
            
            # Estimate tokens based on agent type
            if AgentCapability.CODE_GENERATION in agent.capabilities:
                estimated_tokens = base_tokens * 5
            elif AgentCapability.CODE_ANALYSIS in agent.capabilities:
                estimated_tokens = base_tokens * 3
            elif AgentCapability.TESTING in agent.capabilities:
                estimated_tokens = base_tokens * 4
            else:
                estimated_tokens = base_tokens * 2
                
            # Get model pricing (assuming GPT-4.1 for now)
            pricing = get_model_pricing("gpt-4.1")
            if pricing:
                cost = pricing.calculate_cost(estimated_tokens // 2, estimated_tokens // 2)[2]
            else:
                cost = estimated_tokens * 0.00003  # Default pricing
                
            estimates[agent_name] = {
                "estimated_tokens": estimated_tokens,
                "estimated_cost": cost
            }
            
        total_cost = sum(e["estimated_cost"] for e in estimates.values())
        
        return {
            "agents": estimates,
            "total": total_cost
        }
        
    async def _initialize_agents(self, agent_names: List[str], mcp_servers: List[str]) -> None:
        """Initialize selected agents and connect MCP servers"""
        init_tasks = []
        
        for agent_name in agent_names:
            agent = self.agents[agent_name]
            init_tasks.append(agent.initialize())
            
            if mcp_servers:
                init_tasks.append(agent.connect_mcp_servers(mcp_servers))
                
        await asyncio.gather(*init_tasks)
        
    async def _execute_quantum(self, task: str, context: AgentContext, agent_names: List[str]) -> List[AgentResult]:
        """Execute agents in quantum superposition"""
        variations = []
        
        for agent_name in agent_names:
            agent = self.agents[agent_name]
            
            # Create variations for each agent approach
            for i in range(3):  # 3 variations per agent
                async def agent_task(a=agent, t=task, c=context, variant=i):
                    start_time = datetime.now()
                    try:
                        # Add variation to context
                        variant_context = AgentContext(
                            **{**c.__dict__, "metadata": {**c.metadata, "variant": variant}}
                        )
                        result = await a.process(t, variant_context)
                        
                        return AgentResult(
                            agent_name=a.name,
                            task_id=c.task_id,
                            result=result,
                            execution_time=(datetime.now() - start_time).total_seconds()
                        )
                    except Exception as e:
                        return AgentResult(
                            agent_name=a.name,
                            task_id=c.task_id,
                            result=None,
                            success=False,
                            error=e,
                            execution_time=(datetime.now() - start_time).total_seconds()
                        )
                        
                variations.append(TaskVariation(
                    id=f"{agent_name}_variant_{i}",
                    task=agent_task,
                    params={},
                    priority=len(agent_names) - agent_names.index(agent_name)
                ))
                
        # Execute all variations in quantum superposition
        quantum_result = await self.quantum_manager.execute_quantum_task(
            variations,
            collapse_strategy=CollapseStrategy.BEST_SCORE,
            scoring_fn=self._score_agent_result
        )
        
        # Return the collapsed result
        if quantum_result.success:
            return [quantum_result.value]
        else:
            return [AgentResult(
                agent_name="quantum_collapsed",
                task_id=context.task_id,
                result=None,
                success=False,
                error=quantum_result.error
            )]
            
    async def _execute_parallel(self, task: str, context: AgentContext, agent_names: List[str]) -> List[AgentResult]:
        """Execute agents in parallel"""
        tasks = []
        
        for agent_name in agent_names:
            agent = self.agents[agent_name]
            tasks.append(self._execute_single_agent(agent, task, context))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to AgentResult
        agent_results: List[AgentResult] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                agent_results.append(AgentResult(
                    agent_name=agent_names[i],
                    task_id=context.task_id,
                    result=None,
                    success=False,
                    error=result
                ))
            elif isinstance(result, AgentResult):
                agent_results.append(result)
                
        return agent_results
        
    async def _execute_sequential(self, task: str, context: AgentContext, agent_names: List[str]) -> List[AgentResult]:
        """Execute agents sequentially"""
        results: List[AgentResult] = []
        
        for agent_name in agent_names:
            agent = self.agents[agent_name]
            
            # Update context with previous results
            if results:
                context.previous_results.append({
                    "agent": results[-1].agent_name,
                    "result": results[-1].result
                })
                
            result = await self._execute_single_agent(agent, task, context)
            results.append(result)
            
            # Stop on failure
            if not result.success:
                break
                
        return results
        
    async def _execute_pipeline(self, task: str, context: AgentContext, agent_names: List[str]) -> List[AgentResult]:
        """Execute agents in pipeline (output of one feeds into next)"""
        results = []
        current_task = task
        
        for agent_name in agent_names:
            agent = self.agents[agent_name]
            
            result = await self._execute_single_agent(agent, current_task, context)
            results.append(result)
            
            if result.success and isinstance(result.result, dict) and "output" in result.result:
                # Use output as input for next agent
                current_task = str(result.result["output"])
            else:
                # Stop pipeline on failure
                break
                
        return results
        
    async def _execute_collaborative(self, task: str, context: AgentContext, agent_names: List[str]) -> List[AgentResult]:
        """Execute agents collaboratively with shared context"""
        if len(agent_names) < 2:
            # Fall back to single agent execution
            return await self._execute_parallel(task, context, agent_names)
            
        results = []
        
        # Pair up agents for collaboration
        for i in range(0, len(agent_names), 2):
            if i + 1 < len(agent_names):
                # Collaborate between pairs
                agent1 = self.agents[agent_names[i]]
                agent2 = self.agents[agent_names[i + 1]]
                
                collab_result = await agent1.collaborate_with(agent2, task, context)
                
                # Create result for collaboration
                results.append(AgentResult(
                    agent_name=f"{agent1.name}+{agent2.name}",
                    task_id=context.task_id,
                    result=collab_result,
                    metadata={"collaboration": True}
                ))
            else:
                # Odd agent out - execute alone
                agent = self.agents[agent_names[i]]
                result = await self._execute_single_agent(agent, task, context)
                results.append(result)
                
        return results
        
    async def _execute_single_agent(self, agent: BaseAgent, task: str, context: AgentContext) -> AgentResult:
        """Execute a single agent"""
        start_time = datetime.now()
        
        try:
            result = await agent.process(task, context)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Calculate actual cost (simplified for now)
            tokens_used = len(str(result)) // 4  # Rough estimate
            pricing = get_model_pricing("gpt-4.1")
            actual_cost = pricing.calculate_cost(tokens_used // 2, tokens_used // 2)[2] if pricing else 0.0
            
            return AgentResult(
                agent_name=agent.name,
                task_id=context.task_id,
                result=result,
                execution_time=execution_time,
                tokens_used=tokens_used,
                actual_cost=actual_cost
            )
            
        except Exception as e:
            logger.error(f"Agent {agent.name} failed: {e}")
            return AgentResult(
                agent_name=agent.name,
                task_id=context.task_id,
                result=None,
                success=False,
                error=e,
                execution_time=(datetime.now() - start_time).total_seconds()
            )
            
    def _score_agent_result(self, result: Any) -> float:
        """Score agent results for quantum collapse"""
        if not isinstance(result, AgentResult):
            return 0.0
            
        score = 0.0
        
        # Success is most important
        if result.success:
            score += 0.5
            
        # Faster execution is better
        if result.execution_time < 1.0:
            score += 0.2
        elif result.execution_time < 5.0:
            score += 0.1
            
        # Lower cost is better
        if result.actual_cost < 0.01:
            score += 0.2
        elif result.actual_cost < 0.05:
            score += 0.1
            
        # Check result quality
        if result.result and isinstance(result.result, dict):
            if "code" in result.result:
                score += 0.1
            if "tests" in result.result:
                score += 0.1
            if "documentation" in result.result:
                score += 0.1
                
        return score
        
    def _record_execution(
        self,
        task: str,
        agents: List[str],
        strategy: OrchestrationStrategy,
        results: List[AgentResult],
        execution_time: float
    ):
        """Record execution for analytics"""
        self._execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "agents": agents,
            "strategy": strategy.value,
            "results": len(results),
            "successful": sum(1 for r in results if r.success),
            "total_cost": sum(r.actual_cost for r in results),
            "execution_time": execution_time
        })
        
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get execution history"""
        return self._execution_history.copy()
