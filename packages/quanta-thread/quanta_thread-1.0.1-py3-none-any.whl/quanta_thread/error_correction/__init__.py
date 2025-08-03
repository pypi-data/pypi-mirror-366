"""
Quantum Error Correction Module

This module provides quantum-inspired error correction techniques for classical systems,
including stabilizer codes, surface codes, and fault-tolerant computation methods.
"""

from .stabilizer_codes import (
    StabilizerCode, 
    SurfaceCode, 
    ToricCode,
    CodeType
)

__version__ = "1.0.0"
__author__ = "QuantaThread Team"

__all__ = [
    # Stabilizer Codes
    "StabilizerCode",
    "SurfaceCode", 
    "ToricCode",
    "CodeType",
] 