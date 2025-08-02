"""
Unit tests for data models and validation.
"""

import pytest
from pydantic import ValidationError

from funimpute.models import (
    AnalysisConfig, ColumnMetadata, ImputationSuggestion,
    MissingnessMechanism, ImputationMethod, OutlierHandling
)


class TestAnalysisConfig:
    """Test AnalysisConfig validation and defaults."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = AnalysisConfig()
        assert config.iqr_multiplier == 1.5
        assert config.outlier_percentage_threshold == 0.05
        assert config.correlation_threshold == 0.3
        assert config.metrics_port == 8001
    
    def test_valid_config(self):
        """Test valid configuration parameters."""
        config = AnalysisConfig(
            iqr_multiplier=2.0,
            outlier_percentage_threshold=0.1,
            metrics_port=8002
        )
        assert config.iqr_multiplier == 2.0
        assert config.outlier_percentage_threshold == 0.1
        assert config.metrics_port == 8002
    
    def test_invalid_iqr_multiplier(self):
        """Test validation of IQR multiplier."""
        with pytest.raises(ValidationError):
            AnalysisConfig(iqr_multiplier=0.0)
        
        with pytest.raises(ValidationError):
            AnalysisConfig(iqr_multiplier=-1.0)
    
    def test_invalid_port(self):
        """Test validation of metrics port."""
        with pytest.raises(ValidationError):
            AnalysisConfig(metrics_port=80)  # Too low
        
        with pytest.raises(ValidationError):
            AnalysisConfig(metrics_port=70000)  # Too high


class TestColumnMetadata:
    """Test ColumnMetadata dataclass."""
    
    def test_basic_metadata(self):
        """Test basic metadata creation."""
        metadata = ColumnMetadata(
            column_name="test_col",
            data_type="integer"
        )
        assert metadata.column_name == "test_col"
        assert metadata.data_type == "integer"
        assert metadata.unique_flag is False
    
    def test_full_metadata(self):
        """Test metadata with all fields."""
        metadata = ColumnMetadata(
            column_name="price",
            data_type="float",
            min_value=0.0,
            max_value=1000.0,
            unique_flag=False,
            dependent_column="category",
            business_rule="Must be positive",
            description="Product price"
        )
        assert metadata.min_value == 0.0
        assert metadata.max_value == 1000.0
        assert metadata.business_rule == "Must be positive"


class TestImputationSuggestion:
    """Test ImputationSuggestion functionality."""
    
    def test_suggestion_creation(self):
        """Test creating imputation suggestion."""
        suggestion = ImputationSuggestion(
            column="test_col",
            missing_count=10,
            missing_percentage=0.1,
            mechanism="MCAR",
            proposed_method="Median",
            rationale="Low skewness",
            outlier_count=5,
            outlier_percentage=0.05,
            outlier_handling="Cap to bounds",
            outlier_rationale="Within business rules",
            confidence_score=0.8
        )
        assert suggestion.column == "test_col"
        assert suggestion.confidence_score == 0.8
    
    def test_to_dict_conversion(self):
        """Test conversion to dictionary for CSV output."""
        suggestion = ImputationSuggestion(
            column="test_col",
            missing_count=10,
            missing_percentage=0.1234,
            mechanism="MCAR",
            proposed_method="Median",
            rationale="Test rationale",
            outlier_count=5,
            outlier_percentage=0.0567,
            outlier_handling="Cap to bounds",
            outlier_rationale="Test outlier rationale",
            confidence_score=0.789
        )
        
        result = suggestion.to_dict()
        assert result['Column'] == "test_col"
        assert result['Missing_%'] == 12.34  # Rounded percentage
        assert result['Outlier_%'] == 5.67   # Rounded percentage
        assert result['Confidence_Score'] == 0.789


class TestEnums:
    """Test enum definitions."""
    
    def test_missingness_mechanism_enum(self):
        """Test MissingnessMechanism enum values."""
        assert MissingnessMechanism.MCAR.value == "MCAR"
        assert MissingnessMechanism.MAR.value == "MAR"
        assert MissingnessMechanism.MNAR.value == "MNAR"
        assert MissingnessMechanism.UNKNOWN.value == "Unknown"
    
    def test_imputation_method_enum(self):
        """Test ImputationMethod enum values."""
        assert ImputationMethod.MEDIAN.value == "Median"
        assert ImputationMethod.REGRESSION.value == "Regression"
        assert ImputationMethod.BUSINESS_RULE.value == "Business Rule"
    
    def test_outlier_handling_enum(self):
        """Test OutlierHandling enum values."""
        assert OutlierHandling.CAP_TO_BOUNDS.value == "Cap to bounds"
        assert OutlierHandling.CONVERT_TO_NAN.value == "Convert to NaN"
        assert OutlierHandling.LEAVE_AS_IS.value == "Leave as is"
