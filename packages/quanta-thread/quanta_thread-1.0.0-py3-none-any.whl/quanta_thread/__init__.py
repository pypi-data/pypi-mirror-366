"""
QuantaThread: Quantum-Inspired Computing Framework for Classical Hardware

A Python framework that emulates quantum behavior to accelerate algorithms
and machine learning on classical computers using AI APIs.
"""

__version__ = "1.0.0"
__author__ = "QuantaThread Team"

from .core.qubit_emulator import QubitEmulator
from .core.thread_engine import ThreadEngine
from .core.quantum_logic_rewriter import QuantumLogicRewriter
from .core.ml_accelerator import MLAccelerator

from .api.grok_backend import GrokBackend
from .api.gemini_backend import GeminiBackend
from .api.prompt_generator import PromptGenerator

from .algorithms.grover import GroverAlgorithm
from .algorithms.shor import ShorAlgorithm
from .algorithms.qft import QFTAlgorithm

from .ml.pytorch_patch import PyTorchPatch
from .ml.tensorflow_patch import TensorFlowPatch
from .ml.model_optimizer import ModelOptimizer

from .utils.diagnostics import Diagnostics
from .utils.dynamic_import import DynamicImporter

__all__ = [
    'QubitEmulator',
    'ThreadEngine', 
    'QuantumLogicRewriter',
    'MLAccelerator',
    'GrokBackend',
    'GeminiBackend',
    'PromptGenerator',
    'GroverAlgorithm',
    'ShorAlgorithm',
    'QFTAlgorithm',
    'PyTorchPatch',
    'TensorFlowPatch',
    'ModelOptimizer',
    'Diagnostics',
    'DynamicImporter'
] 