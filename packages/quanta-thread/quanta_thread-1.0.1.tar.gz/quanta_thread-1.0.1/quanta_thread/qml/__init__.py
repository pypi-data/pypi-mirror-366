"""
Quantum Machine Learning Module

This module provides quantum-inspired machine learning algorithms and frameworks,
including quantum neural networks, variational quantum circuits, and quantum kernels.
"""

from .quantum_neural_networks import (
    QuantumNeuralNetwork, 
    VariationalQuantumCircuit, 
    QuantumNeuralClassifier,
    QuantumLayer,
    QuantumLayerType
)

__version__ = "1.0.0"
__author__ = "QuantaThread Team"

__all__ = [
    # Quantum Neural Networks
    "QuantumNeuralNetwork",
    "VariationalQuantumCircuit",
    "QuantumNeuralClassifier",
    "QuantumLayer",
    "QuantumLayerType",
] 