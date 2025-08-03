"""
Diagnostics module for QuantaThread framework.

Provides performance monitoring, debugging, and profiling capabilities
for quantum-inspired algorithms and classical optimizations.
"""

import time
import psutil
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
import logging


@dataclass
class PerformanceMetrics:
    """Performance metrics for algorithm execution."""
    execution_time: float
    memory_usage: float
    cpu_usage: float
    iterations: int
    success_probability: float
    speedup_factor: float
    timestamp: float = field(default_factory=time.time)


@dataclass
class AlgorithmProfile:
    """Profile information for a specific algorithm."""
    name: str
    total_executions: int = 0
    total_execution_time: float = 0.0
    total_memory_usage: float = 0.0
    total_cpu_usage: float = 0.0
    total_iterations: int = 0
    success_count: int = 0
    failure_count: int = 0
    metrics_history: List[PerformanceMetrics] = field(default_factory=list)
    
    @property
    def average_execution_time(self) -> float:
        """Calculate average execution time."""
        return self.total_execution_time / max(self.total_executions, 1)
    
    @property
    def average_memory_usage(self) -> float:
        """Calculate average memory usage."""
        return self.total_memory_usage / max(self.total_executions, 1)
    
    @property
    def average_cpu_usage(self) -> float:
        """Calculate average CPU usage."""
        return self.total_cpu_usage / max(self.total_executions, 1)
    
    @property
    def average_iterations(self) -> float:
        """Calculate average iterations."""
        return self.total_iterations / max(self.total_executions, 1)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        total = self.success_count + self.failure_count
        return self.success_count / max(total, 1)


