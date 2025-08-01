"""
Tests for the Functional Quantum Execution Module
"""

import asyncio
import pytest
from unittest.mock import Mock, patch
import time

from monkey_coder.quantum import QuantumManager, quantum_task, CollapseStrategy
from monkey_coder.quantum.manager import TaskVariation, QuantumResult


class TestQuantumManager:
    """Test cases for QuantumManager."""
    
    @pytest.fixture
    def manager(self):
        """Create a QuantumManager instance for testing."""
        return QuantumManager(max_workers=2, timeout=5.0)
    
    @pytest.mark.asyncio
    async def test_simple_quantum_execution(self, manager):
        """Test basic quantum execution with single variation."""
        
        def sample_task(value):
            return value * 2
        
        variations = [
            TaskVariation(
                id="test_1",
                task=sample_task,
                params={"value": 5}
            )
        ]
        
        result = await manager.execute_quantum_task(variations)
        
        assert result.success is True
        assert result.value == 10
        assert result.variation_id == "test_1"
        assert result.execution_time > 0
    
    @pytest.mark.asyncio
    async def test_multiple_variations_first_success(self, manager):
        """Test quantum execution with multiple variations and FIRST_SUCCESS strategy."""
        
        def fast_task(delay, value):
            time.sleep(delay)
            return f"result_{value}"
        
        variations = [
            TaskVariation(id="slow", task=fast_task, params={"delay": 0.2, "value": 1}),
            TaskVariation(id="fast", task=fast_task, params={"delay": 0.1, "value": 2}),
            TaskVariation(id="slower", task=fast_task, params={"delay": 0.3, "value": 3}),
        ]
        
        result = await manager.execute_quantum_task(
            variations, 
            collapse_strategy=CollapseStrategy.FIRST_SUCCESS
        )
        
        assert result.success is True
        # Should get the fastest result
        assert result.value == "result_2"
        assert result.variation_id == "fast"
    
    @pytest.mark.asyncio
    async def test_best_score_strategy(self, manager):
        """Test BEST_SCORE collapse strategy."""
        
        def scoring_task(value):
            return f"output_{value}"
        
        def score_function(output):
            # Extract number from "output_X" and return as score
            return int(output.split("_")[1])
        
        variations = [
            TaskVariation(id="low", task=scoring_task, params={"value": 3}),
            TaskVariation(id="high", task=scoring_task, params={"value": 8}),
            TaskVariation(id="mid", task=scoring_task, params={"value": 5}),
        ]
        
        result = await manager.execute_quantum_task(
            variations,
            collapse_strategy=CollapseStrategy.BEST_SCORE,
            scoring_fn=score_function
        )
        
        assert result.success is True
        assert result.value == "output_8"
        assert result.variation_id == "high"
        assert result.score == 8.0
    
    @pytest.mark.asyncio
    async def test_consensus_strategy(self, manager):
        """Test CONSENSUS collapse strategy."""
        
        def consensus_task(result_type):
            return f"result_{result_type}"
        
        variations = [
            TaskVariation(id="v1", task=consensus_task, params={"result_type": "A"}),
            TaskVariation(id="v2", task=consensus_task, params={"result_type": "A"}),
            TaskVariation(id="v3", task=consensus_task, params={"result_type": "B"}),
            TaskVariation(id="v4", task=consensus_task, params={"result_type": "A"}),
        ]
        
        result = await manager.execute_quantum_task(
            variations,
            collapse_strategy=CollapseStrategy.CONSENSUS
        )
        
        assert result.success is True
        assert result.value == "result_A"  # Most common result
    
    @pytest.mark.asyncio
    async def test_combined_strategy(self, manager):
        """Test COMBINED collapse strategy."""
        
        def combined_task(approach, value):
            return f"{approach}_{value}"
        
        variations = [
            TaskVariation(id="method1", task=combined_task, params={"approach": "A", "value": 1}),
            TaskVariation(id="method2", task=combined_task, params={"approach": "B", "value": 2}),
            TaskVariation(id="method3", task=combined_task, params={"approach": "C", "value": 3}),
        ]
        
        result = await manager.execute_quantum_task(
            variations,
            collapse_strategy=CollapseStrategy.COMBINED
        )
        
        assert result.success is True
        assert result.variation_id == "combined"
        assert isinstance(result.value, dict)
        assert "primary" in result.value
        assert "alternatives" in result.value
        assert result.value["primary"] == "A_1"
        assert len(result.value["alternatives"]) == 2
    
    @pytest.mark.asyncio
    async def test_async_task_execution(self, manager):
        """Test execution of async tasks."""
        
        async def async_task(value):
            await asyncio.sleep(0.1)
            return value * 3
        
        variations = [
            TaskVariation(id="async_test", task=async_task, params={"value": 4})
        ]
        
        result = await manager.execute_quantum_task(variations)
        
        assert result.success is True
        assert result.value == 12
        assert result.execution_time >= 0.1
    
    @pytest.mark.asyncio
    async def test_error_handling(self, manager):
        """Test error handling in quantum execution."""
        
        def failing_task():
            raise ValueError("Test error")
        
        def successful_task():
            return "success"
        
        variations = [
            TaskVariation(id="fail", task=failing_task, params={}),
            TaskVariation(id="success", task=successful_task, params={}),
        ]
        
        result = await manager.execute_quantum_task(variations)
        
        # Should get the successful result despite one failure
        assert result.success is True
        assert result.value == "success"
        assert result.variation_id == "success"
    
    @pytest.mark.asyncio
    async def test_all_tasks_fail(self, manager):
        """Test behavior when all tasks fail."""
        
        def failing_task(error_msg):
            raise ValueError(error_msg)
        
        variations = [
            TaskVariation(id="fail1", task=failing_task, params={"error_msg": "Error 1"}),
            TaskVariation(id="fail2", task=failing_task, params={"error_msg": "Error 2"}),
        ]
        
        result = await manager.execute_quantum_task(variations)
        
        assert result.success is False
        assert result.error is not None
        assert isinstance(result.error, ValueError)
    
    def test_variation_generation(self, manager):
        """Test generation of task variations."""
        
        def base_task(param1, param2="default"):
            return f"{param1}_{param2}"
        
        variation_configs = [
            {"id": "v1", "params": {"param2": "modified1"}},
            {"id": "v2", "params": {"param2": "modified2"}, "weight": 0.8},
            {"id": "v3", "params": {"param1": "changed", "param2": "modified3"}, "priority": 1},
        ]
        
        variations = manager.generate_variations(
            base_task=base_task,
            base_params={"param1": "base"},
            variation_configs=variation_configs
        )
        
        assert len(variations) == 3
        
        # Check first variation
        assert variations[0].id == "v1"
        assert variations[0].params == {"param1": "base", "param2": "modified1"}
        assert variations[0].weight == 1.0
        
        # Check second variation with weight
        assert variations[1].id == "v2"
        assert variations[1].weight == 0.8
        
        # Check third variation with priority
        assert variations[2].id == "v3"
        assert variations[2].params == {"param1": "changed", "param2": "modified3"}
        assert variations[2].priority == 1
    
    def test_metrics_recording(self, manager):
        """Test that metrics are properly recorded."""
        
        # Record some test metrics
        manager._record_metrics(
            strategy=CollapseStrategy.FIRST_SUCCESS,
            variation_count=3,
            execution_time=1.5,
            success=True
        )
        
        metrics = manager.get_metrics()
        
        assert "executions" in metrics
        assert len(metrics["executions"]) == 1
        
        execution = metrics["executions"][0]
        assert execution["strategy"] == "first_success"
        assert execution["variation_count"] == 3
        assert execution["execution_time"] == 1.5
        assert execution["success"] is True
        assert "timestamp" in execution


