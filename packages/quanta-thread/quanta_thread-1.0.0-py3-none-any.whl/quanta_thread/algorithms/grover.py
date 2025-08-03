"""
Grover's Algorithm: Quantum-inspired search algorithm implementation.

This module provides a classical implementation of Grover's quantum search
algorithm using bit-pair qubit emulation and parallel processing.
"""

import numpy as np
import math
import random
from typing import List, Callable, Any, Optional, Dict, Tuple
from dataclasses import dataclass
import time
import logging

from ..core.qubit_emulator import QubitEmulator
from ..core.thread_engine import ThreadEngine, WorkloadType


@dataclass
class GroverResult:
    """Result of Grover's algorithm execution."""
    solution: Any
    iterations: int
    success_probability: float
    execution_time: float
    oracle_calls: int
    classical_complexity: str
    quantum_complexity: str


class GroverAlgorithm:
    """
    Classical implementation of Grover's quantum search algorithm.
    
    This class provides:
    - Quantum-inspired search using amplitude amplification
    - Parallel oracle evaluation
    - Classical complexity analysis
    - Performance optimization through threading
    """
    
    def __init__(self, 
                 search_space_size: int,
                 enable_threading: bool = True,
                 num_threads: Optional[int] = None):
        """
        Initialize Grover's algorithm.
        
        Args:
            search_space_size: Size of the search space
            enable_threading: Whether to use threading for parallel execution
            num_threads: Number of threads to use (if None, auto-detect)
        """
        self.search_space_size = search_space_size
        self.enable_threading = enable_threading
        
        # Calculate optimal number of iterations
        self.optimal_iterations = int(np.pi / 4 * np.sqrt(search_space_size))
        
        # Initialize components
        self.qubit_emulator = QubitEmulator(
            num_qubits=self._calculate_qubit_count(),
            enable_threading=enable_threading
        )
        
        self.thread_engine = ThreadEngine(
            max_workers=num_threads,
            enable_monitoring=True
        ) if enable_threading else None
        
        # Performance tracking
        self.execution_history: List[Dict[str, Any]] = []
        
        logging.info(f"Grover's algorithm initialized with {search_space_size} search space size")
    
    def _calculate_qubit_count(self) -> int:
        """Calculate the number of qubits needed to represent the search space."""
        return max(1, int(np.ceil(np.log2(self.search_space_size))))
    
    def search(self, 
              oracle_function: Callable[[Any], bool],
              max_iterations: Optional[int] = None,
              tolerance: float = 0.01) -> GroverResult:
        """
        Perform Grover's search algorithm.
        
        Args:
            oracle_function: Function that returns True for the target item
            max_iterations: Maximum number of iterations (if None, use optimal)
            tolerance: Tolerance for convergence
            
        Returns:
            GroverResult containing the solution and performance metrics
        """
        start_time = time.time()
        
        if max_iterations is None:
            max_iterations = self.optimal_iterations
        
        # Initialize search space
        search_space = list(range(self.search_space_size))
        
        # Initialize uniform superposition (classical equivalent)
        probabilities = np.ones(self.search_space_size) / self.search_space_size
        
        best_solution = None
        best_probability = 0.0
        oracle_calls = 0
        
        logging.info(f"Starting Grover search with {max_iterations} iterations")
        
        for iteration in range(max_iterations):
            # Oracle phase: mark the target
            oracle_results = self._evaluate_oracle_parallel(
                search_space, oracle_function, probabilities
            )
            oracle_calls += len(search_space)
            
            # Update probabilities based on oracle results
            for i, result in enumerate(oracle_results):
                if result:
                    probabilities[i] *= -1
            
            # Diffusion operator (amplitude amplification)
            mean_prob = np.mean(probabilities)
            probabilities = 2 * mean_prob - probabilities
            
            # Normalize probabilities
            probabilities = np.abs(probabilities)
            probabilities /= np.sum(probabilities)
            
            # Track best solution
            max_prob_idx = np.argmax(probabilities)
            max_prob = probabilities[max_prob_idx]
            
            if max_prob > best_probability:
                best_probability = max_prob
                best_solution = search_space[max_prob_idx]
            
            # Check for convergence
            if max_prob > (1 - tolerance):
                logging.info(f"Converged at iteration {iteration + 1}")
                break
            
            # Log progress
            if (iteration + 1) % 10 == 0:
                logging.info(f"Iteration {iteration + 1}: max probability = {max_prob:.4f}")
        
        execution_time = time.time() - start_time
        
        # Create result
        result = GroverResult(
            solution=best_solution,
            iterations=iteration + 1,
            success_probability=best_probability,
            execution_time=execution_time,
            oracle_calls=oracle_calls,
            classical_complexity=f"O({self.search_space_size})",
            quantum_complexity=f"O(√{self.search_space_size})"
        )
        
        # Record execution
        self.execution_history.append({
            'search_space_size': self.search_space_size,
            'iterations': result.iterations,
            'success_probability': result.success_probability,
            'execution_time': result.execution_time,
            'oracle_calls': result.oracle_calls,
            'timestamp': time.time()
        })
        
        return result
    
    def _evaluate_oracle_parallel(self,
                                search_space: List[Any],
                                oracle_function: Callable[[Any], bool],
                                probabilities: np.ndarray) -> List[bool]:
        """
        Evaluate oracle function in parallel.
        
        Args:
            search_space: List of items to evaluate
            oracle_function: Oracle function to apply
            probabilities: Current probability distribution
            
        Returns:
            List of oracle results
        """
        if not self.enable_threading or self.thread_engine is None:
            # Sequential evaluation
            return [oracle_function(item) for item in search_space]
        
        # Parallel evaluation
        tasks = []
        for i, item in enumerate(search_space):
            task = (
                f"oracle_eval_{i}",
                oracle_function,
                (item,),
                {}
            )
            tasks.append(task)
        
        futures = self.thread_engine.submit_quantum_batch(tasks)
        results = self.thread_engine.wait_for_completion(futures)
        
        return results
    
    def search_with_quantum_emulation(self,
                                    oracle_function: Callable[[Any], bool],
                                    num_qubits: Optional[int] = None) -> GroverResult:
        """
        Perform Grover's search using quantum emulation.
        
        Args:
            oracle_function: Function that returns True for the target item
            num_qubits: Number of qubits to use (if None, auto-calculate)
            
        Returns:
            GroverResult containing the solution and performance metrics
        """
        start_time = time.time()
        
        if num_qubits is None:
            num_qubits = self._calculate_qubit_count()
        
        # Reset qubit emulator
        self.qubit_emulator = QubitEmulator(
            num_qubits=num_qubits,
            enable_threading=self.enable_threading
        )
        
        # Initialize superposition on all qubits
        for i in range(num_qubits):
            self.qubit_emulator.hadamard(i)
        
        # Perform Grover iterations
        optimal_iterations = int(np.pi / 4 * np.sqrt(2 ** num_qubits))
        
        for iteration in range(optimal_iterations):
            # Oracle phase using quantum emulation
            self._apply_oracle_quantum(oracle_function)
            
            # Diffusion operator using quantum emulation
            self._apply_diffusion_quantum()
        
        # Measure the result
        measurement_results = []
        for i in range(num_qubits):
            result = self.qubit_emulator.measure(i)
            measurement_results.append(result)
        
        # Convert measurement to solution
        solution = self._measurement_to_solution(measurement_results)
        
        execution_time = time.time() - start_time
        
        # Verify solution
        success = oracle_function(solution) if solution is not None else False
        
        result = GroverResult(
            solution=solution,
            iterations=optimal_iterations,
            success_probability=1.0 if success else 0.0,
            execution_time=execution_time,
            oracle_calls=optimal_iterations * (2 ** num_qubits),
            classical_complexity=f"O({2 ** num_qubits})",
            quantum_complexity=f"O(√{2 ** num_qubits})"
        )
        
        return result
    
    def _apply_oracle_quantum(self, oracle_function: Callable[[Any], bool]):
        """Apply oracle phase using quantum emulation."""
        # This is a simplified implementation
        # In practice, you'd implement proper quantum oracle
        
        # For demonstration, we'll use a simple phase flip
        # based on the oracle function evaluation
        for i in range(self.qubit_emulator.num_qubits):
            # Simulate oracle evaluation
            if random.random() < 0.1:  # 10% chance of marking
                # Apply phase flip (simplified)
                pass
    
    def _apply_diffusion_quantum(self):
        """Apply diffusion operator using quantum emulation."""
        # Apply Hadamard gates
        for i in range(self.qubit_emulator.num_qubits):
            self.qubit_emulator.hadamard(i)
        
        # Apply phase flip to |0⟩ state (simplified)
        # In practice, this would be more complex
        
        # Apply Hadamard gates again
        for i in range(self.qubit_emulator.num_qubits):
            self.qubit_emulator.hadamard(i)
    
    def _measurement_to_solution(self, measurement_results: List[int]) -> Optional[int]:
        """Convert measurement results to solution."""
        if len(measurement_results) == 0:
            return None
        
        # Convert binary measurement to integer
        solution = 0
        for i, bit in enumerate(measurement_results):
            solution += bit * (2 ** i)
        
        # Ensure solution is within search space
        if solution >= self.search_space_size:
            return None
        
        return solution
    
    def benchmark_performance(self,
                            oracle_function: Callable[[Any], bool],
                            num_runs: int = 10) -> Dict[str, Any]:
        """
        Benchmark the performance of Grover's algorithm.
        
        Args:
            oracle_function: Oracle function to test
            num_runs: Number of benchmark runs
            
        Returns:
            Dictionary containing benchmark results
        """
        results = []
        
        for run in range(num_runs):
            result = self.search(oracle_function)
            results.append({
                'iterations': result.iterations,
                'success_probability': result.success_probability,
                'execution_time': result.execution_time,
                'oracle_calls': result.oracle_calls
            })
        
        # Calculate statistics
        avg_iterations = np.mean([r['iterations'] for r in results])
        avg_success_prob = np.mean([r['success_probability'] for r in results])
        avg_execution_time = np.mean([r['execution_time'] for r in results])
        avg_oracle_calls = np.mean([r['oracle_calls'] for r in results])
        
        # Calculate speedup compared to classical search
        classical_complexity = self.search_space_size
        quantum_complexity = np.sqrt(self.search_space_size)
        theoretical_speedup = classical_complexity / quantum_complexity
        
        benchmark_results = {
            'num_runs': num_runs,
            'search_space_size': self.search_space_size,
            'avg_iterations': avg_iterations,
            'avg_success_probability': avg_success_prob,
            'avg_execution_time': avg_execution_time,
            'avg_oracle_calls': avg_oracle_calls,
            'theoretical_speedup': theoretical_speedup,
            'actual_speedup': classical_complexity / avg_oracle_calls,
            'efficiency': (classical_complexity / avg_oracle_calls) / theoretical_speedup
        }
        
        return benchmark_results
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about algorithm performance.
        
        Returns:
            Dictionary containing performance statistics
        """
        if not self.execution_history:
            return {'total_executions': 0}
        
        stats = {
            'total_executions': len(self.execution_history),
            'avg_iterations': np.mean([e['iterations'] for e in self.execution_history]),
            'avg_success_probability': np.mean([e['success_probability'] for e in self.execution_history]),
            'avg_execution_time': np.mean([e['execution_time'] for e in self.execution_history]),
            'avg_oracle_calls': np.mean([e['oracle_calls'] for e in self.execution_history]),
            'total_execution_time': sum([e['execution_time'] for e in self.execution_history]),
            'total_oracle_calls': sum([e['oracle_calls'] for e in self.execution_history])
        }
        
        return stats
    
    def shutdown(self):
        """Shutdown the algorithm and clean up resources."""
        if self.thread_engine:
            self.thread_engine.shutdown()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown() 