class Diagnostics:
    """
    Comprehensive diagnostics and monitoring system for QuantaThread.
    
    Provides real-time performance monitoring, profiling, and debugging
    capabilities for quantum-inspired algorithms.
    """
    
    def __init__(self, enable_logging: bool = True, max_history: int = 1000):
        """
        Initialize diagnostics system.
        
        Args:
            enable_logging: Whether to enable logging
            max_history: Maximum number of metrics to keep in history
        """
        self.enable_logging = enable_logging
        self.max_history = max_history
        self.profiles: Dict[str, AlgorithmProfile] = defaultdict(AlgorithmProfile)
        self.active_monitors: Dict[str, threading.Thread] = {}
        self.monitoring_enabled = False
        self.start_time = time.time()
        
        # Setup logging
        if enable_logging:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            self.logger = logging.getLogger('QuantaThread.Diagnostics')
        else:
            self.logger = None
    
    def start_monitoring(self, algorithm_name: str) -> None:
        """Start monitoring for a specific algorithm."""
        if algorithm_name not in self.profiles:
            self.profiles[algorithm_name] = AlgorithmProfile(name=algorithm_name)
        
        if self.logger:
            self.logger.info(f"Started monitoring for algorithm: {algorithm_name}")
    
    def stop_monitoring(self, algorithm_name: str) -> None:
        """Stop monitoring for a specific algorithm."""
        if algorithm_name in self.active_monitors:
            self.active_monitors[algorithm_name].join()
            del self.active_monitors[algorithm_name]
        
        if self.logger:
            self.logger.info(f"Stopped monitoring for algorithm: {algorithm_name}")
    
    def record_execution(self, algorithm_name: str, metrics: PerformanceMetrics) -> None:
        """Record execution metrics for an algorithm."""
        if algorithm_name not in self.profiles:
            self.profiles[algorithm_name] = AlgorithmProfile(name=algorithm_name)
        
        profile = self.profiles[algorithm_name]
        profile.total_executions += 1
        profile.total_execution_time += metrics.execution_time
        profile.total_memory_usage += metrics.memory_usage
        profile.total_cpu_usage += metrics.cpu_usage
        profile.total_iterations += metrics.iterations
        
        if metrics.success_probability > 0.5:
            profile.success_count += 1
        else:
            profile.failure_count += 1
        
        # Add to history
        profile.metrics_history.append(metrics)
        if len(profile.metrics_history) > self.max_history:
            profile.metrics_history.pop(0)
        
        if self.logger:
            self.logger.info(
                f"Recorded execution for {algorithm_name}: "
                f"time={metrics.execution_time:.4f}s, "
                f"iterations={metrics.iterations}, "
                f"success_prob={metrics.success_probability:.4f}"
            )
    
    def get_profile(self, algorithm_name: str) -> Optional[AlgorithmProfile]:
        """Get profile for a specific algorithm."""
        return self.profiles.get(algorithm_name)
    
    def get_all_profiles(self) -> Dict[str, AlgorithmProfile]:
        """Get all algorithm profiles."""
        return dict(self.profiles)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system statistics."""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': process.memory_percent(),
            'memory_used_mb': memory_info.rss / 1024 / 1024,
            'memory_available_mb': psutil.virtual_memory().available / 1024 / 1024,
            'disk_usage_percent': psutil.disk_usage('/').percent,
            'uptime': time.time() - self.start_time
        }
    
    def benchmark_algorithm(self, algorithm_name: str, 
                          test_function: Callable, 
                          num_runs: int = 10) -> Dict[str, Any]:
        """Run benchmark for an algorithm."""
        if algorithm_name not in self.profiles:
            self.profiles[algorithm_name] = AlgorithmProfile(name=algorithm_name)
        
        results = []
        total_time = 0.0
        
        for i in range(num_runs):
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            # Run the test function
            result = test_function()
            
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            execution_time = end_time - start_time
            memory_usage = end_memory - start_memory
            cpu_usage = psutil.cpu_percent(interval=0.1)
            
            metrics = PerformanceMetrics(
                execution_time=execution_time,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                iterations=getattr(result, 'iterations', 0),
                success_probability=getattr(result, 'success_probability', 1.0),
                speedup_factor=getattr(result, 'speedup_factor', 1.0)
            )
            
            self.record_execution(algorithm_name, metrics)
            results.append(metrics)
            total_time += execution_time
        
        # Calculate statistics
        avg_time = total_time / num_runs
        avg_memory = sum(r.memory_usage for r in results) / num_runs
        avg_cpu = sum(r.cpu_usage for r in results) / num_runs
        avg_iterations = sum(r.iterations for r in results) / num_runs
        avg_success = sum(r.success_probability for r in results) / num_runs
        
        return {
            'algorithm_name': algorithm_name,
            'num_runs': num_runs,
            'total_time': total_time,
            'average_execution_time': avg_time,
            'average_memory_usage': avg_memory,
            'average_cpu_usage': avg_cpu,
            'average_iterations': avg_iterations,
            'average_success_probability': avg_success,
            'min_execution_time': min(r.execution_time for r in results),
            'max_execution_time': max(r.execution_time for r in results),
            'std_execution_time': self._calculate_std([r.execution_time for r in results])
        }
    
    def generate_report(self, output_file: Optional[str] = None) -> str:
        """Generate a comprehensive diagnostic report."""
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("QUANTATHREAD DIAGNOSTICS REPORT")
        report_lines.append("=" * 60)
        report_lines.append(f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Uptime: {time.time() - self.start_time:.2f} seconds")
        report_lines.append("")
        
        # System statistics
        system_stats = self.get_system_stats()
        report_lines.append("SYSTEM STATISTICS:")
        report_lines.append("-" * 20)
        report_lines.append(f"CPU Usage: {system_stats['cpu_percent']:.1f}%")
        report_lines.append(f"Memory Usage: {system_stats['memory_used_mb']:.1f} MB")
        report_lines.append(f"Memory Available: {system_stats['memory_available_mb']:.1f} MB")
        report_lines.append(f"Disk Usage: {system_stats['disk_usage_percent']:.1f}%")
        report_lines.append("")
        
        # Algorithm profiles
        if self.profiles:
            report_lines.append("ALGORITHM PROFILES:")
            report_lines.append("-" * 20)
            
            for name, profile in self.profiles.items():
                report_lines.append(f"Algorithm: {name}")
                report_lines.append(f"  Total Executions: {profile.total_executions}")
                report_lines.append(f"  Average Execution Time: {profile.average_execution_time:.4f}s")
                report_lines.append(f"  Average Memory Usage: {profile.average_memory_usage:.2f} MB")
                report_lines.append(f"  Average CPU Usage: {profile.average_cpu_usage:.1f}%")
                report_lines.append(f"  Average Iterations: {profile.average_iterations:.2f}")
                report_lines.append(f"  Success Rate: {profile.success_rate:.2%}")
                report_lines.append("")
        else:
            report_lines.append("No algorithm profiles recorded.")
            report_lines.append("")
        
        report_lines.append("=" * 60)
        
        report = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
        
        return report
    
    def export_data(self, output_file: str) -> None:
        """Export diagnostic data to JSON file."""
        data = {
            'metadata': {
                'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'uptime': time.time() - self.start_time,
                'total_algorithms': len(self.profiles)
            },
            'system_stats': self.get_system_stats(),
            'profiles': {}
        }
        
        for name, profile in self.profiles.items():
            data['profiles'][name] = {
                'name': profile.name,
                'total_executions': profile.total_executions,
                'total_execution_time': profile.total_execution_time,
                'total_memory_usage': profile.total_memory_usage,
                'total_cpu_usage': profile.total_cpu_usage,
                'total_iterations': profile.total_iterations,
                'success_count': profile.success_count,
                'failure_count': profile.failure_count,
                'average_execution_time': profile.average_execution_time,
                'average_memory_usage': profile.average_memory_usage,
                'average_cpu_usage': profile.average_cpu_usage,
                'average_iterations': profile.average_iterations,
                'success_rate': profile.success_rate,
                'metrics_history': [
                    {
                        'execution_time': m.execution_time,
                        'memory_usage': m.memory_usage,
                        'cpu_usage': m.cpu_usage,
                        'iterations': m.iterations,
                        'success_probability': m.success_probability,
                        'speedup_factor': m.speedup_factor,
                        'timestamp': m.timestamp
                    }
                    for m in profile.metrics_history
                ]
            }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def clear_history(self, algorithm_name: Optional[str] = None) -> None:
        """Clear metrics history for algorithm(s)."""
        if algorithm_name:
            if algorithm_name in self.profiles:
                self.profiles[algorithm_name].metrics_history.clear()
        else:
            for profile in self.profiles.values():
                profile.metrics_history.clear()
    
    def reset(self) -> None:
        """Reset all diagnostic data."""
        self.profiles.clear()
        self.active_monitors.clear()
        self.start_time = time.time()
        
        if self.logger:
            self.logger.info("Diagnostics system reset")
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5 