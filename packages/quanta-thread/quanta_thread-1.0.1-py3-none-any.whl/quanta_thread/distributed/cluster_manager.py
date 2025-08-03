"""
Cluster Management for Distributed Quantum Computing

This module provides cluster management capabilities for distributed quantum-inspired
computations, including node management, resource allocation, and task distribution.
"""

import asyncio
import threading
import time
import uuid
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
import socket
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import numpy as np

logger = logging.getLogger(__name__)


class NodeStatus(Enum):
    """Node status enumeration."""
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"
    INITIALIZING = "initializing"


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class NodeInfo:
    """Information about a compute node."""
    
    node_id: str
    hostname: str
    ip_address: str
    port: int
    cpu_count: int
    memory_gb: float
    gpu_count: int = 0
    status: NodeStatus = NodeStatus.IDLE
    current_load: float = 0.0
    available_memory: float = 0.0
    last_heartbeat: float = field(default_factory=time.time)
    capabilities: List[str] = field(default_factory=list)
    quantum_qubits: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "node_id": self.node_id,
            "hostname": self.hostname,
            "ip_address": self.ip_address,
            "port": self.port,
            "cpu_count": self.cpu_count,
            "memory_gb": self.memory_gb,
            "gpu_count": self.gpu_count,
            "status": self.status.value,
            "current_load": self.current_load,
            "available_memory": self.available_memory,
            "last_heartbeat": self.last_heartbeat,
            "capabilities": self.capabilities,
            "quantum_qubits": self.quantum_qubits
        }


@dataclass
class Task:
    """Task definition for distributed computation."""
    
    task_id: str
    task_type: str
    function: Callable
    args: Tuple = ()
    kwargs: Dict = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    node_requirements: Dict[str, Any] = field(default_factory=dict)
    timeout: float = 300.0
    created_at: float = field(default_factory=time.time)
    assigned_node: Optional[str] = None
    status: str = "pending"
    result: Any = None
    error: Optional[str] = None


