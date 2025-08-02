"""
Imputation method proposal logic based on analysis results.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any
from scipy import stats

from .models import (
    ImputationProposal, ImputationMethod, MissingnessMechanism,
    ColumnMetadata, MissingnessAnalysis, OutlierAnalysis, AnalysisConfig
)
from .exceptions import apply_exception_handling
from .adaptive_thresholds import AdaptiveThresholds, calculate_adaptive_confidence_score


def calculate_confidence_score(
    missingness_analysis: MissingnessAnalysis,
    outlier_analysis: OutlierAnalysis,
    metadata: ColumnMetadata,
    data_series: pd.Series
) -> float:
    """
    Calculate confidence score for the imputation proposal (0-1 scale).
    
    Args:
        missingness_analysis: Results of missingness mechanism analysis
        outlier_analysis: Results of outlier analysis
        metadata: Column metadata
        data_series: The actual data series
        
    Returns:
        Confidence score between 0 and 1
    """
    confidence = 0.5  # Base confidence
    
    # Adjust based on missing percentage
    missing_pct = missingness_analysis.missing_percentage
    if missing_pct < 0.05:  # Less than 5% missing
        confidence += 0.2
    elif missing_pct < 0.20:  # Less than 20% missing
        confidence += 0.1
    elif missing_pct > 0.50:  # More than 50% missing
        confidence -= 0.2
    
    # Adjust based on mechanism certainty
    if missingness_analysis.mechanism == MissingnessMechanism.MCAR:
        if missingness_analysis.p_value is None or missingness_analysis.p_value > 0.1:
            confidence += 0.1  # High certainty of MCAR
    elif missingness_analysis.mechanism == MissingnessMechanism.MAR:
        if missingness_analysis.p_value and missingness_analysis.p_value < 0.01:
            confidence += 0.15  # High certainty of MAR
    
    # Adjust based on data quality
    non_null_count = data_series.count()
    if non_null_count > 100:
        confidence += 0.1
    elif non_null_count < 20:
        confidence -= 0.1
    
    # Adjust based on outlier percentage
    if outlier_analysis.outlier_percentage < 0.05:
        confidence += 0.05
    elif outlier_analysis.outlier_percentage > 0.20:
        confidence -= 0.1
    
    # Adjust based on metadata completeness
    if metadata.business_rule:
        confidence += 0.05
    if metadata.dependent_column:
        confidence += 0.05
    
    # Ensure confidence is within bounds
    return max(0.1, min(1.0, confidence))


def propose_imputation_method(
    column_name: str,
    data_series: pd.Series,
    metadata: ColumnMetadata,
    missingness_analysis: MissingnessAnalysis,
    outlier_analysis: OutlierAnalysis,
    config: AnalysisConfig,
    full_data: pd.DataFrame = None,
    metadata_dict: Dict[str, ColumnMetadata] = None
) -> ImputationProposal:
    """
    Propose the best imputation method based on comprehensive analysis.
    
    Args:
        column_name: Name of the column
        data_series: The data series to analyze
        metadata: Column metadata
        missingness_analysis: Results of missingness analysis
        outlier_analysis: Results of outlier analysis
        config: Analysis configuration
        full_data: Full dataset for adaptive threshold calculation
        metadata_dict: Dictionary of all column metadata for adaptive thresholds
        
    Returns:
        ImputationProposal with method, rationale, and parameters
    """
    # FIRST: Apply exception handling rules
    exception_proposal = apply_exception_handling(
        column_name, data_series, metadata, missingness_analysis, 
        outlier_analysis, config
    )
    
    if exception_proposal is not None:
        return exception_proposal
    
    # Initialize adaptive thresholds if data is available
    adaptive_thresholds = None
    if full_data is not None and metadata_dict is not None:
        adaptive_thresholds = AdaptiveThresholds(full_data, metadata_dict, config)
    
    # Helper function to calculate confidence score
    def get_confidence_score():
        if adaptive_thresholds is not None:
            return calculate_adaptive_confidence_score(
                column_name, missingness_analysis, outlier_analysis, 
                metadata, data_series, adaptive_thresholds
            )
        else:
            return calculate_confidence_score(
                missingness_analysis, outlier_analysis, metadata, data_series
            )
    
    # If no exceptions apply, proceed with normal imputation logic
    missing_pct = missingness_analysis.missing_percentage
    mechanism = missingness_analysis.mechanism
    
    # Handle unique identifier columns (backup check)
    if metadata.unique_flag:
        return ImputationProposal(
            method=ImputationMethod.MANUAL_BACKFILL,
            rationale="Unique identifier column requires manual backfill to maintain data integrity",
            parameters={"strategy": "manual_review"},
            confidence_score=get_confidence_score()
        )
    
    # Handle dependency rule columns (specific calculations)
    if metadata.dependency_rule and metadata.dependent_column:
        return ImputationProposal(
            method=ImputationMethod.BUSINESS_RULE,
            rationale=f"Column has dependency rule on {metadata.dependent_column}: {metadata.dependency_rule}",
            parameters={
                "dependent_column": metadata.dependent_column,
                "rule": metadata.dependency_rule,
                "rule_type": "dependency"
            },
            confidence_score=get_confidence_score()
        )
    
    # Handle business rule columns (general constraints)
    if metadata.business_rule and metadata.dependent_column:
        return ImputationProposal(
            method=ImputationMethod.BUSINESS_RULE,
            rationale=f"Column has business rule dependency on {metadata.dependent_column}: {metadata.business_rule}",
            parameters={
                "dependent_column": metadata.dependent_column,
                "rule": metadata.business_rule,
                "rule_type": "business"
            },
            confidence_score=get_confidence_score()
        )
    
    # Handle high missing percentage (>80%)
    if missing_pct > config.missing_threshold:
        return ImputationProposal(
            method=ImputationMethod.CONSTANT_MISSING,
            rationale=f"Very high missing percentage ({missing_pct:.1%}) suggests systematic absence - use constant 'Missing'",
            parameters={"fill_value": "Missing"},
            confidence_score=get_confidence_score()
        )
    
    # Method selection based on data type and mechanism
    if metadata.data_type == 'categorical' or metadata.data_type == 'string':
        if mechanism == MissingnessMechanism.MCAR:
            return ImputationProposal(
                method=ImputationMethod.MODE,
                rationale="Categorical data with MCAR mechanism - use most frequent category",
                parameters={"strategy": "most_frequent"},
                confidence_score=calculate_confidence_score(
                    missingness_analysis, outlier_analysis, metadata, data_series
                )
            )
        else:  # MAR
            return ImputationProposal(
                method=ImputationMethod.KNN,
                rationale=f"Categorical data with MAR mechanism (related to {', '.join(missingness_analysis.related_columns[:2])}) - use kNN",
                parameters={
                    "n_neighbors": min(5, max(3, data_series.count() // 20)),
                    "weights": "distance"
                },
                confidence_score=calculate_confidence_score(
                    missingness_analysis, outlier_analysis, metadata, data_series
                )
            )
    
    elif metadata.data_type in ['integer', 'float']:
        # Check for skewness to decide between mean and median
        non_null_data = data_series.dropna()
        if len(non_null_data) > 3:
            skewness = abs(stats.skew(non_null_data))
        else:
            skewness = 0
        
        # Get adaptive skewness threshold
        skewness_threshold = adaptive_thresholds.get_adaptive_skewness_threshold(column_name) if adaptive_thresholds else config.skewness_threshold
        
        if mechanism == MissingnessMechanism.MCAR:
            if skewness > skewness_threshold:
                return ImputationProposal(
                    method=ImputationMethod.MEDIAN,
                    rationale=f"Numeric data with MCAR mechanism and high skewness ({skewness:.2f}) - use median",
                    parameters={"strategy": "median"},
                    confidence_score=calculate_confidence_score(
                        missingness_analysis, outlier_analysis, metadata, data_series
                    )
                )
            else:
                return ImputationProposal(
                    method=ImputationMethod.MEAN,
                    rationale=f"Numeric data with MCAR mechanism and low skewness ({skewness:.2f}) - use mean",
                    parameters={"strategy": "mean"},
                    confidence_score=calculate_confidence_score(
                        missingness_analysis, outlier_analysis, metadata, data_series
                    )
                )
        else:  # MAR
            # Choose between regression and kNN based on data size and relationships
            if len(non_null_data) > 50 and len(missingness_analysis.related_columns) > 0:
                return ImputationProposal(
                    method=ImputationMethod.REGRESSION,
                    rationale=f"Numeric data with MAR mechanism - use regression with predictors: {', '.join(missingness_analysis.related_columns[:2])}",
                    parameters={
                        "predictors": missingness_analysis.related_columns[:3],
                        "estimator": "BayesianRidge"
                    },
                    confidence_score=calculate_confidence_score(
                        missingness_analysis, outlier_analysis, metadata, data_series
                    )
                )
            else:
                return ImputationProposal(
                    method=ImputationMethod.KNN,
                    rationale=f"Numeric data with MAR mechanism - use kNN (insufficient data for regression)",
                    parameters={
                        "n_neighbors": min(5, max(3, len(non_null_data) // 10)),
                        "weights": "distance"
                    },
                    confidence_score=calculate_confidence_score(
                        missingness_analysis, outlier_analysis, metadata, data_series
                    )
                )
    
    elif metadata.data_type == 'datetime':
        if mechanism == MissingnessMechanism.MCAR:
            return ImputationProposal(
                method=ImputationMethod.FORWARD_FILL,
                rationale="Datetime data with MCAR mechanism - use forward fill to maintain temporal continuity",
                parameters={"method": "ffill", "limit": 3},
                confidence_score=calculate_confidence_score(
                    missingness_analysis, outlier_analysis, metadata, data_series
                )
            )
        else:
            return ImputationProposal(
                method=ImputationMethod.BUSINESS_RULE,
                rationale="Datetime data with MAR mechanism - requires business logic for temporal imputation",
                parameters={"strategy": "business_logic_required"},
                confidence_score=calculate_confidence_score(
                    missingness_analysis, outlier_analysis, metadata, data_series
                )
            )
    
    elif metadata.data_type == 'boolean':
        return ImputationProposal(
            method=ImputationMethod.MODE,
            rationale="Boolean data - use most frequent value",
            parameters={"strategy": "most_frequent"},
            confidence_score=get_confidence_score()
        )
    
    # Default fallback
    return ImputationProposal(
        method=ImputationMethod.CONSTANT_MISSING,
        rationale=f"Unknown data type ({metadata.data_type}) - use constant 'Missing' as safe fallback",
        parameters={"fill_value": "Missing"},
        confidence_score=0.3
    )
