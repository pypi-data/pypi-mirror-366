"""
Financial Applications Module

This module provides quantum-inspired financial modeling capabilities,
including portfolio optimization, risk assessment, and market analysis.
"""

from .portfolio_optimization import (
    PortfolioOptimizer, 
    QuantumPortfolio,
    OptimizationMethod,
    PortfolioResult
)

from .risk_assessment import (
    RiskAnalyzer,
    VaRCalculator,
    StressTesting,
    RiskMetric,
    RiskResult
)

from .market_analysis import (
    MarketAnalyzer,
    QuantumMarketModel,
    MarketModelType,
    MarketAnalysisResult
)

# Additional placeholder classes for future implementation
class OptionPricer:
    """Placeholder for option pricing."""
    pass

class QuantumOptionModel:
    """Placeholder for quantum option models."""
    pass

class AssetAllocator:
    """Placeholder for asset allocation."""
    pass

class QuantumAllocation:
    """Placeholder for quantum asset allocation."""
    pass

class TradingStrategy:
    """Placeholder for trading strategies."""
    pass

class QuantumTrading:
    """Placeholder for quantum trading strategies."""
    pass

class DerivativesPricer:
    """Placeholder for derivatives pricing."""
    pass

class QuantumDerivatives:
    """Placeholder for quantum derivatives models."""
    pass

class FinancialForecaster:
    """Placeholder for financial forecasting."""
    pass

class QuantumForecasting:
    """Placeholder for quantum financial forecasting."""
    pass

__version__ = "1.0.0"
__author__ = "QuantaThread Team"

__all__ = [
    # Portfolio Optimization
    "PortfolioOptimizer",
    "QuantumPortfolio",
    "OptimizationMethod",
    "PortfolioResult",
    
    # Risk Assessment
    "RiskAnalyzer",
    "VaRCalculator",
    "StressTesting",
    "RiskMetric",
    "RiskResult",
    
    # Market Analysis
    "MarketAnalyzer",
    "QuantumMarketModel",
    "MarketModelType",
    "MarketAnalysisResult",
    
    # Option Pricing
    "OptionPricer",
    "QuantumOptionModel",
    
    # Asset Allocation
    "AssetAllocator",
    "QuantumAllocation",
    
    # Trading Strategies
    "TradingStrategy",
    "QuantumTrading",
    
    # Derivatives Pricing
    "DerivativesPricer",
    "QuantumDerivatives",
    
    # Financial Forecasting
    "FinancialForecaster",
    "QuantumForecasting",
] 