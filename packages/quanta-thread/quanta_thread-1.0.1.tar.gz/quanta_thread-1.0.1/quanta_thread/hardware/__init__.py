"""
Hardware Acceleration Module

This module provides GPU and TPU optimizations for quantum-inspired computations,
including CUDA acceleration, TPU support, and hardware-specific optimizations.
"""

from .gpu_acceleration import (
    GPUAccelerator, 
    CUDAManager, 
    GPUMemoryPool,
    GPUInfo,
    GPUType
)

__version__ = "1.0.0"
__author__ = "QuantaThread Team"

__all__ = [
    # GPU Acceleration
    "GPUAccelerator",
    "CUDAManager",
    "GPUMemoryPool",
    "GPUInfo",
    "GPUType",
] 