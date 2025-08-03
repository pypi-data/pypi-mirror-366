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

# Lazy imports for ML modules to avoid TensorFlow/PyTorch import issues
def _import_ml_modules():
    try:
        from .ml import PyTorchPatch, TensorFlowPatch, ModelOptimizer
        return PyTorchPatch, TensorFlowPatch, ModelOptimizer
    except ImportError:
        return None, None, None

# Quantum Error Correction
from .error_correction import StabilizerCode, SurfaceCode, ToricCode, CodeType

# Quantum Machine Learning
from .qml import QuantumNeuralNetwork, VariationalQuantumCircuit, QuantumNeuralClassifier, QuantumLayer, QuantumLayerType

# Distributed Computing
from .distributed import QuantumClusterManager, NodeManager, NodeInfo, Task, NodeStatus, TaskPriority, RoundRobinLoadBalancer

# Hardware Acceleration
from .hardware import GPUAccelerator, CUDAManager, GPUMemoryPool, GPUInfo, GPUType

# Quantum Chemistry
from .chemistry import (
    ElectronicStructure, MolecularDynamics, QuantumChemistry,
    HartreeFock, DFT, QuantumDynamics, MolecularGeometry, GeometryOptimizer,
    ChemicalAnalyzer, ReactionPathway, VQE_Chemistry, MolecularProperties,
    Spectroscopy, ReactionKinetics, TransitionStateTheory, SolvationModel, ImplicitSolvent
)

# Financial Applications
from .finance import (
    PortfolioOptimizer, RiskAnalyzer, MarketAnalyzer,
    QuantumPortfolio, VaRCalculator, StressTesting, QuantumMarketModel,
    OptionPricer, QuantumOptionModel, AssetAllocator, QuantumAllocation,
    TradingStrategy, QuantumTrading, DerivativesPricer, QuantumDerivatives,
    FinancialForecaster, QuantumForecasting
)

from .utils.diagnostics import Diagnostics
from .utils.dynamic_import import DynamicImporter

__all__ = [
    # Core Components
    'QubitEmulator',
    'ThreadEngine', 
    'QuantumLogicRewriter',
    'MLAccelerator',
    
    # API Backends
    'GrokBackend',
    'GeminiBackend',
    'PromptGenerator',
    
    # Quantum Algorithms
    'GroverAlgorithm',
    'ShorAlgorithm',
    'QFTAlgorithm',
    
    # Machine Learning
    'PyTorchPatch',
    'TensorFlowPatch',
    'ModelOptimizer',
    
    # Quantum Error Correction
    'StabilizerCode',
    'SurfaceCode',
    'ToricCode',
    'CodeType',
    
    # Quantum Machine Learning
    'QuantumNeuralNetwork',
    'VariationalQuantumCircuit',
    'QuantumNeuralClassifier',
    'QuantumLayer',
    'QuantumLayerType',
    
    # Distributed Computing
    'QuantumClusterManager',
    'NodeManager',
    'NodeInfo',
    'Task',
    'NodeStatus',
    'TaskPriority',
    'RoundRobinLoadBalancer',
    
    # Hardware Acceleration
    'GPUAccelerator',
    'CUDAManager',
    'GPUMemoryPool',
    'GPUInfo',
    'GPUType',
    
    # Quantum Chemistry
    'ElectronicStructure',
    'MolecularDynamics',
    'QuantumChemistry',
    'HartreeFock',
    'DFT',
    'QuantumDynamics',
    'MolecularGeometry',
    'GeometryOptimizer',
    'ChemicalAnalyzer',
    'ReactionPathway',
    'VQE_Chemistry',
    'MolecularProperties',
    'Spectroscopy',
    'ReactionKinetics',
    'TransitionStateTheory',
    'SolvationModel',
    'ImplicitSolvent',
    
    # Financial Applications
    'PortfolioOptimizer',
    'RiskAnalyzer',
    'MarketAnalyzer',
    'QuantumPortfolio',
    'VaRCalculator',
    'StressTesting',
    'QuantumMarketModel',
    'OptionPricer',
    'QuantumOptionModel',
    'AssetAllocator',
    'QuantumAllocation',
    'TradingStrategy',
    'QuantumTrading',
    'DerivativesPricer',
    'QuantumDerivatives',
    'FinancialForecaster',
    'QuantumForecasting',
    
    # Utilities
    'Diagnostics',
    'DynamicImporter'
]

# Lazy loading for ML modules
def __getattr__(name):
    if name in ['PyTorchPatch', 'TensorFlowPatch', 'ModelOptimizer']:
        pytorch_patch, tensorflow_patch, model_optimizer = _import_ml_modules()
        if name == 'PyTorchPatch':
            return pytorch_patch
        elif name == 'TensorFlowPatch':
            return tensorflow_patch
        elif name == 'ModelOptimizer':
            return model_optimizer
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'") 