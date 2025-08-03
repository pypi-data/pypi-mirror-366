"""
Risk Assessment Module

This module provides quantum-inspired risk assessment tools,
including Value at Risk (VaR), stress testing, and risk metrics.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
from dataclasses import dataclass
from enum import Enum
import logging
from scipy import stats
from scipy.optimize import minimize

logger = logging.getLogger(__name__)


class RiskMetric(Enum):
    """Risk metrics enumeration."""
    VAR = "var"
    CVAR = "cvar"
    VOLATILITY = "volatility"
    BETA = "beta"
    SHARPE_RATIO = "sharpe_ratio"
    MAX_DRAWDOWN = "max_drawdown"


@dataclass
class RiskResult:
    """Risk assessment result."""
    
    metric: RiskMetric
    value: float
    confidence_level: float
    time_horizon: int
    method: str
    additional_info: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metric": self.metric.value,
            "value": self.value,
            "confidence_level": self.confidence_level,
            "time_horizon": self.time_horizon,
            "method": self.method,
            "additional_info": self.additional_info
        }


class RiskAnalyzer:
    """Quantum-inspired risk analyzer."""
    
    def __init__(self, 
                 confidence_level: float = 0.95,
                 time_horizon: int = 1,
                 method: str = "quantum_inspired"):
        """
        Initialize risk analyzer.
        
        Args:
            confidence_level: Confidence level for risk metrics
            time_horizon: Time horizon in periods
            method: Risk calculation method
        """
        self.confidence_level = confidence_level
        self.time_horizon = time_horizon
        self.method = method
        self.returns = None
        self.quantum_parameters = None
        
    def fit(self, returns: np.ndarray):
        """
        Fit the risk analyzer with historical returns.
        
        Args:
            returns: Historical returns (n_assets, n_periods)
        """
        self.returns = returns
        
        # Initialize quantum parameters for risk modeling
        n_assets = returns.shape[0]
        self.quantum_parameters = np.random.uniform(0, 2*np.pi, n_assets * 3)
        
    def calculate_var(self, portfolio_weights: np.ndarray) -> RiskResult:
        """
        Calculate Value at Risk (VaR).
        
        Args:
            portfolio_weights: Portfolio weights
            
        Returns:
            VaR result
        """
        if self.returns is None:
            raise ValueError("Must call fit() before calculate_var()")
        
        # Calculate portfolio returns
        portfolio_returns = np.dot(portfolio_weights, self.returns)
        
        if self.method == "quantum_inspired":
            var_value = self._quantum_var(portfolio_returns)
        else:
            var_value = self._standard_var(portfolio_returns)
        
        return RiskResult(
            metric=RiskMetric.VAR,
            value=var_value,
            confidence_level=self.confidence_level,
            time_horizon=self.time_horizon,
            method=self.method,
            additional_info={"portfolio_returns_mean": np.mean(portfolio_returns),
                           "portfolio_returns_std": np.std(portfolio_returns)}
        )
    
    def calculate_cvar(self, portfolio_weights: np.ndarray) -> RiskResult:
        """
        Calculate Conditional Value at Risk (CVaR).
        
        Args:
            portfolio_weights: Portfolio weights
            
        Returns:
            CVaR result
        """
        if self.returns is None:
            raise ValueError("Must call fit() before calculate_cvar()")
        
        # Calculate portfolio returns
        portfolio_returns = np.dot(portfolio_weights, self.returns)
        
        if self.method == "quantum_inspired":
            cvar_value = self._quantum_cvar(portfolio_returns)
        else:
            cvar_value = self._standard_cvar(portfolio_returns)
        
        return RiskResult(
            metric=RiskMetric.CVAR,
            value=cvar_value,
            confidence_level=self.confidence_level,
            time_horizon=self.time_horizon,
            method=self.method,
            additional_info={"portfolio_returns_mean": np.mean(portfolio_returns),
                           "portfolio_returns_std": np.std(portfolio_returns)}
        )
    
    def calculate_volatility(self, portfolio_weights: np.ndarray) -> RiskResult:
        """
        Calculate portfolio volatility.
        
        Args:
            portfolio_weights: Portfolio weights
            
        Returns:
            Volatility result
        """
        if self.returns is None:
            raise ValueError("Must call fit() before calculate_volatility()")
        
        # Calculate covariance matrix
        covariance = np.cov(self.returns)
        
        # Calculate portfolio volatility
        volatility = np.sqrt(np.dot(portfolio_weights.T, np.dot(covariance, portfolio_weights)))
        
        return RiskResult(
            metric=RiskMetric.VOLATILITY,
            value=volatility,
            confidence_level=self.confidence_level,
            time_horizon=self.time_horizon,
            method="standard",
            additional_info={"covariance_matrix": covariance.tolist()}
        )
    
    def _quantum_var(self, returns: np.ndarray) -> float:
        """Quantum-inspired VaR calculation."""
        # Apply quantum-inspired transformation to returns
        quantum_returns = self._apply_quantum_transformation(returns)
        
        # Calculate VaR using transformed returns
        var_quantile = 1 - self.confidence_level
        var_value = np.percentile(quantum_returns, var_quantile * 100)
        
        return abs(var_value)
    
    def _quantum_cvar(self, returns: np.ndarray) -> float:
        """Quantum-inspired CVaR calculation."""
        # Apply quantum-inspired transformation to returns
        quantum_returns = self._apply_quantum_transformation(returns)
        
        # Calculate CVaR using transformed returns
        var_quantile = 1 - self.confidence_level
        var_threshold = np.percentile(quantum_returns, var_quantile * 100)
        
        # Calculate expected value of returns below VaR threshold
        tail_returns = quantum_returns[quantum_returns <= var_threshold]
        cvar_value = np.mean(tail_returns) if len(tail_returns) > 0 else var_threshold
        
        return abs(cvar_value)
    
    def _standard_var(self, returns: np.ndarray) -> float:
        """Standard VaR calculation."""
        var_quantile = 1 - self.confidence_level
        var_value = np.percentile(returns, var_quantile * 100)
        return abs(var_value)
    
    def _standard_cvar(self, returns: np.ndarray) -> float:
        """Standard CVaR calculation."""
        var_quantile = 1 - self.confidence_level
        var_threshold = np.percentile(returns, var_quantile * 100)
        
        # Calculate expected value of returns below VaR threshold
        tail_returns = returns[returns <= var_threshold]
        cvar_value = np.mean(tail_returns) if len(tail_returns) > 0 else var_threshold
        
        return abs(cvar_value)
    
    def _apply_quantum_transformation(self, returns: np.ndarray) -> np.ndarray:
        """Apply quantum-inspired transformation to returns."""
        # Use quantum parameters to create non-linear transformation
        n_assets = len(self.quantum_parameters) // 3
        
        # Apply quantum rotation and entanglement
        transformed_returns = returns.copy()
        for i in range(n_assets):
            if i < len(returns):
                # Apply quantum rotation
                rotation = self.quantum_parameters[i * 3:(i + 1) * 3]
                transformed_returns[i] = returns[i] * np.cos(rotation[0]) + np.sin(rotation[1]) * np.cos(rotation[2])
        
        return transformed_returns


class VaRCalculator:
    """Value at Risk calculator with multiple methods."""
    
    def __init__(self, confidence_level: float = 0.95):
        """
        Initialize VaR calculator.
        
        Args:
            confidence_level: Confidence level for VaR calculation
        """
        self.confidence_level = confidence_level
        
    def historical_var(self, returns: np.ndarray) -> float:
        """
        Calculate historical VaR.
        
        Args:
            returns: Historical returns
            
        Returns:
            Historical VaR
        """
        var_quantile = 1 - self.confidence_level
        var_value = np.percentile(returns, var_quantile * 100)
        return abs(var_value)
    
    def parametric_var(self, returns: np.ndarray, distribution: str = "normal") -> float:
        """
        Calculate parametric VaR.
        
        Args:
            returns: Historical returns
            distribution: Assumed distribution ("normal", "t", "skewed")
            
        Returns:
            Parametric VaR
        """
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        if distribution == "normal":
            z_score = stats.norm.ppf(1 - self.confidence_level)
        elif distribution == "t":
            # Use t-distribution with degrees of freedom
            df = len(returns) - 1
            z_score = stats.t.ppf(1 - self.confidence_level, df)
        else:
            raise ValueError(f"Unsupported distribution: {distribution}")
        
        var_value = mean_return - z_score * std_return
        return abs(var_value)
    
    def monte_carlo_var(self, returns: np.ndarray, n_simulations: int = 10000) -> float:
        """
        Calculate Monte Carlo VaR.
        
        Args:
            returns: Historical returns
            n_simulations: Number of Monte Carlo simulations
            
        Returns:
            Monte Carlo VaR
        """
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        # Generate random returns
        simulated_returns = np.random.normal(mean_return, std_return, n_simulations)
        
        # Calculate VaR from simulated returns
        var_quantile = 1 - self.confidence_level
        var_value = np.percentile(simulated_returns, var_quantile * 100)
        
        return abs(var_value)


class StressTesting:
    """Stress testing framework for portfolio risk assessment."""
    
    def __init__(self, scenarios: Optional[Dict[str, Dict[str, float]]] = None):
        """
        Initialize stress testing.
        
        Args:
            scenarios: Dictionary of stress scenarios
        """
        self.scenarios = scenarios or self._default_scenarios()
        
    def _default_scenarios(self) -> Dict[str, Dict[str, float]]:
        """Default stress testing scenarios."""
        return {
            "market_crash": {
                "equity_shock": -0.20,
                "bond_shock": 0.05,
                "currency_shock": -0.10,
                "volatility_shock": 2.0
            },
            "interest_rate_spike": {
                "equity_shock": -0.05,
                "bond_shock": -0.15,
                "currency_shock": 0.02,
                "volatility_shock": 1.5
            },
            "currency_crisis": {
                "equity_shock": -0.10,
                "bond_shock": -0.05,
                "currency_shock": -0.25,
                "volatility_shock": 2.5
            },
            "quantum_inspired": {
                "equity_shock": -0.15,
                "bond_shock": 0.03,
                "currency_shock": -0.08,
                "volatility_shock": 1.8
            }
        }
    
    def run_stress_test(self, 
                       portfolio_weights: np.ndarray,
                       asset_returns: np.ndarray,
                       scenario_name: str = "market_crash") -> Dict[str, float]:
        """
        Run stress test on portfolio.
        
        Args:
            portfolio_weights: Portfolio weights
            asset_returns: Historical asset returns
            scenario_name: Name of stress scenario
            
        Returns:
            Stress test results
        """
        if scenario_name not in self.scenarios:
            raise ValueError(f"Unknown scenario: {scenario_name}")
        
        scenario = self.scenarios[scenario_name]
        
        # Apply stress shocks to returns
        stressed_returns = self._apply_stress_shocks(asset_returns, scenario)
        
        # Calculate stressed portfolio return
        stressed_portfolio_return = np.dot(portfolio_weights, np.mean(stressed_returns, axis=1))
        
        # Calculate stressed portfolio volatility
        stressed_covariance = np.cov(stressed_returns)
        stressed_volatility = np.sqrt(np.dot(portfolio_weights.T, np.dot(stressed_covariance, portfolio_weights)))
        
        # Calculate stressed VaR
        portfolio_returns = np.dot(portfolio_weights, stressed_returns)
        stressed_var = np.percentile(portfolio_returns, 5)  # 95% VaR
        
        return {
            "scenario": scenario_name,
            "stressed_return": stressed_portfolio_return,
            "stressed_volatility": stressed_volatility,
            "stressed_var": abs(stressed_var),
            "return_impact": stressed_portfolio_return - np.dot(portfolio_weights, np.mean(asset_returns, axis=1)),
            "volatility_impact": stressed_volatility - np.sqrt(np.dot(portfolio_weights.T, np.dot(np.cov(asset_returns), portfolio_weights)))
        }
    
    def _apply_stress_shocks(self, returns: np.ndarray, scenario: Dict[str, float]) -> np.ndarray:
        """Apply stress shocks to returns."""
        stressed_returns = returns.copy()
        
        # Apply shocks based on scenario
        for shock_type, shock_value in scenario.items():
            if shock_type == "equity_shock":
                # Apply to equity-like assets (first half)
                n_equity = returns.shape[0] // 2
                stressed_returns[:n_equity] *= (1 + shock_value)
            elif shock_type == "bond_shock":
                # Apply to bond-like assets (second half)
                n_bonds = returns.shape[0] - returns.shape[0] // 2
                stressed_returns[-n_bonds:] *= (1 + shock_value)
            elif shock_type == "volatility_shock":
                # Increase volatility
                stressed_returns *= np.sqrt(shock_value)
        
        return stressed_returns
    
    def add_custom_scenario(self, name: str, scenario: Dict[str, float]):
        """Add custom stress scenario."""
        self.scenarios[name] = scenario


def create_risk_analyzer(confidence_level: float = 0.95) -> RiskAnalyzer:
    """Factory function to create risk analyzer."""
    return RiskAnalyzer(confidence_level=confidence_level)


def create_var_calculator(confidence_level: float = 0.95) -> VaRCalculator:
    """Factory function to create VaR calculator."""
    return VaRCalculator(confidence_level=confidence_level)


def create_stress_testing() -> StressTesting:
    """Factory function to create stress testing framework."""
    return StressTesting() 