class TestQuantumTaskDecorator:
    """Test cases for the @quantum_task decorator."""
    
    @pytest.mark.asyncio
    async def test_simple_quantum_task_decorator(self):
        """Test basic usage of @quantum_task decorator without variations."""
        
        @quantum_task()
        def simple_task(x, y):
            return x + y
        
        result = await simple_task(3, 4)
        assert result == 7
    
    @pytest.mark.asyncio
    async def test_quantum_task_with_variations(self):
        """Test @quantum_task decorator with variations."""
        
        @quantum_task(
            variations=[
                {"id": "add", "params": {"operation": "add"}},
                {"id": "multiply", "params": {"operation": "multiply"}},
            ],
            collapse_strategy=CollapseStrategy.FIRST_SUCCESS
        )
        def math_task(x, y, operation="add"):
            if operation == "add":
                return x + y
            elif operation == "multiply":
                return x * y
            else:
                return 0
        
        result = await math_task(3, 4)
        
        # Should get one of the results (add=7, multiply=12)
        assert result in [7, 12]
    
    @pytest.mark.asyncio
    async def test_quantum_task_with_scoring(self):
        """Test @quantum_task decorator with custom scoring function."""
        
        @quantum_task(
            variations=[
                {"id": "short", "params": {"prefix": "Hi"}},
                {"id": "long", "params": {"prefix": "Hello there"}},
                {"id": "medium", "params": {"prefix": "Hello"}},
            ],
            collapse_strategy=CollapseStrategy.BEST_SCORE,
            scoring_fn=lambda x: len(x)  # Prefer longer strings
        )
        def greeting_task(name, prefix="Hi"):
            return f"{prefix}, {name}!"
        
        result = await greeting_task("World")
        
        # Should get the longest result
        assert result == "Hello there, World!"
    
    @pytest.mark.asyncio
    async def test_async_quantum_task_decorator(self):
        """Test @quantum_task decorator with async function."""
        
        @quantum_task(
            variations=[
                {"id": "v1", "params": {"multiplier": 2}},
                {"id": "v2", "params": {"multiplier": 3}},
            ]
        )
        async def async_math_task(value, multiplier=1):
            await asyncio.sleep(0.01)  # Simulate async work
            return value * multiplier
        
        result = await async_math_task(5)
        
        # Should get one of the results (10 or 15)
        assert result in [10, 15]
    
    @pytest.mark.asyncio
    async def test_quantum_task_error_handling(self):
        """Test error handling in @quantum_task decorator."""
        
        @quantum_task(
            variations=[
                {"id": "fail", "params": {"should_fail": True}},
                {"id": "success", "params": {"should_fail": False}},
            ]
        )
        def error_prone_task(value, should_fail=False):
            if should_fail:
                raise ValueError("Intentional failure")
            return value * 2
        
        result = await error_prone_task(5)
        
        # Should get the successful result
        assert result == 10