class NodeManager:
    """Manages individual compute nodes."""
    
    def __init__(self, node_id: str, hostname: str, port: int = 8080):
        """
        Initialize node manager.
        
        Args:
            node_id: Unique node identifier
            hostname: Node hostname
            port: Communication port
        """
        self.node_id = node_id
        self.hostname = hostname
        self.port = port
        self.ip_address = socket.gethostbyname(hostname)
        
        # System information
        self.cpu_count = mp.cpu_count()
        self.memory_gb = self._get_memory_gb()
        self.gpu_count = self._get_gpu_count()
        
        # Status and resources
        self.status = NodeStatus.INITIALIZING
        self.current_load = 0.0
        self.available_memory = self.memory_gb
        self.last_heartbeat = time.time()
        
        # Task management
        self.current_tasks: Dict[str, Task] = {}
        self.task_queue: List[Task] = []
        self.max_concurrent_tasks = self.cpu_count
        
        # Executors
        self.thread_executor = ThreadPoolExecutor(max_workers=self.cpu_count)
        self.process_executor = ProcessPoolExecutor(max_workers=self.cpu_count)
        
        # Communication
        self.message_queue = asyncio.Queue()
        self.heartbeat_interval = 5.0
        
        # Capabilities
        self.capabilities = self._detect_capabilities()
        self.quantum_qubits = self._estimate_quantum_qubits()
        
        logger.info(f"Node {node_id} initialized with {self.cpu_count} CPUs, "
                   f"{self.memory_gb:.1f}GB RAM, {self.gpu_count} GPUs")
    
    def _get_memory_gb(self) -> float:
        """Get available memory in GB."""
        try:
            import psutil
            return psutil.virtual_memory().total / (1024**3)
        except ImportError:
            return 8.0  # Default assumption
    
    def _get_gpu_count(self) -> int:
        """Get number of available GPUs."""
        try:
            import torch
            return torch.cuda.device_count()
        except ImportError:
            return 0
    
    def _detect_capabilities(self) -> List[str]:
        """Detect node capabilities."""
        capabilities = ["cpu", "threading", "multiprocessing"]
        
        # Check for ML frameworks
        try:
            import torch
            capabilities.append("pytorch")
        except ImportError:
            pass
        
        try:
            import tensorflow as tf
            capabilities.append("tensorflow")
        except ImportError:
            pass
        
        # Check for GPU support
        if self.gpu_count > 0:
            capabilities.append("gpu")
            capabilities.append("cuda")
        
        # Check for quantum libraries
        try:
            import qiskit
            capabilities.append("qiskit")
        except ImportError:
            pass
        
        return capabilities
    
    def _estimate_quantum_qubits(self) -> int:
        """Estimate number of quantum qubits this node can simulate."""
        # Rough estimation based on available memory
        # Each qubit requires ~2^n complex numbers for state vector
        memory_per_qubit = 16  # bytes per complex number
        max_qubits = int(np.log2(self.memory_gb * 1024**3 / memory_per_qubit))
        return min(max_qubits, 30)  # Cap at 30 qubits for practical purposes
    
    async def start(self):
        """Start the node manager."""
        self.status = NodeStatus.IDLE
        logger.info(f"Node {self.node_id} started")
        
        # Start background tasks
        asyncio.create_task(self._heartbeat_loop())
        asyncio.create_task(self._task_processor_loop())
        asyncio.create_task(self._resource_monitor_loop())
    
    async def stop(self):
        """Stop the node manager."""
        self.status = NodeStatus.OFFLINE
        self.thread_executor.shutdown(wait=True)
        self.process_executor.shutdown(wait=True)
        logger.info(f"Node {self.node_id} stopped")
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeats."""
        while self.status != NodeStatus.OFFLINE:
            self.last_heartbeat = time.time()
            await asyncio.sleep(self.heartbeat_interval)
    
    async def _task_processor_loop(self):
        """Process queued tasks."""
        while self.status != NodeStatus.OFFLINE:
            if self.task_queue and len(self.current_tasks) < self.max_concurrent_tasks:
                task = self.task_queue.pop(0)
                await self._execute_task(task)
            await asyncio.sleep(0.1)
    
    async def _resource_monitor_loop(self):
        """Monitor system resources."""
        while self.status != NodeStatus.OFFLINE:
            try:
                import psutil
                self.current_load = psutil.cpu_percent() / 100.0
                self.available_memory = psutil.virtual_memory().available / (1024**3)
            except ImportError:
                pass
            await asyncio.sleep(5.0)
    
    async def _execute_task(self, task: Task):
        """Execute a task."""
        task.status = "running"
        task.assigned_node = self.node_id
        self.current_tasks[task.task_id] = task
        
        try:
            # Choose executor based on task type
            if task.task_type in ["quantum", "ml", "optimization"]:
                executor = self.process_executor
            else:
                executor = self.thread_executor
            
            # Execute task
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                executor, 
                task.function, 
                *task.args, 
                **task.kwargs
            )
            
            task.result = result
            task.status = "completed"
            
        except Exception as e:
            task.error = str(e)
            task.status = "failed"
            logger.error(f"Task {task.task_id} failed: {e}")
        
        finally:
            # Clean up
            if task.task_id in self.current_tasks:
                del self.current_tasks[task.task_id]
    
    def submit_task(self, task: Task) -> bool:
        """Submit a task to this node."""
        if self.status != NodeStatus.IDLE and self.status != NodeStatus.BUSY:
            return False
        
        # Check resource requirements
        if not self._check_task_requirements(task):
            return False
        
        self.task_queue.append(task)
        self.task_queue.sort(key=lambda t: t.priority.value, reverse=True)
        return True
    
    def _check_task_requirements(self, task: Task) -> bool:
        """Check if node meets task requirements."""
        requirements = task.node_requirements
        
        # Check CPU requirements
        if "cpu_count" in requirements:
            if self.cpu_count < requirements["cpu_count"]:
                return False
        
        # Check memory requirements
        if "memory_gb" in requirements:
            if self.available_memory < requirements["memory_gb"]:
                return False
        
        # Check GPU requirements
        if "gpu_count" in requirements:
            if self.gpu_count < requirements["gpu_count"]:
                return False
        
        # Check capabilities
        if "capabilities" in requirements:
            required_caps = requirements["capabilities"]
            if not all(cap in self.capabilities for cap in required_caps):
                return False
        
        return True
    
    def get_node_info(self) -> NodeInfo:
        """Get current node information."""
        return NodeInfo(
            node_id=self.node_id,
            hostname=self.hostname,
            ip_address=self.ip_address,
            port=self.port,
            cpu_count=self.cpu_count,
            memory_gb=self.memory_gb,
            gpu_count=self.gpu_count,
            status=self.status,
            current_load=self.current_load,
            available_memory=self.available_memory,
            last_heartbeat=self.last_heartbeat,
            capabilities=self.capabilities,
            quantum_qubits=self.quantum_qubits
        )


class QuantumClusterManager:
    """Manages a cluster of quantum computing nodes."""
    
    def __init__(self, cluster_id: str = None):
        """
        Initialize cluster manager.
        
        Args:
            cluster_id: Unique cluster identifier
        """
        self.cluster_id = cluster_id or str(uuid.uuid4())
        self.nodes: Dict[str, NodeManager] = {}
        self.task_queue: List[Task] = []
        self.completed_tasks: Dict[str, Task] = {}
        self.failed_tasks: Dict[str, Task] = {}
        
        # Load balancing
        self.load_balancer = RoundRobinLoadBalancer()
        
        # Monitoring
        self.cluster_stats = {
            "total_nodes": 0,
            "active_nodes": 0,
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "total_quantum_qubits": 0
        }
        
        logger.info(f"Quantum cluster {self.cluster_id} initialized")
    
    def add_node(self, node: NodeManager) -> bool:
        """Add a node to the cluster."""
        if node.node_id in self.nodes:
            logger.warning(f"Node {node.node_id} already exists in cluster")
            return False
        
        self.nodes[node.node_id] = node
        self.load_balancer.add_node(node.node_id)
        self.cluster_stats["total_nodes"] += 1
        self.cluster_stats["total_quantum_qubits"] += node.quantum_qubits
        
        logger.info(f"Node {node.node_id} added to cluster {self.cluster_id}")
        return True
    
    def remove_node(self, node_id: str) -> bool:
        """Remove a node from the cluster."""
        if node_id not in self.nodes:
            return False
        
        node = self.nodes[node_id]
        self.load_balancer.remove_node(node_id)
        self.cluster_stats["total_nodes"] -= 1
        self.cluster_stats["total_quantum_qubits"] -= node.quantum_qubits
        
        del self.nodes[node_id]
        logger.info(f"Node {node_id} removed from cluster {self.cluster_id}")
        return True
    
    def submit_task(self, 
                   task_type: str,
                   function: Callable,
                   args: Tuple = (),
                   kwargs: Dict = None,
                   priority: TaskPriority = TaskPriority.NORMAL,
                   node_requirements: Dict = None,
                   timeout: float = 300.0) -> str:
        """
        Submit a task to the cluster.
        
        Args:
            task_type: Type of task
            function: Function to execute
            args: Function arguments
            kwargs: Function keyword arguments
            priority: Task priority
            node_requirements: Node requirements
            timeout: Task timeout
            
        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())
        task = Task(
            task_id=task_id,
            task_type=task_type,
            function=function,
            args=args,
            kwargs=kwargs or {},
            priority=priority,
            node_requirements=node_requirements or {},
            timeout=timeout
        )
        
        self.task_queue.append(task)
        self.task_queue.sort(key=lambda t: t.priority.value, reverse=True)
        self.cluster_stats["total_tasks"] += 1
        
        logger.info(f"Task {task_id} submitted to cluster {self.cluster_id}")
        return task_id
    
    async def process_tasks(self):
        """Process queued tasks."""
        while self.task_queue:
            task = self.task_queue[0]
            
            # Find suitable node
            node_id = self.load_balancer.select_node(task)
            if node_id is None:
                # No suitable node available, wait
                await asyncio.sleep(1.0)
                continue
            
            # Submit task to node
            node = self.nodes[node_id]
            if node.submit_task(task):
                self.task_queue.pop(0)
                logger.info(f"Task {task.task_id} assigned to node {node_id}")
            else:
                # Task submission failed, try next node
                await asyncio.sleep(0.1)
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """Get cluster status information."""
        active_nodes = sum(1 for node in self.nodes.values() 
                          if node.status in [NodeStatus.IDLE, NodeStatus.BUSY])
        
        return {
            "cluster_id": self.cluster_id,
            "total_nodes": len(self.nodes),
            "active_nodes": active_nodes,
            "queued_tasks": len(self.task_queue),
            "running_tasks": sum(len(node.current_tasks) for node in self.nodes.values()),
            "total_quantum_qubits": sum(node.quantum_qubits for node in self.nodes.values()),
            "cluster_stats": self.cluster_stats.copy()
        }
    
    def get_node_status(self, node_id: str) -> Optional[NodeInfo]:
        """Get status of a specific node."""
        if node_id not in self.nodes:
            return None
        return self.nodes[node_id].get_node_info()


class RoundRobinLoadBalancer:
    """Simple round-robin load balancer."""
    
    def __init__(self):
        """Initialize load balancer."""
        self.nodes: List[str] = []
        self.current_index = 0
    
    def add_node(self, node_id: str):
        """Add a node to the load balancer."""
        if node_id not in self.nodes:
            self.nodes.append(node_id)
    
    def remove_node(self, node_id: str):
        """Remove a node from the load balancer."""
        if node_id in self.nodes:
            self.nodes.remove(node_id)
    
    def select_node(self, task: Task) -> Optional[str]:
        """Select a node for task execution."""
        if not self.nodes:
            return None
        
        # Simple round-robin selection
        node_id = self.nodes[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.nodes)
        
        return node_id 