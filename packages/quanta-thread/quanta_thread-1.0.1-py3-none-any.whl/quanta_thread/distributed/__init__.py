"""
Distributed Computing Module

This module provides multi-node quantum-inspired computation capabilities,
including distributed quantum algorithms, cluster management, and parallel processing.
"""

from .cluster_manager import (
    QuantumClusterManager, 
    NodeManager,
    NodeInfo,
    Task,
    NodeStatus,
    TaskPriority,
    RoundRobinLoadBalancer
)

__version__ = "1.0.0"
__author__ = "QuantaThread Team"

__all__ = [
    # Cluster Management
    "QuantumClusterManager",
    "NodeManager",
    "NodeInfo",
    "Task",
    "NodeStatus",
    "TaskPriority",
    "RoundRobinLoadBalancer",
] 