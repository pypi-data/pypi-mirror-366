"""
Functional Quantum Execution Manager

This module implements quantum-inspired execution patterns for parallel task processing,
task variations generation, and collapse strategies for result optimization.

Inspired by quantum computing principles:
- Superposition: Multiple task variations executed in parallel
- Entanglement: Task dependencies and relationships
- Collapse: Selection of optimal results based on strategies
"""

import asyncio
import logging
import time
from collections import defaultdict
from enum import Enum
from functools import wraps
from typing import Any, Awaitable, Callable, Dict, List, Optional, TypeVar, Union
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

try:
    import anyio
except ImportError:
    anyio = None

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CollapseStrategy(Enum):
    """Strategies for collapsing quantum execution results."""
    
    FIRST_SUCCESS = "first_success"  # Return first successful result
    BEST_SCORE = "best_score"       # Return result with highest score
    CONSENSUS = "consensus"         # Return result agreed upon by majority
    COMBINED = "combined"           # Combine multiple results intelligently


@dataclass
class TaskVariation:
    """Represents a variation of a task for quantum execution."""
    
    id: str
    task: Callable
    params: Dict[str, Any]
    weight: float = 1.0
    priority: int = 0
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class QuantumResult:
    """Result from quantum task execution."""
    
    value: Any
    score: float = 0.0
    execution_time: float = 0.0
    variation_id: str = ""
    metadata: Optional[Dict[str, Any]] = None
    success: bool = True
    error: Optional[Exception] = None


