"""
GPU Acceleration for Quantum Computing

This module provides GPU acceleration capabilities for quantum-inspired computations,
including CUDA support, memory management, and parallel processing optimizations.
"""

import numpy as np
import torch
import torch.cuda as cuda
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from dataclasses import dataclass
from enum import Enum
import logging
import time
import threading
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class GPUType(Enum):
    """GPU types enumeration."""
    NVIDIA = "nvidia"
    AMD = "amd"
    INTEL = "intel"
    UNKNOWN = "unknown"


@dataclass
class GPUInfo:
    """GPU information structure."""
    
    device_id: int
    name: str
    gpu_type: GPUType
    memory_total: int  # in bytes
    memory_free: int   # in bytes
    compute_capability: Tuple[int, int]
    multiprocessor_count: int
    max_threads_per_block: int
    max_blocks_per_grid: Tuple[int, int, int]
    is_available: bool = True
    
    @property
    def memory_used(self) -> int:
        """Get used memory in bytes."""
        return self.memory_total - self.memory_free
    
    @property
    def memory_usage_percent(self) -> float:
        """Get memory usage percentage."""
        return (self.memory_used / self.memory_total) * 100


class CUDAManager:
    """Manages CUDA devices and operations."""
    
    def __init__(self):
        """Initialize CUDA manager."""
        self.devices: Dict[int, GPUInfo] = {}
        self.current_device: Optional[int] = None
        self._initialize_devices()
    
    def _initialize_devices(self):
        """Initialize available CUDA devices."""
        if not cuda.is_available():
            logger.warning("CUDA is not available")
            return
        
        device_count = cuda.device_count()
        logger.info(f"Found {device_count} CUDA device(s)")
        
        for device_id in range(device_count):
            try:
                cuda.set_device(device_id)
                props = cuda.get_device_properties(device_id)
                
                # Get memory info
                memory_total = props.total_memory
                memory_free = cuda.memory_reserved(device_id) - cuda.memory_allocated(device_id)
                
                gpu_info = GPUInfo(
                    device_id=device_id,
                    name=props.name,
                    gpu_type=GPUType.NVIDIA,
                    memory_total=memory_total,
                    memory_free=memory_free,
                    compute_capability=(props.major, props.minor),
                    multiprocessor_count=props.multi_processor_count,
                    max_threads_per_block=props.max_threads_per_block,
                    max_blocks_per_grid=(props.max_grid_size[0], 
                                        props.max_grid_size[1], 
                                        props.max_grid_size[2])
                )
                
                self.devices[device_id] = gpu_info
                logger.info(f"Initialized GPU {device_id}: {props.name}")
                
            except Exception as e:
                logger.error(f"Failed to initialize GPU {device_id}: {e}")
        
        # Set default device
        if self.devices:
            self.current_device = 0
            cuda.set_device(0)
    
    def get_device_info(self, device_id: int) -> Optional[GPUInfo]:
        """Get information about a specific device."""
        if device_id in self.devices:
            # Update memory info
            device = self.devices[device_id]
            device.memory_free = cuda.memory_reserved(device_id) - cuda.memory_allocated(device_id)
            return device
        return None
    
    def get_best_device(self, memory_required: int = 0) -> Optional[int]:
        """Get the best available device based on memory and performance."""
        best_device = None
        best_score = -1
        
        for device_id, device in self.devices.items():
            if not device.is_available:
                continue
            
            if memory_required > device.memory_free:
                continue
            
            # Score based on memory availability and compute capability
            memory_score = device.memory_free / device.memory_total
            compute_score = device.compute_capability[0] + device.compute_capability[1] / 10
            total_score = memory_score * 0.6 + compute_score * 0.4
            
            if total_score > best_score:
                best_score = total_score
                best_device = device_id
        
        return best_device
    
    def set_device(self, device_id: int) -> bool:
        """Set the current CUDA device."""
        if device_id not in self.devices:
            logger.error(f"Device {device_id} not found")
            return False
        
        try:
            cuda.set_device(device_id)
            self.current_device = device_id
            logger.info(f"Set current device to {device_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to set device {device_id}: {e}")
            return False
    
    def synchronize(self, device_id: Optional[int] = None):
        """Synchronize CUDA operations."""
        if device_id is not None:
            with cuda.device(device_id):
                cuda.synchronize()
        else:
            cuda.synchronize()
    
    def empty_cache(self, device_id: Optional[int] = None):
        """Empty CUDA cache."""
        if device_id is not None:
            with cuda.device(device_id):
                cuda.empty_cache()
        else:
            cuda.empty_cache()


