"""
Portfolio Optimization Module

This module provides quantum-inspired portfolio optimization algorithms,
including modern portfolio theory, risk management, and asset allocation.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum
import logging
from scipy.optimize import minimize
from sklearn.covariance import LedoitWolf

logger = logging.getLogger(__name__)


class OptimizationMethod(Enum):
    """Portfolio optimization methods."""
    MARKOWITZ = "markowitz"
    QUANTUM_INSPIRED = "quantum_inspired"
    BLACK_LITTERMAN = "black_litterman"
    RISK_PARITY = "risk_parity"


@dataclass
class PortfolioResult:
    """Result of portfolio optimization."""
    
    weights: np.ndarray
    expected_return: float
    volatility: float
    sharpe_ratio: float
    risk_free_rate: float
    optimization_method: OptimizationMethod
    constraints_satisfied: bool
    optimization_time: float
    convergence_status: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "weights": self.weights.tolist(),
            "expected_return": self.expected_return,
            "volatility": self.volatility,
            "sharpe_ratio": self.sharpe_ratio,
            "risk_free_rate": self.risk_free_rate,
            "optimization_method": self.optimization_method.value,
            "constraints_satisfied": self.constraints_satisfied,
            "optimization_time": self.optimization_time,
            "convergence_status": self.convergence_status
        }


class PortfolioOptimizer:
    """Quantum-inspired portfolio optimizer."""
    
    def __init__(self, 
                 method: OptimizationMethod = OptimizationMethod.QUANTUM_INSPIRED,
                 risk_free_rate: float = 0.02,
                 max_iterations: int = 1000):
        """
        Initialize portfolio optimizer.
        
        Args:
            method: Optimization method
            risk_free_rate: Risk-free rate
            max_iterations: Maximum optimization iterations
        """
        self.method = method
        self.risk_free_rate = risk_free_rate
        self.max_iterations = max_iterations
        self.returns = None
        self.covariance = None
        self.expected_returns = None
        
    def fit(self, returns: np.ndarray, expected_returns: Optional[np.ndarray] = None):
        """
        Fit the optimizer with historical returns.
        
        Args:
            returns: Historical returns (n_assets, n_periods)
            expected_returns: Expected returns (n_assets,)
        """
        self.returns = returns
        self.expected_returns = expected_returns
        
        # Calculate covariance matrix
        if self.method == OptimizationMethod.QUANTUM_INSPIRED:
            # Use quantum-inspired covariance estimation
            self.covariance = self._quantum_covariance_estimation(returns)
        else:
            # Use standard covariance estimation
            self.covariance = np.cov(returns)
        
        # Calculate expected returns if not provided
        if self.expected_returns is None:
            self.expected_returns = np.mean(returns, axis=1)
    
    def optimize(self, 
                target_return: Optional[float] = None,
                target_volatility: Optional[float] = None,
                constraints: Optional[Dict] = None) -> PortfolioResult:
        """
        Optimize portfolio weights.
        
        Args:
            target_return: Target expected return
            target_volatility: Target volatility
            constraints: Additional constraints
            
        Returns:
            Portfolio optimization result
        """
        if self.returns is None:
            raise ValueError("Must call fit() before optimize()")
        
        n_assets = self.returns.shape[0]
        
        # Initial weights (equal weight)
        initial_weights = np.ones(n_assets) / n_assets
        
        # Define constraints
        bounds = [(0, 1) for _ in range(n_assets)]  # Long-only constraint
        constraints_list = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}  # Sum to 1
        ]
        
        # Add target return constraint
        if target_return is not None:
            constraints_list.append({
                'type': 'eq', 
                'fun': lambda w: np.dot(w, self.expected_returns) - target_return
            })
        
        # Add target volatility constraint
        if target_volatility is not None:
            constraints_list.append({
                'type': 'eq',
                'fun': lambda w: np.sqrt(np.dot(w.T, np.dot(self.covariance, w))) - target_volatility
            })
        
        # Add custom constraints
        if constraints:
            for constraint in constraints:
                constraints_list.append(constraint)
        
        # Define objective function
        if self.method == OptimizationMethod.QUANTUM_INSPIRED:
            objective = self._quantum_objective_function
        else:
            objective = self._markowitz_objective_function
        
        # Optimize
        import time
        start_time = time.time()
        
        result = minimize(
            objective,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints_list,
            options={'maxiter': self.max_iterations}
        )
        
        optimization_time = time.time() - start_time
        
        # Calculate portfolio metrics
        weights = result.x
        expected_return = np.dot(weights, self.expected_returns)
        volatility = np.sqrt(np.dot(weights.T, np.dot(self.covariance, weights)))
        sharpe_ratio = (expected_return - self.risk_free_rate) / volatility
        
        return PortfolioResult(
            weights=weights,
            expected_return=expected_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            risk_free_rate=self.risk_free_rate,
            optimization_method=self.method,
            constraints_satisfied=result.success,
            optimization_time=optimization_time,
            convergence_status=result.message
        )
    
    def _quantum_covariance_estimation(self, returns: np.ndarray) -> np.ndarray:
        """Quantum-inspired covariance estimation."""
        # Use Ledoit-Wolf shrinkage estimator as quantum-inspired approach
        lw = LedoitWolf()
        lw.fit(returns.T)
        return lw.covariance_
    
    def _quantum_objective_function(self, weights: np.ndarray) -> float:
        """Quantum-inspired objective function."""
        # Combine risk and return with quantum-inspired weighting
        expected_return = np.dot(weights, self.expected_returns)
        volatility = np.sqrt(np.dot(weights.T, np.dot(self.covariance, weights)))
        
        # Quantum-inspired penalty for non-diversification
        concentration_penalty = np.sum(weights**2) * 0.1
        
        return -expected_return + volatility + concentration_penalty
    
    def _markowitz_objective_function(self, weights: np.ndarray) -> float:
        """Standard Markowitz objective function."""
        expected_return = np.dot(weights, self.expected_returns)
        volatility = np.sqrt(np.dot(weights.T, np.dot(self.covariance, weights)))
        
        return -expected_return + volatility


class QuantumPortfolio:
    """Quantum-inspired portfolio with advanced features."""
    
    def __init__(self, 
                 n_assets: int,
                 quantum_layers: int = 3,
                 learning_rate: float = 0.01):
        """
        Initialize quantum portfolio.
        
        Args:
            n_assets: Number of assets
            quantum_layers: Number of quantum-inspired layers
            learning_rate: Learning rate for optimization
        """
        self.n_assets = n_assets
        self.quantum_layers = quantum_layers
        self.learning_rate = learning_rate
        self.weights = np.ones(n_assets) / n_assets
        self.quantum_parameters = np.random.uniform(0, 2*np.pi, quantum_layers * n_assets)
        
    def update_weights(self, returns: np.ndarray, market_data: Dict[str, Any]):
        """Update portfolio weights using quantum-inspired algorithm."""
        # Quantum-inspired weight update
        for layer in range(self.quantum_layers):
            # Apply quantum rotation
            rotation = self.quantum_parameters[layer * self.n_assets:(layer + 1) * self.n_assets]
            self.weights = self.weights * np.cos(rotation) + np.sin(rotation)
            
            # Normalize weights
            self.weights = np.abs(self.weights)
            self.weights = self.weights / np.sum(self.weights)
        
        # Apply market feedback
        recent_performance = np.mean(returns, axis=1)
        performance_factor = 1 + self.learning_rate * recent_performance
        self.weights = self.weights * performance_factor
        self.weights = self.weights / np.sum(self.weights)
    
    def get_weights(self) -> np.ndarray:
        """Get current portfolio weights."""
        return self.weights.copy()
    
    def get_portfolio_return(self, returns: np.ndarray) -> float:
        """Calculate portfolio return."""
        return np.dot(self.weights, np.mean(returns, axis=1))
    
    def get_portfolio_volatility(self, returns: np.ndarray) -> float:
        """Calculate portfolio volatility."""
        covariance = np.cov(returns)
        return np.sqrt(np.dot(self.weights.T, np.dot(covariance, self.weights)))


def create_portfolio_optimizer(method: OptimizationMethod = OptimizationMethod.QUANTUM_INSPIRED) -> PortfolioOptimizer:
    """Factory function to create portfolio optimizer."""
    return PortfolioOptimizer(method=method)


def create_quantum_portfolio(n_assets: int) -> QuantumPortfolio:
    """Factory function to create quantum portfolio."""
    return QuantumPortfolio(n_assets=n_assets) 