"""
Unit tests for exception handling in imputation suggestions.
"""

import pytest
import pandas as pd
import numpy as np

from funimpute.models import (
    ColumnMetadata, AnalysisConfig, MissingnessAnalysis, OutlierAnalysis,
    MissingnessMechanism, OutlierHandling, ImputationMethod
)
from funimpute.exceptions import (
    check_no_missing_values, check_unique_identifier, check_all_values_missing,
    check_mnar_without_business_rule, check_metadata_validation_failure,
    check_skip_column, apply_exception_handling, should_skip_column
)


class TestExceptionHandling:
    """Test exception handling rules for imputation suggestions."""
    
    def test_no_missing_values_exception(self):
        """Test exception for columns with no missing values."""
        missingness_analysis = MissingnessAnalysis(
            missing_count=0,
            missing_percentage=0.0,
            mechanism=MissingnessMechanism.MCAR,
            test_statistic=None,
            p_value=None,
            related_columns=[],
            rationale="No missing values"
        )
        
        exception = check_no_missing_values(missingness_analysis)
        assert exception is not None
        assert exception.method == ImputationMethod.NO_ACTION_NEEDED
        assert "no imputation required" in exception.rationale.lower()
        assert exception.confidence == 1.0
    
    def test_unique_identifier_exception(self):
        """Test exception for unique identifier columns."""
        metadata = ColumnMetadata(
            column_name="id",
            data_type="integer",
            unique_flag=True
        )
        
        exception = check_unique_identifier(metadata)
        assert exception is not None
        assert exception.method == ImputationMethod.MANUAL_BACKFILL
        assert "unique ids cannot be auto-imputed" in exception.rationale.lower()
        assert exception.confidence == 0.9
    
    def test_all_values_missing_exception(self):
        """Test exception for columns where all values are missing."""
        data_series = pd.Series([np.nan, np.nan, np.nan, np.nan])
        missingness_analysis = MissingnessAnalysis(
            missing_count=4,
            missing_percentage=1.0,
            mechanism=MissingnessMechanism.MCAR,
            test_statistic=None,
            p_value=None,
            related_columns=[],
            rationale="All values missing"
        )
        
        exception = check_all_values_missing(data_series, missingness_analysis)
        assert exception is not None
        assert exception.method == ImputationMethod.MANUAL_BACKFILL
        assert "no observed values" in exception.rationale.lower()
        assert exception.confidence == 0.8
    
    def test_mnar_without_business_rule_exception(self):
        """Test exception for MNAR mechanism without business rule."""
        missingness_analysis = MissingnessAnalysis(
            missing_count=10,
            missing_percentage=0.1,
            mechanism=MissingnessMechanism.MNAR,
            test_statistic=None,
            p_value=None,
            related_columns=[],
            rationale="MNAR detected"
        )
        
        metadata = ColumnMetadata(
            column_name="test_col",
            data_type="float",
            business_rule=None  # No business rule
        )
        
        exception = check_mnar_without_business_rule(missingness_analysis, metadata)
        assert exception is not None
        assert exception.method == ImputationMethod.MANUAL_BACKFILL
        assert "mnar" in exception.rationale.lower()
        assert "no domain rule" in exception.rationale.lower()
        assert exception.confidence == 0.7
    
    def test_unknown_mechanism_without_business_rule_exception(self):
        """Test exception for UNKNOWN mechanism without business rule."""
        missingness_analysis = MissingnessAnalysis(
            missing_count=10,
            missing_percentage=0.1,
            mechanism=MissingnessMechanism.UNKNOWN,
            test_statistic=None,
            p_value=None,
            related_columns=[],
            rationale="Unknown mechanism"
        )
        
        metadata = ColumnMetadata(
            column_name="test_col",
            data_type="float",
            business_rule=None
        )
        
        exception = check_mnar_without_business_rule(missingness_analysis, metadata)
        assert exception is not None
        assert exception.method == ImputationMethod.MANUAL_BACKFILL
    
    def test_metadata_validation_failure_invalid_data_type(self):
        """Test exception for invalid data type in metadata."""
        metadata = ColumnMetadata(
            column_name="test_col",
            data_type="invalid_type"  # Invalid data type
        )
        data_series = pd.Series([1, 2, 3, 4, 5])
        
        exception = check_metadata_validation_failure(metadata, data_series)
        assert exception is not None
        assert exception.method == ImputationMethod.ERROR_INVALID_METADATA
        assert "invalid data type" in exception.rationale.lower()
        assert exception.confidence == 0.0
    
    def test_metadata_validation_failure_invalid_constraints(self):
        """Test exception for invalid min/max constraints."""
        metadata = ColumnMetadata(
            column_name="test_col",
            data_type="float",
            min_value=100.0,
            max_value=50.0  # min > max
        )
        data_series = pd.Series([1, 2, 3, 4, 5])
        
        exception = check_metadata_validation_failure(metadata, data_series)
        assert exception is not None
        assert exception.method == ImputationMethod.ERROR_INVALID_METADATA
        assert "invalid constraints" in exception.rationale.lower()
    
    def test_metadata_validation_failure_empty_column_name(self):
        """Test exception for empty column name."""
        metadata = ColumnMetadata(
            column_name="",  # Empty column name
            data_type="float"
        )
        data_series = pd.Series([1, 2, 3, 4, 5])
        
        exception = check_metadata_validation_failure(metadata, data_series)
        assert exception is not None
        assert exception.method == ImputationMethod.ERROR_INVALID_METADATA
        assert "column name is missing" in exception.rationale.lower()
    
    def test_metadata_validation_failure_data_type_mismatch(self):
        """Test exception for data type mismatch."""
        metadata = ColumnMetadata(
            column_name="test_col",
            data_type="integer"
        )
        data_series = pd.Series(["a", "b", "c", "d"])  # String data but metadata says integer
        
        exception = check_metadata_validation_failure(metadata, data_series)
        assert exception is not None
        assert exception.method == ImputationMethod.ERROR_INVALID_METADATA
        assert "data type mismatch" in exception.rationale.lower()
    
    def test_skip_column_check(self):
        """Test skip column functionality."""
        config = AnalysisConfig(skip_columns=["skip_me", "also_skip"])
        
        # Column in skip list
        assert check_skip_column("skip_me", config) is True
        assert should_skip_column("skip_me", config) is True
        
        # Column not in skip list
        assert check_skip_column("keep_me", config) is None
        assert should_skip_column("keep_me", config) is False
    
    def test_apply_exception_handling_priority_order(self):
        """Test that exception handling applies rules in correct priority order."""
        config = AnalysisConfig()
        
        # Test no missing values (should be highest priority after metadata validation)
        data_series = pd.Series([1, 2, 3, 4, 5])  # No missing values
        metadata = ColumnMetadata(
            column_name="test_col",
            data_type="integer",
            unique_flag=True  # This would normally trigger unique ID exception
        )
        
        missingness_analysis = MissingnessAnalysis(
            missing_count=0,
            missing_percentage=0.0,
            mechanism=MissingnessMechanism.MCAR,
            test_statistic=None,
            p_value=None,
            related_columns=[],
            rationale="No missing values"
        )
        
        outlier_analysis = OutlierAnalysis(
            outlier_count=0,
            outlier_percentage=0.0,
            lower_bound=None,
            upper_bound=None,
            outlier_values=[],
            handling_strategy=OutlierHandling.LEAVE_AS_IS,
            rationale="No outliers"
        )
        
        proposal = apply_exception_handling(
            "test_col", data_series, metadata, missingness_analysis, 
            outlier_analysis, config
        )
        
        # Should return "No action needed" instead of "Manual Backfill" for unique ID
        assert proposal is not None
        assert proposal.method == ImputationMethod.NO_ACTION_NEEDED
    
    def test_apply_exception_handling_unique_id_with_missing_values(self):
        """Test unique ID exception when there are missing values."""
        config = AnalysisConfig()
        
        data_series = pd.Series([1, 2, np.nan, 4, 5])  # Has missing values
        metadata = ColumnMetadata(
            column_name="id_col",
            data_type="integer",
            unique_flag=True
        )
        
        missingness_analysis = MissingnessAnalysis(
            missing_count=1,
            missing_percentage=0.2,
            mechanism=MissingnessMechanism.MCAR,
            test_statistic=None,
            p_value=None,
            related_columns=[],
            rationale="Some missing values"
        )
        
        outlier_analysis = OutlierAnalysis(
            outlier_count=0,
            outlier_percentage=0.0,
            lower_bound=None,
            upper_bound=None,
            outlier_values=[],
            handling_strategy=OutlierHandling.LEAVE_AS_IS,
            rationale="No outliers"
        )
        
        proposal = apply_exception_handling(
            "id_col", data_series, metadata, missingness_analysis, 
            outlier_analysis, config
        )
        
        # Should return Manual Backfill for unique ID
        assert proposal is not None
        assert proposal.method == ImputationMethod.MANUAL_BACKFILL
        assert "unique" in proposal.rationale.lower()
    
    def test_no_exception_applies(self):
        """Test case where no exceptions apply and normal processing should continue."""
        config = AnalysisConfig()
        
        data_series = pd.Series([1, 2, np.nan, 4, 5])  # Normal case with some missing
        metadata = ColumnMetadata(
            column_name="normal_col",
            data_type="integer",
            unique_flag=False,
            business_rule="Must be positive"  # Has business rule
        )
        
        missingness_analysis = MissingnessAnalysis(
            missing_count=1,
            missing_percentage=0.2,
            mechanism=MissingnessMechanism.MAR,  # Not MNAR/UNKNOWN
            test_statistic=0.5,
            p_value=0.03,
            related_columns=["other_col"],
            rationale="MAR mechanism"
        )
        
        outlier_analysis = OutlierAnalysis(
            outlier_count=0,
            outlier_percentage=0.0,
            lower_bound=None,
            upper_bound=None,
            outlier_values=[],
            handling_strategy=OutlierHandling.LEAVE_AS_IS,
            rationale="No outliers"
        )
        
        proposal = apply_exception_handling(
            "normal_col", data_series, metadata, missingness_analysis, 
            outlier_analysis, config
        )
        
        # Should return None to indicate normal processing should continue
        assert proposal is None