class GPUMemoryPool:
    """Manages GPU memory allocation and pooling."""
    
    def __init__(self, device_id: int, pool_size: Optional[int] = None):
        """
        Initialize GPU memory pool.
        
        Args:
            device_id: GPU device ID
            pool_size: Pool size in bytes (None for auto)
        """
        self.device_id = device_id
        self.pool_size = pool_size
        self.allocated_blocks: Dict[int, int] = {}  # ptr -> size
        self.free_blocks: List[Tuple[int, int]] = []  # (ptr, size)
        self._lock = threading.Lock()
        
        # Initialize pool
        if pool_size is None:
            # Use 80% of available memory
            device_info = cuda.get_device_properties(device_id)
            self.pool_size = int(device_info.total_memory * 0.8)
        
        logger.info(f"Initialized GPU memory pool on device {device_id} "
                   f"with size {self.pool_size / 1024**3:.2f}GB")
    
    def allocate(self, size: int) -> int:
        """
        Allocate memory from pool.
        
        Args:
            size: Memory size in bytes
            
        Returns:
            Memory pointer
        """
        with self._lock:
            # Try to find a suitable free block
            for i, (ptr, block_size) in enumerate(self.free_blocks):
                if block_size >= size:
                    # Use this block
                    del self.free_blocks[i]
                    
                    # If block is larger than needed, split it
                    if block_size > size:
                        remaining_size = block_size - size
                        remaining_ptr = ptr + size
                        self.free_blocks.append((remaining_ptr, remaining_size))
                    
                    self.allocated_blocks[ptr] = size
                    return ptr
            
            # No suitable free block, allocate new memory
            try:
                ptr = cuda.malloc(size)
                self.allocated_blocks[ptr] = size
                return ptr
            except Exception as e:
                logger.error(f"Failed to allocate {size} bytes: {e}")
                raise
    
    def free(self, ptr: int):
        """
        Free allocated memory.
        
        Args:
            ptr: Memory pointer to free
        """
        with self._lock:
            if ptr not in self.allocated_blocks:
                logger.warning(f"Attempting to free unallocated pointer {ptr}")
                return
            
            size = self.allocated_blocks[ptr]
            del self.allocated_blocks[ptr]
            
            # Add to free blocks
            self.free_blocks.append((ptr, size))
            
            # Merge adjacent free blocks
            self._merge_free_blocks()
    
    def _merge_free_blocks(self):
        """Merge adjacent free memory blocks."""
        if len(self.free_blocks) < 2:
            return
        
        # Sort by pointer
        self.free_blocks.sort(key=lambda x: x[0])
        
        i = 0
        while i < len(self.free_blocks) - 1:
            current_ptr, current_size = self.free_blocks[i]
            next_ptr, next_size = self.free_blocks[i + 1]
            
            # Check if blocks are adjacent
            if current_ptr + current_size == next_ptr:
                # Merge blocks
                merged_size = current_size + next_size
                self.free_blocks[i] = (current_ptr, merged_size)
                del self.free_blocks[i + 1]
            else:
                i += 1
    
    def get_memory_stats(self) -> Dict[str, int]:
        """Get memory pool statistics."""
        with self._lock:
            allocated_size = sum(self.allocated_blocks.values())
            free_size = sum(size for _, size in self.free_blocks)
            
            return {
                "total_size": self.pool_size,
                "allocated_size": allocated_size,
                "free_size": free_size,
                "allocated_blocks": len(self.allocated_blocks),
                "free_blocks": len(self.free_blocks)
            }


