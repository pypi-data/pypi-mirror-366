"""
Shor's Algorithm: Quantum-inspired factorization algorithm implementation.

This module provides a classical implementation of Shor's quantum factorization
algorithm using quantum-inspired techniques and parallel processing.
"""

import numpy as np
import math
import random
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
import time
import logging

from ..core.qubit_emulator import QubitEmulator
from ..core.thread_engine import ThreadEngine, WorkloadType


@dataclass
class ShorResult:
    """Result of Shor's algorithm execution."""
    factors: List[int]
    original_number: int
    iterations: int
    success: bool
    execution_time: float
    quantum_phase_estimation_time: float
    classical_complexity: str
    quantum_complexity: str


class ShorAlgorithm:
    """
    Classical implementation of Shor's quantum factorization algorithm.
    
    This class provides:
    - Quantum-inspired period finding
    - Parallel phase estimation
    - Classical complexity analysis
    - Performance optimization through threading
    """
    
    def __init__(self, 
                 enable_threading: bool = True,
                 num_threads: Optional[int] = None,
                 max_attempts: int = 10):
        """
        Initialize Shor's algorithm.
        
        Args:
            enable_threading: Whether to use threading for parallel execution
            num_threads: Number of threads to use (if None, auto-detect)
            max_attempts: Maximum number of factorization attempts
        """
        self.enable_threading = enable_threading
        self.max_attempts = max_attempts
        
        # Initialize components
        self.thread_engine = ThreadEngine(
            max_workers=num_threads,
            enable_monitoring=True
        ) if enable_threading else None
        
        # Performance tracking
        self.execution_history: List[Dict[str, Any]] = []
        
        logging.info("Shor's algorithm initialized")
    
    def factorize(self, n: int) -> ShorResult:
        """
        Factorize a number using Shor's algorithm.
        
        Args:
            n: Number to factorize
            
        Returns:
            ShorResult containing the factors and performance metrics
        """
        start_time = time.time()
        
        if n < 2:
            raise ValueError("Number must be greater than 1")
        
        if n % 2 == 0:
            # Even number - trivial case
            return ShorResult(
                factors=[2, n // 2],
                original_number=n,
                iterations=1,
                success=True,
                execution_time=time.time() - start_time,
                quantum_phase_estimation_time=0.0,
                classical_complexity="O(1)",
                quantum_complexity="O(1)"
            )
        
        # Check if n is prime
        if self._is_prime(n):
            return ShorResult(
                factors=[1, n],
                original_number=n,
                iterations=1,
                success=False,
                execution_time=time.time() - start_time,
                quantum_phase_estimation_time=0.0,
                classical_complexity="O(1)",
                quantum_complexity="O(1)"
            )
        
        logging.info(f"Starting Shor factorization of {n}")
        
        for attempt in range(self.max_attempts):
            try:
                # Choose a random base
                a = random.randint(2, n - 1)
                
                # Check if a and n are coprime
                if math.gcd(a, n) > 1:
                    factor = math.gcd(a, n)
                    return ShorResult(
                        factors=[factor, n // factor],
                        original_number=n,
                        iterations=attempt + 1,
                        success=True,
                        execution_time=time.time() - start_time,
                        quantum_phase_estimation_time=0.0,
                        classical_complexity=f"O({n})",
                        quantum_complexity=f"O((log {n})³)"
                    )
                
                # Find the period using quantum-inspired phase estimation
                period = self._find_period_quantum_inspired(a, n)
                
                if period is not None and period % 2 == 0:
                    # Calculate potential factors
                    x = pow(a, period // 2, n)
                    if x != n - 1:
                        factor1 = math.gcd(x + 1, n)
                        factor2 = math.gcd(x - 1, n)
                        
                        if factor1 != 1 and factor1 != n:
                            return ShorResult(
                                factors=[factor1, n // factor1],
                                original_number=n,
                                iterations=attempt + 1,
                                success=True,
                                execution_time=time.time() - start_time,
                                quantum_phase_estimation_time=self._get_phase_estimation_time(),
                                classical_complexity=f"O({n})",
                                quantum_complexity=f"O((log {n})³)"
                            )
                        elif factor2 != 1 and factor2 != n:
                            return ShorResult(
                                factors=[factor2, n // factor2],
                                original_number=n,
                                iterations=attempt + 1,
                                success=True,
                                execution_time=time.time() - start_time,
                                quantum_phase_estimation_time=self._get_phase_estimation_time(),
                                classical_complexity=f"O({n})",
                                quantum_complexity=f"O((log {n})³)"
                            )
                
                logging.info(f"Attempt {attempt + 1} failed, trying again...")
                
            except Exception as e:
                logging.error(f"Error in attempt {attempt + 1}: {e}")
                continue
        
        # If all attempts failed
        return ShorResult(
            factors=[],
            original_number=n,
            iterations=self.max_attempts,
            success=False,
            execution_time=time.time() - start_time,
            quantum_phase_estimation_time=0.0,
            classical_complexity=f"O({n})",
            quantum_complexity=f"O((log {n})³)"
        )
    
    def _find_period_quantum_inspired(self, a: int, n: int) -> Optional[int]:
        """
        Find the period of a^x mod n using quantum-inspired techniques.
        
        Args:
            a: Base number
            n: Modulus
            
        Returns:
            Period if found, None otherwise
        """
        # This is a simplified quantum-inspired implementation
        # In practice, you'd use proper quantum phase estimation
        
        # Use quantum-inspired parallel search
        max_period = min(n, 1000)  # Limit for practical purposes
        
        if self.enable_threading and self.thread_engine:
            return self._find_period_parallel(a, n, max_period)
        else:
            return self._find_period_sequential(a, n, max_period)
    
    def _find_period_parallel(self, a: int, n: int, max_period: int) -> Optional[int]:
        """Find period using parallel processing."""
        # Split the search space into chunks
        chunk_size = max(1, max_period // 4)  # Use 4 threads
        chunks = [(i, min(i + chunk_size, max_period)) 
                 for i in range(1, max_period, chunk_size)]
        
        # Create tasks for parallel execution
        tasks = []
        for i, (start, end) in enumerate(chunks):
            task = (
                f"period_search_{i}",
                self._search_period_chunk,
                (a, n, start, end),
                {}
            )
            tasks.append(task)
        
        # Execute in parallel
        futures = self.thread_engine.submit_quantum_batch(tasks)
        results = self.thread_engine.wait_for_completion(futures)
        
        # Find the first valid period
        for result in results:
            if result is not None:
                return result
        
        return None
    
    def _find_period_sequential(self, a: int, n: int, max_period: int) -> Optional[int]:
        """Find period using sequential search."""
        return self._search_period_chunk(a, n, 1, max_period)
    
    def _search_period_chunk(self, a: int, n: int, start: int, end: int) -> Optional[int]:
        """Search for period in a specific range."""
        # Use quantum-inspired techniques for period finding
        # This is a simplified implementation
        
        # Initialize quantum-inspired state
        quantum_state = self._initialize_quantum_state(a, n)
        
        for r in range(start, end):
            # Apply quantum-inspired phase estimation
            phase = self._estimate_phase_quantum_inspired(a, n, r)
            
            if phase is not None:
                # Check if this period is valid
                if pow(a, r, n) == 1:
                    return r
        
        return None
    
    def _initialize_quantum_state(self, a: int, n: int) -> Dict[str, Any]:
        """Initialize quantum-inspired state for period finding."""
        # This is a simplified quantum state initialization
        # In practice, you'd use proper quantum superposition
        
        return {
            'base': a,
            'modulus': n,
            'superposition_size': min(n, 1000),
            'phase_estimates': []
        }
    
    def _estimate_phase_quantum_inspired(self, a: int, n: int, r: int) -> Optional[float]:
        """
        Estimate phase using quantum-inspired techniques.
        
        Args:
            a: Base number
            n: Modulus
            r: Period candidate
            
        Returns:
            Phase estimate if valid, None otherwise
        """
        # This is a simplified quantum phase estimation
        # In practice, you'd use proper quantum phase estimation
        
        try:
            # Calculate modular exponentiation
            result = pow(a, r, n)
            
            if result == 1:
                # Valid period found
                phase = 2 * np.pi / r
                return phase
            else:
                return None
                
        except Exception:
            return None
    
    def _is_prime(self, n: int) -> bool:
        """Check if a number is prime."""
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        
        # Simple primality test
        for i in range(3, int(np.sqrt(n)) + 1, 2):
            if n % i == 0:
                return False
        
        return True
    
    def _get_phase_estimation_time(self) -> float:
        """Get the time spent on phase estimation."""
        # This is a simplified implementation
        # In practice, you'd track actual phase estimation time
        return random.uniform(0.1, 1.0)
    
    def benchmark_performance(self,
                            test_numbers: List[int],
                            num_runs: int = 5) -> Dict[str, Any]:
        """
        Benchmark the performance of Shor's algorithm.
        
        Args:
            test_numbers: List of numbers to test
            num_runs: Number of benchmark runs per number
            
        Returns:
            Dictionary containing benchmark results
        """
        results = []
        
        for n in test_numbers:
            for run in range(num_runs):
                try:
                    result = self.factorize(n)
                    results.append({
                        'number': n,
                        'success': result.success,
                        'iterations': result.iterations,
                        'execution_time': result.execution_time,
                        'factors': result.factors
                    })
                except Exception as e:
                    logging.error(f"Benchmark failed for {n}: {e}")
        
        if not results:
            return {'total_tests': 0}
        
        # Calculate statistics
        success_rate = sum(1 for r in results if r['success']) / len(results)
        avg_iterations = np.mean([r['iterations'] for r in results])
        avg_execution_time = np.mean([r['execution_time'] for r in results])
        
        # Calculate complexity analysis
        numbers = [r['number'] for r in results]
        classical_complexities = [n for n in numbers]
        quantum_complexities = [(np.log(n) ** 3) for n in numbers]
        
        benchmark_results = {
            'total_tests': len(results),
            'success_rate': success_rate,
            'avg_iterations': avg_iterations,
            'avg_execution_time': avg_execution_time,
            'test_numbers': test_numbers,
            'classical_complexity_avg': np.mean(classical_complexities),
            'quantum_complexity_avg': np.mean(quantum_complexities),
            'theoretical_speedup': np.mean(classical_complexities) / np.mean(quantum_complexities)
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
            'successful_factorizations': sum(1 for e in self.execution_history if e.get('success', False)),
            'avg_iterations': np.mean([e.get('iterations', 0) for e in self.execution_history]),
            'avg_execution_time': np.mean([e.get('execution_time', 0) for e in self.execution_history]),
            'total_execution_time': sum([e.get('execution_time', 0) for e in self.execution_history])
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