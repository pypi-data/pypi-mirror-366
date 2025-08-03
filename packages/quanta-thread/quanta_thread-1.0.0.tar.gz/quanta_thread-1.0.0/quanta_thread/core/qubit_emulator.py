"""
Qubit Emulator: Classical bit-pair implementation of quantum qubits.

This module emulates quantum qubits using classical computing resources,
specifically using 2 classical bits per qubit to simulate superposition,
entanglement, and quantum interference.
"""

import numpy as np
import threading
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import math
import random


class QubitState(Enum):
    """Enumeration of possible qubit states."""
    ZERO = 0
    ONE = 1
    SUPERPOSITION = 2
    ENTANGLED = 3


@dataclass
class QubitPair:
    """Represents a pair of classical bits emulating a quantum qubit."""
    bit1: bool
    bit2: bool
    state: QubitState
    phase: float = 0.0
    amplitude: float = 1.0
    
    def __post_init__(self):
        if self.amplitude <= 0:
            raise ValueError("Amplitude must be positive")
        if not 0 <= self.phase <= 2 * math.pi:
            self.phase = self.phase % (2 * math.pi)


class QubitEmulator:
    """
    Emulates quantum qubits using classical bit-pairs and threading.
    
    This class provides quantum-like behavior including:
    - Superposition states using bit-pair combinations
    - Entanglement simulation through shared state
    - Quantum interference patterns
    - Measurement collapse simulation
    """
    
    def __init__(self, num_qubits: int = 1, enable_threading: bool = True):
        """
        Initialize the qubit emulator.
        
        Args:
            num_qubits: Number of qubits to emulate
            enable_threading: Whether to use threading for parallel operations
        """
        self.num_qubits = num_qubits
        self.enable_threading = enable_threading
        self.qubits: List[QubitPair] = []
        self.entanglement_map: Dict[int, List[int]] = {}
        self.measurement_history: List[Dict[str, Any]] = []
        self._lock = threading.Lock() if enable_threading else None
        
        # Initialize qubits in |0⟩ state
        self._initialize_qubits()
    
    def _initialize_qubits(self):
        """Initialize all qubits in the |0⟩ state."""
        for i in range(self.num_qubits):
            qubit = QubitPair(
                bit1=False,
                bit2=False,
                state=QubitState.ZERO,
                phase=0.0,
                amplitude=1.0
            )
            self.qubits.append(qubit)
    
    def initialize_state(self, state_vector: List[float]) -> None:
        """
        Initialize qubits with a specific state vector.
        
        Args:
            state_vector: List of amplitudes for each basis state
        """
        if len(state_vector) != 2 ** self.num_qubits:
            raise ValueError(f"State vector length must be 2^{self.num_qubits} = {2 ** self.num_qubits}")
        
        # Normalize the state vector
        norm = math.sqrt(sum(abs(amp) ** 2 for amp in state_vector))
        if norm == 0:
            raise ValueError("State vector cannot be zero")
        
        normalized_vector = [amp / norm for amp in state_vector]
        
        if self._lock:
            with self._lock:
                self._set_state_vector(normalized_vector)
        else:
            self._set_state_vector(normalized_vector)
    
    def _set_state_vector(self, state_vector: List[float]) -> None:
        """Internal method to set the state vector."""
        # For simplicity, we'll set the first qubit based on the first two amplitudes
        if len(state_vector) >= 2:
            # Set first qubit based on |0⟩ and |1⟩ amplitudes
            amp_0 = abs(state_vector[0])
            amp_1 = abs(state_vector[1])
            
            if amp_0 > 0.5:
                self.qubits[0].state = QubitState.ZERO
                self.qubits[0].amplitude = amp_0
            elif amp_1 > 0.5:
                self.qubits[0].state = QubitState.ONE
                self.qubits[0].amplitude = amp_1
            else:
                self.qubits[0].state = QubitState.SUPERPOSITION
                self.qubits[0].amplitude = math.sqrt(amp_0**2 + amp_1**2)
    
    def hadamard(self, qubit_index: int) -> None:
        """
        Apply Hadamard gate to create superposition.
        
        Args:
            qubit_index: Index of the qubit to apply the gate to
        """
        if not 0 <= qubit_index < self.num_qubits:
            raise ValueError(f"Invalid qubit index: {qubit_index}")
        
        if self._lock:
            with self._lock:
                self._apply_hadamard(qubit_index)
        else:
            self._apply_hadamard(qubit_index)
    
    def _apply_hadamard(self, qubit_index: int):
        """Internal Hadamard gate implementation."""
        qubit = self.qubits[qubit_index]
        
        # Simulate superposition using bit-pair combinations
        if qubit.state == QubitState.ZERO:
            # |0⟩ → (|0⟩ + |1⟩)/√2
            qubit.bit1 = random.choice([True, False])
            qubit.bit2 = not qubit.bit1
            qubit.state = QubitState.SUPERPOSITION
            qubit.amplitude = 1.0 / math.sqrt(2)
        elif qubit.state == QubitState.ONE:
            # |1⟩ → (|0⟩ - |1⟩)/√2
            qubit.bit1 = random.choice([True, False])
            qubit.bit2 = not qubit.bit1
            qubit.state = QubitState.SUPERPOSITION
            qubit.phase = math.pi
            qubit.amplitude = 1.0 / math.sqrt(2)
        else:
            # Already in superposition, apply phase shift
            qubit.phase = (qubit.phase + math.pi) % (2 * math.pi)
    
    def cnot(self, control_qubit: int, target_qubit: int) -> None:
        """
        Apply CNOT gate to create entanglement.
        
        Args:
            control_qubit: Index of the control qubit
            target_qubit: Index of the target qubit
        """
        if not (0 <= control_qubit < self.num_qubits and 
                0 <= target_qubit < self.num_qubits):
            raise ValueError("Invalid qubit indices")
        
        if self._lock:
            with self._lock:
                self._apply_cnot(control_qubit, target_qubit)
        else:
            self._apply_cnot(control_qubit, target_qubit)
    
    def _apply_cnot(self, control_qubit: int, target_qubit: int):
        """Internal CNOT gate implementation."""
        control = self.qubits[control_qubit]
        target = self.qubits[target_qubit]
        
        # Create entanglement
        if control.state in [QubitState.ONE, QubitState.SUPERPOSITION]:
            # Flip target qubit if control is |1⟩
            target.bit1 = not target.bit1
            target.bit2 = not target.bit2
            
            # Mark as entangled
            control.state = QubitState.ENTANGLED
            target.state = QubitState.ENTANGLED
            
            # Update entanglement map
            if control_qubit not in self.entanglement_map:
                self.entanglement_map[control_qubit] = []
            if target_qubit not in self.entanglement_map:
                self.entanglement_map[target_qubit] = []
            
            self.entanglement_map[control_qubit].append(target_qubit)
            self.entanglement_map[target_qubit].append(control_qubit)
    
    def measure(self, qubit_index: int) -> int:
        """
        Measure a qubit, collapsing its state.
        
        Args:
            qubit_index: Index of the qubit to measure
            
        Returns:
            Measurement result (0 or 1)
        """
        if not 0 <= qubit_index < self.num_qubits:
            raise ValueError(f"Invalid qubit index: {qubit_index}")
        
        if self._lock:
            with self._lock:
                return self._perform_measurement(qubit_index)
        else:
            return self._perform_measurement(qubit_index)
    
    def _perform_measurement(self, qubit_index: int) -> int:
        """Internal measurement implementation."""
        qubit = self.qubits[qubit_index]
        
        # Record measurement
        measurement = {
            'qubit_index': qubit_index,
            'previous_state': qubit.state,
            'amplitude': qubit.amplitude,
            'phase': qubit.phase
        }
        
        if qubit.state == QubitState.SUPERPOSITION:
            # Collapse superposition based on amplitude
            prob_zero = qubit.amplitude ** 2
            result = 0 if random.random() < prob_zero else 1
            
            # Collapse to definite state
            qubit.bit1 = (result == 1)
            qubit.bit2 = (result == 1)
            qubit.state = QubitState.ZERO if result == 0 else QubitState.ONE
            qubit.phase = 0.0
            qubit.amplitude = 1.0
            
            measurement['result'] = result
            measurement['collapsed'] = True
        else:
            # Already in definite state
            result = 1 if qubit.bit1 else 0
            measurement['result'] = result
            measurement['collapsed'] = False
        
        self.measurement_history.append(measurement)
        return result
    
    def get_state_vector(self) -> np.ndarray:
        """
        Get the current state vector representation.
        
        Returns:
            State vector as numpy array
        """
        if self._lock:
            with self._lock:
                return self._compute_state_vector()
        else:
            return self._compute_state_vector()
    
    def _compute_state_vector(self) -> np.ndarray:
        """Compute the current state vector."""
        # For n qubits, we need 2^n complex amplitudes
        vector_size = 2 ** self.num_qubits
        state_vector = np.zeros(vector_size, dtype=complex)
        
        # Compute amplitudes based on current qubit states
        for i in range(vector_size):
            amplitude = 1.0
            phase = 0.0
            
            for j in range(self.num_qubits):
                qubit = self.qubits[j]
                bit_value = (i >> j) & 1
                
                if qubit.state == QubitState.SUPERPOSITION:
                    # Superposition contributes to multiple basis states
                    if bit_value == 0:
                        amplitude *= qubit.amplitude
                    else:
                        amplitude *= qubit.amplitude
                        phase += qubit.phase
                elif qubit.state == QubitState.ZERO:
                    if bit_value != 0:
                        amplitude = 0.0
                        break
                elif qubit.state == QubitState.ONE:
                    if bit_value != 1:
                        amplitude = 0.0
                        break
            
            if amplitude > 0:
                state_vector[i] = amplitude * np.exp(1j * phase)
        
        return state_vector
    
    def reset(self, qubit_index: Optional[int] = None) -> None:
        """
        Reset qubit(s) to |0⟩ state.
        
        Args:
            qubit_index: Specific qubit to reset, or None for all
        """
        if self._lock:
            with self._lock:
                self._reset_qubits(qubit_index)
        else:
            self._reset_qubits(qubit_index)
    
    def _reset_qubits(self, qubit_index: Optional[int] = None):
        """Internal reset implementation."""
        if qubit_index is None:
            # Reset all qubits
            for i in range(self.num_qubits):
                self.qubits[i] = QubitPair(
                    bit1=False, bit2=False,
                    state=QubitState.ZERO,
                    phase=0.0, amplitude=1.0
                )
            self.entanglement_map.clear()
        else:
            # Reset specific qubit
            if 0 <= qubit_index < self.num_qubits:
                self.qubits[qubit_index] = QubitPair(
                    bit1=False, bit2=False,
                    state=QubitState.ZERO,
                    phase=0.0, amplitude=1.0
                )
                # Remove from entanglement map
                if qubit_index in self.entanglement_map:
                    del self.entanglement_map[qubit_index]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the current quantum state.
        
        Returns:
            Dictionary containing various statistics
        """
        if self._lock:
            with self._lock:
                return self._compute_statistics()
        else:
            return self._compute_statistics()
    
    def _compute_statistics(self) -> Dict[str, Any]:
        """Compute quantum state statistics."""
        stats = {
            'num_qubits': self.num_qubits,
            'superposition_count': sum(1 for q in self.qubits if q.state == QubitState.SUPERPOSITION),
            'entangled_count': sum(1 for q in self.qubits if q.state == QubitState.ENTANGLED),
            'definite_count': sum(1 for q in self.qubits if q.state in [QubitState.ZERO, QubitState.ONE]),
            'entanglement_pairs': len(self.entanglement_map),
            'measurement_count': len(self.measurement_history),
            'threading_enabled': self.enable_threading
        }
        
        # Add measurement statistics
        if self.measurement_history:
            results = [m['result'] for m in self.measurement_history]
            stats['measurement_zeros'] = results.count(0)
            stats['measurement_ones'] = results.count(1)
            stats['measurement_ratio'] = stats['measurement_ones'] / len(results)
        
        return stats
    
    def shutdown(self) -> None:
        """Shutdown the qubit emulator and clean up resources."""
        # Clear all qubits
        self.qubits.clear()
        self.entanglement_map.clear()
        self.measurement_history.clear()
        
        # Release lock if it exists
        if self._lock:
            self._lock = None 