class GPUAccelerator:
    """Main GPU acceleration class for quantum computations."""
    
    def __init__(self, device_id: Optional[int] = None):
        """
        Initialize GPU accelerator.
        
        Args:
            device_id: GPU device ID (None for auto-selection)
        """
        self.cuda_manager = CUDAManager()
        
        if device_id is None:
            device_id = self.cuda_manager.get_best_device()
        
        if device_id is None:
            raise RuntimeError("No suitable GPU device found")
        
        self.device_id = device_id
        self.cuda_manager.set_device(device_id)
        
        # Initialize memory pool
        self.memory_pool = GPUMemoryPool(device_id)
        
        # Performance tracking
        self.operation_times: Dict[str, List[float]] = {}
        
        logger.info(f"GPU accelerator initialized on device {device_id}")
    
    @contextmanager
    def gpu_context(self):
        """Context manager for GPU operations."""
        try:
            yield self
        finally:
            self.cuda_manager.synchronize()
    
    def to_gpu(self, tensor: torch.Tensor) -> torch.Tensor:
        """Move tensor to GPU."""
        return tensor.cuda(self.device_id)
    
    def to_cpu(self, tensor: torch.Tensor) -> torch.Tensor:
        """Move tensor to CPU."""
        return tensor.cpu()
    
    def quantum_state_vector(self, num_qubits: int) -> torch.Tensor:
        """
        Create quantum state vector on GPU.
        
        Args:
            num_qubits: Number of qubits
            
        Returns:
            Quantum state vector tensor
        """
        state_size = 2**num_qubits
        state = torch.zeros(state_size, dtype=torch.complex64, device=f'cuda:{self.device_id}')
        state[0] = 1.0  # Initialize to |0⟩ state
        return state
    
    def apply_quantum_gate(self, 
                          state: torch.Tensor, 
                          gate: torch.Tensor,
                          qubits: List[int]) -> torch.Tensor:
        """
        Apply quantum gate to state vector.
        
        Args:
            state: Quantum state vector
            gate: Quantum gate matrix
            qubits: Target qubits
            
        Returns:
            Updated state vector
        """
        # Reshape state for tensor operations
        num_qubits = int(np.log2(state.shape[0]))
        state_reshaped = state.view([2] * num_qubits)
        
        # Apply gate using tensor contractions
        # This is a simplified implementation
        result = torch.tensordot(state_reshaped, gate, dims=([qubits], [1]))
        
        return result.flatten()
    
    def quantum_fourier_transform(self, state: torch.Tensor) -> torch.Tensor:
        """
        Apply quantum Fourier transform.
        
        Args:
            state: Input state vector
            
        Returns:
            Transformed state vector
        """
        num_qubits = int(np.log2(state.shape[0]))
        
        # Reshape to tensor format
        state_tensor = state.view([2] * num_qubits)
        
        # Apply QFT using tensor operations
        for i in range(num_qubits):
            for j in range(i + 1, num_qubits):
                # Apply controlled phase rotation
                phase = 2 * np.pi / (2**(j - i + 1))
                rotation = torch.exp(1j * phase * torch.arange(2**(j - i + 1), 
                                                              device=state.device))
                # Apply rotation (simplified)
                state_tensor = state_tensor * rotation.view([1] * i + [2**(j - i + 1)] + [1] * (num_qubits - j - 1))
        
        return state_tensor.flatten()
    
    def measure_quantum_state(self, 
                             state: torch.Tensor, 
                             num_measurements: int = 1000) -> np.ndarray:
        """
        Measure quantum state multiple times.
        
        Args:
            state: Quantum state vector
            num_measurements: Number of measurements
            
        Returns:
            Measurement results
        """
        # Calculate probabilities
        probabilities = torch.abs(state)**2
        
        # Sample from probability distribution
        measurements = torch.multinomial(probabilities, num_measurements, replacement=True)
        
        return measurements.cpu().numpy()
    
    def parallel_quantum_operations(self, 
                                   operations: List[Callable],
                                   batch_size: int = 32) -> List[torch.Tensor]:
        """
        Execute quantum operations in parallel.
        
        Args:
            operations: List of quantum operations
            batch_size: Batch size for parallel execution
            
        Returns:
            List of operation results
        """
        results = []
        
        for i in range(0, len(operations), batch_size):
            batch = operations[i:i + batch_size]
            
            # Execute batch in parallel
            batch_results = []
            for op in batch:
                try:
                    result = op()
                    batch_results.append(result)
                except Exception as e:
                    logger.error(f"Operation failed: {e}")
                    batch_results.append(None)
            
            results.extend(batch_results)
        
        return results
    
    def optimize_memory_usage(self):
        """Optimize GPU memory usage."""
        # Empty cache
        self.cuda_manager.empty_cache()
        
        # Garbage collection
        import gc
        gc.collect()
        
        # Synchronize
        self.cuda_manager.synchronize()
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get GPU performance statistics."""
        device_info = self.cuda_manager.get_device_info(self.device_id)
        memory_stats = self.memory_pool.get_memory_stats()
        
        return {
            "device_info": device_info.to_dict() if device_info else None,
            "memory_stats": memory_stats,
            "operation_times": {op: np.mean(times) for op, times in self.operation_times.items()}
        }
    
    def benchmark_quantum_operations(self, num_qubits: int = 10) -> Dict[str, float]:
        """
        Benchmark quantum operations.
        
        Args:
            num_qubits: Number of qubits for benchmarking
            
        Returns:
            Benchmark results
        """
        results = {}
        
        # Benchmark state vector creation
        start_time = time.time()
        state = self.quantum_state_vector(num_qubits)
        cuda.synchronize()
        results["state_creation"] = time.time() - start_time
        
        # Benchmark QFT
        start_time = time.time()
        qft_state = self.quantum_fourier_transform(state)
        cuda.synchronize()
        results["quantum_fourier_transform"] = time.time() - start_time
        
        # Benchmark measurements
        start_time = time.time()
        measurements = self.measure_quantum_state(state, 1000)
        cuda.synchronize()
        results["measurements"] = time.time() - start_time
        
        return results 