"""
Thread Engine: Manages concurrency for quantum simulations and ML acceleration.

This module provides intelligent thread management for parallel quantum operations,
ML training acceleration, and dynamic workload distribution.
"""

import threading
import multiprocessing
import concurrent.futures
import queue
import time
import psutil
from typing import List, Dict, Any, Callable, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np
import logging


class WorkloadType(Enum):
    """Types of workloads that can be processed."""
    QUANTUM_SIMULATION = "quantum_simulation"
    ML_TRAINING = "ml_training"
    ML_INFERENCE = "ml_inference"
    DATA_PROCESSING = "data_processing"
    OPTIMIZATION = "optimization"


@dataclass
class ThreadTask:
    """Represents a task to be executed by a thread."""
    task_id: str
    workload_type: WorkloadType
    function: Callable
    args: tuple
    kwargs: dict
    priority: int = 0
    created_at: float = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()


class ThreadEngine:
    """
    Intelligent thread management engine for quantum-inspired computing.
    
    This class provides:
    - Dynamic thread pool sizing based on workload
    - Priority-based task scheduling
    - CPU/memory monitoring and optimization
    - Workload-specific thread allocation
    """
    
    def __init__(self, 
                 max_workers: Optional[int] = None,
                 num_threads: Optional[int] = None,
                 enable_monitoring: bool = True,
                 auto_scaling: bool = True):
        """
        Initialize the thread engine.
        
        Args:
            max_workers: Maximum number of worker threads
            enable_monitoring: Whether to monitor system resources
            auto_scaling: Whether to automatically scale thread count
        """
        self.max_workers = max_workers or num_threads or min(32, (multiprocessing.cpu_count() or 1) + 4)
        self.enable_monitoring = enable_monitoring
        self.auto_scaling = auto_scaling
        
        # Thread pools for different workload types
        self.quantum_pool: Optional[concurrent.futures.ThreadPoolExecutor] = None
        self.ml_pool: Optional[concurrent.futures.ThreadPoolExecutor] = None
        self.general_pool: Optional[concurrent.futures.ThreadPoolExecutor] = None
        
        # Task management
        self.task_queue = queue.PriorityQueue()
        self.active_tasks: Dict[str, ThreadTask] = {}
        self.completed_tasks: List[Dict[str, Any]] = []
        
        # Performance monitoring
        self.performance_stats = {
            'cpu_usage': [],
            'memory_usage': [],
            'active_threads': [],
            'task_completion_times': []
        }
        
        # Threading control
        self._lock = threading.Lock()
        self._shutdown_event = threading.Event()
        self._monitor_thread: Optional[threading.Thread] = None
        
        # Initialize pools
        self._initialize_pools()
        
        # Start monitoring if enabled
        if self.enable_monitoring:
            self._start_monitoring()
    
    def _initialize_pools(self):
        """Initialize thread pools for different workload types."""
        quantum_workers = max(2, self.max_workers // 4)
        ml_workers = max(4, self.max_workers // 2)
        general_workers = max(2, self.max_workers - quantum_workers - ml_workers)
        
        self.quantum_pool = concurrent.futures.ThreadPoolExecutor(
            max_workers=quantum_workers,
            thread_name_prefix="quantum"
        )
        
        self.ml_pool = concurrent.futures.ThreadPoolExecutor(
            max_workers=ml_workers,
            thread_name_prefix="ml"
        )
        
        self.general_pool = concurrent.futures.ThreadPoolExecutor(
            max_workers=general_workers,
            thread_name_prefix="general"
        )
    
    def _start_monitoring(self):
        """Start the performance monitoring thread."""
        self._monitor_thread = threading.Thread(
            target=self._monitor_performance,
            daemon=True,
            name="performance_monitor"
        )
        self._monitor_thread.start()
    
    def _monitor_performance(self):
        """Monitor system performance and adjust thread allocation."""
        while not self._shutdown_event.is_set():
            try:
                # Collect system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_percent = psutil.virtual_memory().percent
                
                with self._lock:
                    self.performance_stats['cpu_usage'].append(cpu_percent)
                    self.performance_stats['memory_usage'].append(memory_percent)
                    self.performance_stats['active_threads'].append(
                        len(self.active_tasks)
                    )
                    
                    # Keep only recent history
                    max_history = 100
                    for key in self.performance_stats:
                        if len(self.performance_stats[key]) > max_history:
                            self.performance_stats[key] = self.performance_stats[key][-max_history:]
                
                # Auto-scaling logic
                if self.auto_scaling:
                    self._adjust_thread_allocation(cpu_percent, memory_percent)
                
                time.sleep(5)  # Monitor every 5 seconds
                
            except Exception as e:
                logging.error(f"Performance monitoring error: {e}")
                time.sleep(10)
    
    def _adjust_thread_allocation(self, cpu_percent: float, memory_percent: float):
        """Adjust thread allocation based on system performance."""
        if cpu_percent > 80 or memory_percent > 85:
            # High load - reduce thread count
            self._scale_down_pools()
        elif cpu_percent < 50 and memory_percent < 70:
            # Low load - increase thread count
            self._scale_up_pools()
    
    def _scale_down_pools(self):
        """Scale down thread pools to reduce system load."""
        # This is a simplified implementation
        # In practice, you'd want to implement proper pool scaling
        pass
    
    def _scale_up_pools(self):
        """Scale up thread pools to utilize available resources."""
        # This is a simplified implementation
        # In practice, you'd want to implement proper pool scaling
        pass
    
    def submit_task(self, 
                   task_id: str,
                   workload_type: WorkloadType,
                   function: Callable,
                   *args,
                   priority: int = 0,
                   **kwargs) -> concurrent.futures.Future:
        """
        Submit a task for execution.
        
        Args:
            task_id: Unique identifier for the task
            workload_type: Type of workload
            function: Function to execute
            *args: Arguments for the function
            priority: Task priority (lower = higher priority)
            **kwargs: Keyword arguments for the function
            
        Returns:
            Future object representing the task execution
        """
        task = ThreadTask(
            task_id=task_id,
            workload_type=workload_type,
            function=function,
            args=args,
            kwargs=kwargs,
            priority=priority
        )
        
        with self._lock:
            self.active_tasks[task_id] = task
        
        # Submit to appropriate pool
        if workload_type == WorkloadType.QUANTUM_SIMULATION:
            future = self.quantum_pool.submit(self._execute_task, task)
        elif workload_type in [WorkloadType.ML_TRAINING, WorkloadType.ML_INFERENCE]:
            future = self.ml_pool.submit(self._execute_task, task)
        else:
            future = self.general_pool.submit(self._execute_task, task)
        
        # Add callback to track completion
        future.add_done_callback(lambda f: self._task_completed(task_id, f))
        
        return future
    
    def _execute_task(self, task: ThreadTask) -> Any:
        """
        Execute a task and track its performance.
        
        Args:
            task: Task to execute
            
        Returns:
            Result of the task execution
        """
        start_time = time.time()
        
        try:
            result = task.function(*task.args, **task.kwargs)
            execution_time = time.time() - start_time
            
            # Record performance
            with self._lock:
                self.performance_stats['task_completion_times'].append(execution_time)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logging.error(f"Task {task.task_id} failed after {execution_time:.2f}s: {e}")
            raise
    
    def _task_completed(self, task_id: str, future: concurrent.futures.Future):
        """Handle task completion."""
        with self._lock:
            if task_id in self.active_tasks:
                task = self.active_tasks.pop(task_id)
                
                completion_info = {
                    'task_id': task_id,
                    'workload_type': task.workload_type.value,
                    'priority': task.priority,
                    'created_at': task.created_at,
                    'completed_at': time.time(),
                    'duration': time.time() - task.created_at,
                    'success': not future.exception()
                }
                
                if future.exception():
                    completion_info['error'] = str(future.exception())
                
                self.completed_tasks.append(completion_info)
    
    def submit_quantum_batch(self, 
                           tasks: List[Tuple[str, Callable, tuple, dict]],
                           priority: int = 0) -> List[concurrent.futures.Future]:
        """
        Submit a batch of quantum simulation tasks.
        
        Args:
            tasks: List of (task_id, function, args, kwargs) tuples
            priority: Priority for all tasks in the batch
            
        Returns:
            List of Future objects
        """
        futures = []
        
        for task_tuple in tasks:
            task_id, function, args, kwargs = task_tuple
            # Create a ThreadTask directly to avoid the argument passing issue
            task = ThreadTask(
                task_id=task_id,
                workload_type=WorkloadType.QUANTUM_SIMULATION,
                function=function,
                args=args,
                kwargs=kwargs,
                priority=priority
            )
            
            with self._lock:
                self.active_tasks[task_id] = task
            
            # Submit to quantum pool
            future = self.quantum_pool.submit(self._execute_task, task)
            future.add_done_callback(lambda f: self._task_completed(task_id, f))
            futures.append(future)
        
        return futures
    
    def submit_ml_batch(self,
                       tasks: List[Tuple[str, Callable, tuple, dict]],
                       workload_type: WorkloadType = WorkloadType.ML_TRAINING,
                       priority: int = 0) -> List[concurrent.futures.Future]:
        """
        Submit a batch of ML tasks.
        
        Args:
            tasks: List of (task_id, function, args, kwargs) tuples
            workload_type: Type of ML workload
            priority: Priority for all tasks in the batch
            
        Returns:
            List of Future objects
        """
        futures = []
        
        for task_tuple in tasks:
            task_id, function, args, kwargs = task_tuple
            # Create a ThreadTask directly to avoid the argument passing issue
            task = ThreadTask(
                task_id=task_id,
                workload_type=workload_type,
                function=function,
                args=args,
                kwargs=kwargs,
                priority=priority
            )
            
            with self._lock:
                self.active_tasks[task_id] = task
            
            # Submit to appropriate pool
            if workload_type in [WorkloadType.ML_TRAINING, WorkloadType.ML_INFERENCE]:
                future = self.ml_pool.submit(self._execute_task, task)
            else:
                future = self.general_pool.submit(self._execute_task, task)
            
            future.add_done_callback(lambda f: self._task_completed(task_id, f))
            futures.append(future)
        
        return futures
    
    def wait_for_completion(self, 
                          futures: List[concurrent.futures.Future],
                          timeout: Optional[float] = None) -> List[Any]:
        """
        Wait for a list of futures to complete.
        
        Args:
            futures: List of Future objects
            timeout: Maximum time to wait in seconds
            
        Returns:
            List of results from completed futures
        """
        results = []
        
        for future in concurrent.futures.as_completed(futures, timeout=timeout):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logging.error(f"Future failed: {e}")
                results.append(None)
        
        return results
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get current performance statistics.
        
        Returns:
            Dictionary containing performance metrics
        """
        with self._lock:
            stats = self.performance_stats.copy()
            
            # Add current system metrics
            stats['current_cpu'] = psutil.cpu_percent()
            stats['current_memory'] = psutil.virtual_memory().percent
            stats['active_task_count'] = len(self.active_tasks)
            stats['completed_task_count'] = len(self.completed_tasks)
            
            # Calculate averages
            if stats['cpu_usage']:
                stats['avg_cpu'] = np.mean(stats['cpu_usage'])
            if stats['memory_usage']:
                stats['avg_memory'] = np.mean(stats['memory_usage'])
            if stats['task_completion_times']:
                stats['avg_task_time'] = np.mean(stats['task_completion_times'])
            
            return stats
    
    def get_pool_status(self) -> Dict[str, Any]:
        """
        Get status of all thread pools.
        
        Returns:
            Dictionary containing pool status information
        """
        status = {}
        
        for pool_name, pool in [
            ('quantum', self.quantum_pool),
            ('ml', self.ml_pool),
            ('general', self.general_pool)
        ]:
            if pool:
                status[pool_name] = {
                    'max_workers': pool._max_workers,
                    'active_threads': len(pool._threads),
                    'queue_size': pool._work_queue.qsize() if hasattr(pool._work_queue, 'qsize') else 0
                }
        
        return status
    
    def shutdown(self, wait: bool = True):
        """
        Shutdown the thread engine.
        
        Args:
            wait: Whether to wait for active tasks to complete
        """
        self._shutdown_event.set()
        
        # Shutdown all pools
        for pool in [self.quantum_pool, self.ml_pool, self.general_pool]:
            if pool:
                pool.shutdown(wait=wait)
        
        # Wait for monitor thread
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown() 