class QuantumManager:
    """
    Functional Quantum Execution Manager.
    
    Provides quantum-inspired execution patterns including:
    - Task variation generation
    - Async parallel execution  
    - Multiple collapse strategies
    - Performance optimization
    """
    
    def __init__(
        self,
        max_workers: int = 4,
        timeout: float = 30.0,
        default_strategy: CollapseStrategy = CollapseStrategy.FIRST_SUCCESS
    ):
        self.max_workers = max_workers
        self.timeout = timeout
        self.default_strategy = default_strategy
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._metrics = defaultdict(list)
        
        # Check if anyio is available
        if anyio is None:
            logger.warning("anyio not available, falling back to asyncio")
    
    async def execute_quantum_task(
        self,
        variations: List[TaskVariation],
        collapse_strategy: Optional[CollapseStrategy] = None,
        scoring_fn: Optional[Callable[[Any], float]] = None
    ) -> QuantumResult:
        """
        Execute task variations in quantum superposition and collapse to optimal result.
        
        Args:
            variations: List of task variations to execute in parallel
            collapse_strategy: Strategy for selecting final result
            scoring_fn: Function to score results for BEST_SCORE strategy
            
        Returns:
            QuantumResult containing the collapsed result
        """
        strategy = collapse_strategy or self.default_strategy
        start_time = time.time()
        
        logger.info(f"Starting quantum execution with {len(variations)} variations")
        
        # Execute variations in parallel using anyio if available
        if anyio is not None:
            results = await self._execute_with_anyio(variations)
        else:
            results = await self._execute_with_asyncio(variations)
        
        # Collapse results based on strategy
        final_result = self._collapse_results(results, strategy, scoring_fn)
        
        execution_time = time.time() - start_time
        final_result.execution_time = execution_time
        
        # Record metrics
        self._record_metrics(strategy, len(variations), execution_time, final_result.success)
        
        logger.info(f"Quantum execution completed in {execution_time:.3f}s")
        return final_result
    
    async def _execute_with_anyio(self, variations: List[TaskVariation]) -> List[QuantumResult]:
        """Execute variations using anyio for structured concurrency."""
        results = []
        
        async with anyio.create_task_group() as tg:
            for variation in variations:
                tg.start_soon(self._execute_variation, variation, results)
        
        return results
    
    async def _execute_with_asyncio(self, variations: List[TaskVariation]) -> List[QuantumResult]:
        """Execute variations using standard asyncio."""
        tasks = [
            self._execute_variation_async(variation) 
            for variation in variations
        ]
        
        try:
            completed_results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=self.timeout
            )
            
            results = []
            for i, result in enumerate(completed_results):
                if isinstance(result, Exception):
                    results.append(QuantumResult(
                        value=None,
                        success=False,
                        error=result,
                        variation_id=variations[i].id
                    ))
                else:
                    results.append(result)
            
            return results
            
        except asyncio.TimeoutError:
            logger.warning(f"Quantum execution timed out after {self.timeout}s")
            return [QuantumResult(
                value=None,
                success=False,
                error=asyncio.TimeoutError("Execution timed out"),
                variation_id="timeout"
            )]
    
    async def _execute_variation(self, variation: TaskVariation, results: List[QuantumResult]):
        """Execute a single variation and append result to results list (for anyio)."""
        result = await self._execute_variation_async(variation)
        results.append(result)
    
    async def _execute_variation_async(self, variation: TaskVariation) -> QuantumResult:
        """Execute a single task variation asynchronously."""
        start_time = time.time()
        
        try:
            # Handle both sync and async tasks
            if asyncio.iscoroutinefunction(variation.task):
                result_value = await variation.task(**variation.params)
            else:
                # Run sync function in thread pool
                loop = asyncio.get_event_loop()
                result_value = await loop.run_in_executor(
                    self._executor,
                    lambda: variation.task(**variation.params)
                )
            
            execution_time = time.time() - start_time
            
            return QuantumResult(
                value=result_value,
                execution_time=execution_time,
                variation_id=variation.id,
                success=True,
                metadata=variation.metadata
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Variation {variation.id} failed: {e}")
            
            return QuantumResult(
                value=None,
                execution_time=execution_time,
                variation_id=variation.id,
                success=False,
                error=e,
                metadata=variation.metadata
            )
    
    def _collapse_results(
        self,
        results: List[QuantumResult],
        strategy: CollapseStrategy,
        scoring_fn: Optional[Callable[[Any], float]] = None
    ) -> QuantumResult:
        """Collapse multiple results into a single result based on strategy."""
        
        successful_results = [r for r in results if r.success]
        
        if not successful_results:
            # Return first failed result if no successes
            return results[0] if results else QuantumResult(
                value=None,
                success=False,
                error=Exception("No results available")
            )
        
        if strategy == CollapseStrategy.FIRST_SUCCESS:
            return self._collapse_first_success(successful_results)
        
        elif strategy == CollapseStrategy.BEST_SCORE:
            return self._collapse_best_score(successful_results, scoring_fn)
        
        elif strategy == CollapseStrategy.CONSENSUS:
            return self._collapse_consensus(successful_results)
        
        elif strategy == CollapseStrategy.COMBINED:
            return self._collapse_combined(successful_results)
        
        else:
            return successful_results[0]
    
    def _collapse_first_success(self, results: List[QuantumResult]) -> QuantumResult:
        """Return the first successful result."""
        # Sort by priority if available, then by execution time
        sorted_results = sorted(
            results,
            key=lambda r: (
                getattr(r.metadata or {}, 'priority', 0),
                r.execution_time
            )
        )
        return sorted_results[0]
    
    def _collapse_best_score(
        self,
        results: List[QuantumResult],
        scoring_fn: Optional[Callable[[Any], float]] = None
    ) -> QuantumResult:
        """Return the result with the highest score."""
        
        if scoring_fn:
            # Apply custom scoring function
            for result in results:
                try:
                    result.score = scoring_fn(result.value)
                except Exception as e:
                    logger.warning(f"Scoring failed for result: {e}")
                    result.score = 0.0
        
        # Return result with highest score
        best_result = max(results, key=lambda r: r.score)
        return best_result
    
    def _collapse_consensus(self, results: List[QuantumResult]) -> QuantumResult:
        """Return result based on consensus (most common value)."""
        
        # Group results by value (simple equality check)
        value_groups = defaultdict(list)
        for result in results:
            # Use string representation for grouping
            key = str(result.value)
            value_groups[key].append(result)
        
        # Find the most common result
        if not value_groups:
            return results[0]
        
        most_common_group = max(value_groups.values(), key=len)
        
        # Return the fastest result from the most common group
        return min(most_common_group, key=lambda r: r.execution_time)
    
    def _collapse_combined(self, results: List[QuantumResult]) -> QuantumResult:
        """Intelligently combine multiple results."""
        
        if len(results) == 1:
            return results[0]
        
        # For combined strategy, we'll create a composite result
        # This is a simplified implementation - could be more sophisticated
        
        combined_value = {
            'primary': results[0].value,
            'alternatives': [r.value for r in results[1:]],
            'execution_times': [r.execution_time for r in results],
            'variation_ids': [r.variation_id for r in results]
        }
        
        avg_score = sum(r.score for r in results) / len(results)
        total_time = sum(r.execution_time for r in results)
        
        return QuantumResult(
            value=combined_value,
            score=avg_score,
            execution_time=total_time,
            variation_id="combined",
            success=True,
            metadata={'strategy': 'combined', 'count': len(results)}
        )
    
    def generate_variations(
        self,
        base_task: Callable,
        base_params: Dict[str, Any],
        variation_configs: List[Dict[str, Any]]
    ) -> List[TaskVariation]:
        """
        Generate task variations from a base task and configuration variations.
        
        Args:
            base_task: The base task function to vary
            base_params: Base parameters for the task
            variation_configs: List of parameter variations and metadata
            
        Returns:
            List of TaskVariation objects
        """
        variations = []
        
        for i, config in enumerate(variation_configs):
            # Merge base params with variation-specific params
            params = {**base_params, **config.get('params', {})}
            
            variation = TaskVariation(
                id=config.get('id', f"variation_{i}"),
                task=config.get('task', base_task),
                params=params,
                weight=config.get('weight', 1.0),
                priority=config.get('priority', 0),
                metadata=config.get('metadata', {})
            )
            
            variations.append(variation)
        
        return variations
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get execution metrics."""
        return dict(self._metrics)
    
    def _record_metrics(
        self,
        strategy: CollapseStrategy,
        variation_count: int,
        execution_time: float,
        success: bool
    ):
        """Record execution metrics."""
        self._metrics['executions'].append({
            'strategy': strategy.value,
            'variation_count': variation_count,
            'execution_time': execution_time,
            'success': success,
            'timestamp': time.time()
        })
    
    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=False)


def quantum_task(
    variations: Optional[List[Dict[str, Any]]] = None,
    collapse_strategy: CollapseStrategy = CollapseStrategy.FIRST_SUCCESS,
    scoring_fn: Optional[Callable[[Any], float]] = None,
    max_workers: int = 4,
    timeout: float = 30.0
):
    """
    Decorator to make a function execute in quantum mode with variations.
    
    Args:
        variations: List of parameter variations to try
        collapse_strategy: Strategy for selecting final result
        scoring_fn: Function to score results
        max_workers: Maximum parallel workers
        timeout: Execution timeout in seconds
        
    Usage:
        @quantum_task(
            variations=[
                {'params': {'approach': 'method1'}, 'weight': 1.0},
                {'params': {'approach': 'method2'}, 'weight': 0.8}
            ],
            collapse_strategy=CollapseStrategy.BEST_SCORE,
            scoring_fn=lambda x: len(str(x))  # Prefer longer results
        )
        async def my_task(input_data, approach='default'):
            # Task implementation
            return f"Result using {approach}: {input_data}"
    """
    
    def decorator(func: Callable[..., T]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            manager = QuantumManager(
                max_workers=max_workers,
                timeout=timeout,
                default_strategy=collapse_strategy
            )
            
            # If no variations specified, just run the function normally
            if not variations:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
            
            # Convert args to kwargs for variation generation
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            base_params = dict(bound_args.arguments)
            
            # Generate variations
            task_variations = manager.generate_variations(
                base_task=func,
                base_params=base_params,
                variation_configs=variations
            )
            
            # Execute quantum task
            result = await manager.execute_quantum_task(
                variations=task_variations,
                collapse_strategy=collapse_strategy,
                scoring_fn=scoring_fn
            )
            
            if not result.success:
                raise result.error or Exception("Quantum task execution failed")
            
            return result.value
        
        return wrapper
    return decorator
