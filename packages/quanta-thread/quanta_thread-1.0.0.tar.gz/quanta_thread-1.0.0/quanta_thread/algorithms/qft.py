"""
Quantum Fourier Transform: Quantum-inspired FFT implementation.

This module provides a classical implementation of the Quantum Fourier Transform
using quantum-inspired techniques and parallel processing.
"""

import numpy as np
import math
from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass
import time
import logging

from ..core.qubit_emulator import QubitEmulator
from ..core.thread_engine import ThreadEngine, WorkloadType


@dataclass
class QFTResult:
    """Result of QFT algorithm execution."""
    transformed_vector: np.ndarray
    original_vector: np.ndarray
    execution_time: float
    num_qubits: int
    classical_complexity: str
    quantum_complexity: str
    reconstruction_error: float


class QFTAlgorithm:
    """
    Classical implementation of the Quantum Fourier Transform.
    
    This class provides:
    - Quantum-inspired FFT using bit-pair qubit emulation
    - Parallel phase estimation
    - Classical complexity analysis
    - Performance optimization through threading
    """
    
    def __init__(self, 
                 enable_threading: bool = True,
                 num_threads: Optional[int] = None):
        """
        Initialize QFT algorithm.
        
        Args:
            enable_threading: Whether to use threading for parallel execution
            num_threads: Number of threads to use (if None, auto-detect)
        """
        self.enable_threading = enable_threading
        
        # Initialize components
        self.thread_engine = ThreadEngine(
            max_workers=num_threads,
            enable_monitoring=True
        ) if enable_threading else None
        
        # Performance tracking
        self.execution_history: List[Dict[str, Any]] = []
        
        logging.info("QFT algorithm initialized")
    
    def transform(self, 
                 vector: Union[List[complex], np.ndarray],
                 use_quantum_emulation: bool = True) -> QFTResult:
        """
        Apply Quantum Fourier Transform to a vector.
        
        Args:
            vector: Input vector (can be complex)
            use_quantum_emulation: Whether to use quantum emulation
            
        Returns:
            QFTResult containing the transformed vector and performance metrics
        """
        start_time = time.time()
        
        # Convert to numpy array
        vector = np.array(vector, dtype=complex)
        n = len(vector)
        
        # Calculate number of qubits needed
        num_qubits = int(np.ceil(np.log2(n)))
        
        if use_quantum_emulation:
            result_vector = self._quantum_inspired_qft(vector, num_qubits)
        else:
            result_vector = self._classical_qft(vector)
        
        execution_time = time.time() - start_time
        
        # Calculate reconstruction error
        inverse_result = self._inverse_qft(result_vector)
        reconstruction_error = np.mean(np.abs(vector - inverse_result))
        
        # Create result
        result = QFTResult(
            transformed_vector=result_vector,
            original_vector=vector,
            execution_time=execution_time,
            num_qubits=num_qubits,
            classical_complexity=f"O({n} log {n})",
            quantum_complexity=f"O((log {n})²)",
            reconstruction_error=reconstruction_error
        )
        
        # Record execution
        self.execution_history.append({
            'vector_size': n,
            'num_qubits': num_qubits,
            'execution_time': execution_time,
            'reconstruction_error': reconstruction_error,
            'use_quantum_emulation': use_quantum_emulation,
            'timestamp': time.time()
        })
        
        return result
    
    def _quantum_inspired_qft(self, vector: np.ndarray, num_qubits: int) -> np.ndarray:
        """
        Apply quantum-inspired QFT.
        
        Args:
            vector: Input vector
            num_qubits: Number of qubits
            
        Returns:
            Transformed vector
        """
        n = len(vector)
        
        # Pad vector to power of 2 if necessary
        target_size = 2 ** num_qubits
        if n < target_size:
            padded_vector = np.zeros(target_size, dtype=complex)
            padded_vector[:n] = vector
            vector = padded_vector
            n = target_size
        
        # Initialize qubit emulator
        qubit_emulator = QubitEmulator(
            num_qubits=num_qubits,
            enable_threading=self.enable_threading
        )
        
        # Apply quantum-inspired QFT
        result = self._apply_qft_quantum_inspired(vector, qubit_emulator)
        
        return result
    
    def _apply_qft_quantum_inspired(self, 
                                  vector: np.ndarray, 
                                  qubit_emulator: QubitEmulator) -> np.ndarray:
        """
        Apply QFT using quantum-inspired techniques.
        
        Args:
            vector: Input vector
            qubit_emulator: Qubit emulator instance
            
        Returns:
            Transformed vector
        """
        n = len(vector)
        num_qubits = qubit_emulator.num_qubits
        
        # Initialize quantum state
        quantum_state = self._initialize_quantum_state(vector, qubit_emulator)
        
        # Apply QFT using quantum-inspired techniques
        transformed_state = self._apply_qft_gates(quantum_state, qubit_emulator)
        
        # Convert back to classical vector
        result_vector = self._quantum_state_to_vector(transformed_state, n)
        
        return result_vector
    
    def _initialize_quantum_state(self, 
                                vector: np.ndarray, 
                                qubit_emulator: QubitEmulator) -> Dict[str, Any]:
        """
        Initialize quantum state from classical vector.
        
        Args:
            vector: Classical vector
            qubit_emulator: Qubit emulator
            
        Returns:
            Quantum state representation
        """
        n = len(vector)
        
        # Normalize vector
        norm = np.linalg.norm(vector)
        if norm > 0:
            normalized_vector = vector / norm
        else:
            normalized_vector = vector
        
        # Create quantum state representation
        quantum_state = {
            'amplitudes': normalized_vector,
            'num_qubits': qubit_emulator.num_qubits,
            'size': n,
            'phases': np.angle(normalized_vector),
            'magnitudes': np.abs(normalized_vector)
        }
        
        return quantum_state
    
    def _apply_qft_gates(self, 
                        quantum_state: Dict[str, Any], 
                        qubit_emulator: QubitEmulator) -> Dict[str, Any]:
        """
        Apply QFT gates to quantum state.
        
        Args:
            quantum_state: Quantum state
            qubit_emulator: Qubit emulator
            
        Returns:
            Transformed quantum state
        """
        num_qubits = qubit_emulator.num_qubits
        amplitudes = quantum_state['amplitudes'].copy()
        
        # Apply QFT using quantum-inspired techniques
        for i in range(num_qubits):
            # Apply Hadamard gate to qubit i
            amplitudes = self._apply_hadamard_gate(amplitudes, i, num_qubits)
            
            # Apply controlled phase gates
            for j in range(i + 1, num_qubits):
                phase = 2 * np.pi / (2 ** (j - i + 1))
                amplitudes = self._apply_controlled_phase_gate(amplitudes, i, j, phase, num_qubits)
        
        # Swap qubits (reverse order)
        amplitudes = self._swap_qubits(amplitudes, num_qubits)
        
        # Update quantum state
        quantum_state['amplitudes'] = amplitudes
        quantum_state['phases'] = np.angle(amplitudes)
        quantum_state['magnitudes'] = np.abs(amplitudes)
        
        return quantum_state
    
    def _apply_hadamard_gate(self, 
                           amplitudes: np.ndarray, 
                           qubit: int, 
                           num_qubits: int) -> np.ndarray:
        """
        Apply Hadamard gate to a qubit.
        
        Args:
            amplitudes: Amplitude vector
            qubit: Qubit index
            num_qubits: Number of qubits
            
        Returns:
            Updated amplitude vector
        """
        new_amplitudes = amplitudes.copy()
        n = len(amplitudes)
        
        # Apply Hadamard transformation
        for i in range(n):
            # Check if qubit is set in state i
            if (i >> qubit) & 1:
                # Qubit is 1 - apply Hadamard transformation
                # Find the state with qubit set to 0
                j = i & ~(1 << qubit)
                
                # Hadamard transformation: |1⟩ → (|0⟩ - |1⟩)/√2
                new_amplitudes[i] = (amplitudes[j] - amplitudes[i]) / np.sqrt(2)
                new_amplitudes[j] = (amplitudes[j] + amplitudes[i]) / np.sqrt(2)
        
        return new_amplitudes
    
    def _apply_controlled_phase_gate(self, 
                                   amplitudes: np.ndarray, 
                                   control: int, 
                                   target: int, 
                                   phase: float, 
                                   num_qubits: int) -> np.ndarray:
        """
        Apply controlled phase gate.
        
        Args:
            amplitudes: Amplitude vector
            control: Control qubit
            target: Target qubit
            phase: Phase angle
            num_qubits: Number of qubits
            
        Returns:
            Updated amplitude vector
        """
        new_amplitudes = amplitudes.copy()
        n = len(amplitudes)
        
        # Apply controlled phase gate
        for i in range(n):
            # Check if both control and target qubits are set
            if ((i >> control) & 1) and ((i >> target) & 1):
                new_amplitudes[i] *= np.exp(1j * phase)
        
        return new_amplitudes
    
    def _swap_qubits(self, amplitudes: np.ndarray, num_qubits: int) -> np.ndarray:
        """
        Swap qubits to reverse order.
        
        Args:
            amplitudes: Amplitude vector
            num_qubits: Number of qubits
            
        Returns:
            Updated amplitude vector
        """
        new_amplitudes = np.zeros_like(amplitudes)
        n = len(amplitudes)
        
        for i in range(n):
            # Reverse the bit order
            reversed_i = 0
            for j in range(num_qubits):
                reversed_i |= ((i >> j) & 1) << (num_qubits - 1 - j)
            
            new_amplitudes[reversed_i] = amplitudes[i]
        
        return new_amplitudes
    
    def _quantum_state_to_vector(self, 
                               quantum_state: Dict[str, Any], 
                               size: int) -> np.ndarray:
        """
        Convert quantum state back to classical vector.
        
        Args:
            quantum_state: Quantum state
            size: Size of output vector
            
        Returns:
            Classical vector
        """
        amplitudes = quantum_state['amplitudes']
        
        # Take the first 'size' elements
        result = amplitudes[:size]
        
        # Normalize
        norm = np.linalg.norm(result)
        if norm > 0:
            result = result / norm
        
        return result
    
    def _classical_qft(self, vector: np.ndarray) -> np.ndarray:
        """
        Apply classical FFT (for comparison).
        
        Args:
            vector: Input vector
            
        Returns:
            Transformed vector
        """
        # Use numpy's FFT
        result = np.fft.fft(vector)
        
        # Normalize (quantum-inspired)
        result = result / np.sqrt(len(vector))
        
        return result
    
    def _inverse_qft(self, vector: np.ndarray) -> np.ndarray:
        """
        Apply inverse QFT.
        
        Args:
            vector: Input vector
            
        Returns:
            Inverse transformed vector
        """
        # Use numpy's inverse FFT
        result = np.fft.ifft(vector)
        
        # Normalize
        result = result * np.sqrt(len(vector))
        
        return result
    
    def benchmark_performance(self,
                            test_sizes: List[int],
                            num_runs: int = 5) -> Dict[str, Any]:
        """
        Benchmark the performance of QFT algorithm.
        
        Args:
            test_sizes: List of vector sizes to test
            num_runs: Number of benchmark runs per size
            
        Returns:
            Dictionary containing benchmark results
        """
        results = []
        
        for size in test_sizes:
            for run in range(num_runs):
                # Generate random test vector
                test_vector = np.random.random(size) + 1j * np.random.random(size)
                
                # Test quantum-inspired QFT
                qft_result = self.transform(test_vector, use_quantum_emulation=True)
                
                # Test classical FFT for comparison
                classical_start = time.time()
                classical_result = np.fft.fft(test_vector)
                classical_time = time.time() - classical_start
                
                results.append({
                    'size': size,
                    'quantum_time': qft_result.execution_time,
                    'classical_time': classical_time,
                    'reconstruction_error': qft_result.reconstruction_error,
                    'speedup': classical_time / qft_result.execution_time if qft_result.execution_time > 0 else 0
                })
        
        if not results:
            return {'total_tests': 0}
        
        # Calculate statistics
        avg_quantum_time = np.mean([r['quantum_time'] for r in results])
        avg_classical_time = np.mean([r['classical_time'] for r in results])
        avg_speedup = np.mean([r['speedup'] for r in results])
        avg_reconstruction_error = np.mean([r['reconstruction_error'] for r in results])
        
        benchmark_results = {
            'total_tests': len(results),
            'test_sizes': test_sizes,
            'avg_quantum_time': avg_quantum_time,
            'avg_classical_time': avg_classical_time,
            'avg_speedup': avg_speedup,
            'avg_reconstruction_error': avg_reconstruction_error,
            'theoretical_speedup': np.mean([np.log2(size) for size in test_sizes])
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
            'avg_vector_size': np.mean([e.get('vector_size', 0) for e in self.execution_history]),
            'avg_num_qubits': np.mean([e.get('num_qubits', 0) for e in self.execution_history]),
            'avg_execution_time': np.mean([e.get('execution_time', 0) for e in self.execution_history]),
            'avg_reconstruction_error': np.mean([e.get('reconstruction_error', 0) for e in self.execution_history]),
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