class TestQuantumBenchmarks:
    """Benchmark tests for quantum execution performance."""
    
    @pytest.mark.asyncio
    async def test_parallel_execution_performance(self):
        """Test that parallel execution is faster than sequential."""
        
        def cpu_intensive_task(duration, result):
            """Simulate CPU-intensive work."""
            end_time = time.time() + duration
            while time.time() < end_time:
                pass  # Busy wait
            return result
        
        manager = QuantumManager(max_workers=3)
        
        # Sequential execution baseline
        start_time = time.time()
        sequential_results = []
        for i in range(3):
            result = cpu_intensive_task(0.1, f"result_{i}")
            sequential_results.append(result)
        sequential_time = time.time() - start_time
        
        # Parallel quantum execution
        variations = [
            TaskVariation(id=f"task_{i}", task=cpu_intensive_task, params={"duration": 0.1, "result": f"result_{i}"})
            for i in range(3)
        ]
        
        start_time = time.time()
        parallel_result = await manager.execute_quantum_task(
            variations, 
            collapse_strategy=CollapseStrategy.FIRST_SUCCESS
        )
        parallel_time = time.time() - start_time
        
        # Parallel should be significantly faster than sequential
        assert parallel_time < sequential_time * 0.8  # At least 20% faster
        assert parallel_result.success is True
    
    @pytest.mark.asyncio 
    async def test_large_variation_count(self):
        """Test quantum execution with many variations."""
        
        def simple_task(task_id, value):
            return f"task_{task_id}_{value}"
        
        manager = QuantumManager(max_workers=8)
        
        # Create many variations
        variations = [
            TaskVariation(
                id=f"variation_{i}",
                task=simple_task,
                params={"task_id": i, "value": i * 2}
            )
            for i in range(20)
        ]
        
        start_time = time.time()
        result = await manager.execute_quantum_task(variations)
        execution_time = time.time() - start_time
        
        assert result.success is True
        assert execution_time < 5.0  # Should complete reasonably quickly
        assert result.value.startswith("task_")
    
    @pytest.mark.asyncio
    async def test_strategy_performance_comparison(self):
        """Compare performance of different collapse strategies."""
        
        def benchmark_task(value, computation_factor=1):
            # Simulate variable computation time
            for _ in range(computation_factor * 1000):
                pass
            return value * computation_factor
        
        manager = QuantumManager(max_workers=4)
        
        variations = [
            TaskVariation(
                id=f"comp_{i}",
                task=benchmark_task,
                params={"value": 10, "computation_factor": i + 1}
            )
            for i in range(4)
        ]
        
        strategies_to_test = [
            CollapseStrategy.FIRST_SUCCESS,
            CollapseStrategy.BEST_SCORE,
            CollapseStrategy.CONSENSUS,
            CollapseStrategy.COMBINED,
        ]
        
        strategy_times = {}
        
        for strategy in strategies_to_test:
            start_time = time.time()
            
            result = await manager.execute_quantum_task(
                variations,
                collapse_strategy=strategy,
                scoring_fn=lambda x: x if isinstance(x, (int, float)) else 0
            )
            
            execution_time = time.time() - start_time
            strategy_times[strategy.value] = execution_time
            
            assert result.success is True
        
        # FIRST_SUCCESS should generally be fastest
        assert strategy_times["first_success"] <= min(strategy_times.values()) * 1.5
        
        # All strategies should complete in reasonable time
        for time_taken in strategy_times.values():
            assert time_taken < 10.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
