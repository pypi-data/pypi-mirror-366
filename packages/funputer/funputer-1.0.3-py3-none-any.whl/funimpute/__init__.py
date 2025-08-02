"""
Simple, intelligent imputation analysis for data science.
"""

__version__ = "1.0.3"
__author__ = "Rajesh Ramachander"

# Simple API for client applications
from .simple_analyzer import (
    SimpleImputationAnalyzer,
    analyze_imputation_requirements,
    analyze_dataframe
)

# Core models for advanced usage
from .models import ColumnMetadata, AnalysisConfig, ImputationSuggestion

# Legacy analyzer for backward compatibility
from .analyzer import ImputationAnalyzer

__all__ = [
    # Simple API (recommended for most users)
    "analyze_imputation_requirements",
    "analyze_dataframe", 
    "SimpleImputationAnalyzer",
    
    # Core models
    "ColumnMetadata",
    "AnalysisConfig", 
    "ImputationSuggestion",
    
    # Advanced/legacy
    "ImputationAnalyzer"
]
