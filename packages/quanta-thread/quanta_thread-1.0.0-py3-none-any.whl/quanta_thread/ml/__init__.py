"""
Machine learning acceleration modules for QuantaThread framework.
"""

from .pytorch_patch import PyTorchPatch
from .tensorflow_patch import TensorFlowPatch
from .model_optimizer import ModelOptimizer

__all__ = [
    'PyTorchPatch',
    'TensorFlowPatch',
    'ModelOptimizer'
] 