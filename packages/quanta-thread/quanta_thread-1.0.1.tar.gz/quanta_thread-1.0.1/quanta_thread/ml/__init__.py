"""
Machine learning acceleration modules for QuantaThread framework.
"""

# Lazy imports to avoid TensorFlow/PyTorch import issues
def _import_pytorch_patch():
    try:
        from .pytorch_patch import PyTorchPatch
        return PyTorchPatch
    except ImportError:
        return None

def _import_tensorflow_patch():
    try:
        from .tensorflow_patch import TensorFlowPatch
        return TensorFlowPatch
    except ImportError:
        return None

def _import_model_optimizer():
    try:
        from .model_optimizer import ModelOptimizer
        return ModelOptimizer
    except ImportError:
        return None

# Export the classes with lazy loading
__all__ = [
    'PyTorchPatch',
    'TensorFlowPatch',
    'ModelOptimizer'
]

# Make classes available through lazy loading
def __getattr__(name):
    if name == 'PyTorchPatch':
        return _import_pytorch_patch()
    elif name == 'TensorFlowPatch':
        return _import_tensorflow_patch()
    elif name == 'ModelOptimizer':
        return _import_model_optimizer()
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'") 