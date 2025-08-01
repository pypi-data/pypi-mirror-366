"""
Base Agent class for Monkey Coder multi-agent system
Provides quantum execution capabilities and MCP integration
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Callable
from datetime import datetime

from ..quantum.manager import QuantumManager, CollapseStrategy
from ..mcp.client import MCPClient

logger = logging.getLogger(__name__)


class AgentCapability(Enum):
    """Agent capabilities that can be declared"""
    CODE_GENERATION = "code_generation"
    CODE_ANALYSIS = "code_analysis"
    CODE_REVIEW = "code_review"
    ARCHITECTURE_DESIGN = "architecture_design"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    SECURITY_ANALYSIS = "security_analysis"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    DEBUGGING = "debugging"
    REFACTORING = "refactoring"


@dataclass
class AgentContext:
    """Context shared between agents"""
    task_id: str
    user_id: str
    session_id: str
    workspace_path: Optional[str] = None
    files: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    previous_results: List[Dict[str, Any]] = field(default_factory=list)
    mcp_servers: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AgentMemory:
    """Agent memory for learning and context retention"""
    short_term: Dict[str, Any] = field(default_factory=dict)
    long_term: Dict[str, Any] = field(default_factory=dict)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    learned_patterns: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """
    Base class for all agents in the Monkey Coder system
    Provides quantum execution and MCP integration capabilities
    """
    
    def __init__(self, name: str, capabilities: Set[AgentCapability]):
        self.name = name
        self.capabilities = capabilities
        self.quantum_manager = QuantumManager()
        self.mcp_clients: Dict[str, MCPClient] = {}
        self.memory = AgentMemory()
        self._is_initialized = False
        
    async def initialize(self):
        """Initialize the agent"""
        if self._is_initialized:
            return
            
        logger.info(f"Initializing agent: {self.name}")
        await self._setup()
        self._is_initialized = True
        
    @abstractmethod
    async def _setup(self):
        """Agent-specific setup logic"""
        pass
        
    async def connect_mcp_servers(self, servers: List[str]) -> None:
        """Connect to MCP servers"""
        for server in servers:
            if server not in self.mcp_clients:
                try:
                    client = await MCPClient.connect(server)
                    self.mcp_clients[server] = client
                    logger.info(f"{self.name} connected to MCP server: {server}")
                except Exception as e:
                    logger.error(f"Failed to connect to MCP server {server}: {e}")
                    
    async def disconnect_mcp_servers(self) -> None:
        """Disconnect from all MCP servers"""
        for server, client in self.mcp_clients.items():
            try:
                await client.disconnect()
                logger.info(f"{self.name} disconnected from MCP server: {server}")
            except Exception as e:
                logger.error(f"Error disconnecting from MCP server {server}: {e}")
        self.mcp_clients.clear()
        
    @abstractmethod
    async def process(self, task: str, context: AgentContext) -> Dict[str, Any]:
        """
        Process a task with the given context
        Must be implemented by subclasses
        """
        pass
        
    def get_quantum_variations(self, task: str, context: AgentContext) -> List[Dict[str, Any]]:
        """
        Get quantum variations for the task
        Can be overridden by subclasses for custom variations
        """
        return [
            {"id": "default", "params": {}},
            {"id": "optimized", "params": {"optimize": True}},
            {"id": "comprehensive", "params": {"comprehensive": True}},
        ]
        
    async def execute_with_quantum(
        self,
        task: str,
        context: AgentContext,
        collapse_strategy: CollapseStrategy = CollapseStrategy.BEST_SCORE,
        scoring_fn: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Execute task using quantum superposition"""
        variations = self.get_quantum_variations(task, context)
        
        # Create quantum task variations
        from ..quantum.manager import TaskVariation
        
        quantum_variations = []
        for var in variations:
            async def task_fn(t=task, c=context, p=var["params"]):
                return await self.process(t, c, **p)
            quantum_variations.append(TaskVariation(
                id=var["id"],
                task=task_fn,
                params={}
            ))
            
        # Execute with quantum manager
        result = await self.quantum_manager.execute_quantum_task(
            quantum_variations,
            collapse_strategy=collapse_strategy,
            scoring_fn=scoring_fn or self._default_scoring_fn
        )
        
        return result.value if result else {}
        
    def _default_scoring_fn(self, result: Any) -> float:
        """Default scoring function for quantum collapse"""
        if isinstance(result, dict):
            # Score based on completeness and quality metrics
            score = 0.0
            if "code" in result:
                score += 0.3
            if "tests" in result:
                score += 0.2
            if "documentation" in result:
                score += 0.2
            if "confidence" in result:
                score += result["confidence"] * 0.3
            return score
        return 0.0
        
    async def use_mcp_tool(self, server: str, tool: str, arguments: Dict[str, Any]) -> Any:
        """Use an MCP tool from a connected server"""
        if server not in self.mcp_clients:
            raise ValueError(f"Not connected to MCP server: {server}")
            
        client = self.mcp_clients[server]
        return await client.call_tool(tool, arguments)
        
    async def get_mcp_resource(self, server: str, uri: str) -> Any:
        """Get a resource from an MCP server"""
        if server not in self.mcp_clients:
            raise ValueError(f"Not connected to MCP server: {server}")
            
        client = self.mcp_clients[server]
        return await client.get_resource(uri)
        
    def update_memory(self, key: str, value: Any, memory_type: str = "short_term"):
        """Update agent memory"""
        if memory_type == "short_term":
            self.memory.short_term[key] = value
        elif memory_type == "long_term":
            self.memory.long_term[key] = value
        else:
            raise ValueError(f"Unknown memory type: {memory_type}")
            
    def recall_memory(self, key: str, memory_type: str = "short_term") -> Any:
        """Recall from agent memory"""
        if memory_type == "short_term":
            return self.memory.short_term.get(key)
        elif memory_type == "long_term":
            return self.memory.long_term.get(key)
        else:
            raise ValueError(f"Unknown memory type: {memory_type}")
            
    def add_to_conversation(self, role: str, content: str):
        """Add to conversation history"""
        self.memory.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
    def learn_pattern(self, pattern_name: str, pattern_data: Dict[str, Any]):
        """Learn a new pattern for future use"""
        self.memory.learned_patterns[pattern_name] = pattern_data
        
    async def collaborate_with(self, other_agent: 'BaseAgent', task: str, context: AgentContext) -> Dict[str, Any]:
        """Collaborate with another agent on a task"""
        # Share context and memory
        shared_context = AgentContext(
            task_id=context.task_id,
            user_id=context.user_id,
            session_id=context.session_id,
            workspace_path=context.workspace_path,
            files=context.files.copy(),
            metadata={**context.metadata, "collaboration": True},
            previous_results=context.previous_results + [{"agent": self.name, "memory": self.memory.short_term}],
            mcp_servers=context.mcp_servers
        )
        
        # Execute tasks in parallel
        results = await asyncio.gather(
            self.process(f"[Collaboration] {task}", shared_context),
            other_agent.process(f"[Collaboration] {task}", shared_context)
        )
        
        # Convert tuple to list for _combine_results
        results_list = list(results)
        
        # Combine results
        return {
            "collaboration": True,
            "agents": [self.name, other_agent.name],
            "results": {
                self.name: results_list[0],
                other_agent.name: results_list[1]
            },
            "combined": self._combine_results(results_list)
        }
        
    def _combine_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine results from multiple agents"""
        combined = {}
        for result in results:
            if isinstance(result, dict):
                for key, value in result.items():
                    if key not in combined:
                        combined[key] = value
                    elif isinstance(value, list) and isinstance(combined[key], list):
                        combined[key].extend(value)
                    elif isinstance(value, dict) and isinstance(combined[key], dict):
                        combined[key].update(value)
        return combined
        
    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}', capabilities={[c.value for c in self.capabilities]})"
