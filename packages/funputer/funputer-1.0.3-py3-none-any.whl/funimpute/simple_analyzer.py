"""
Simple imputation analyzer for client applications.
Clean, lightweight interface focused on core functionality.
"""

import time
import logging
from typing import List, Dict, Any, Union
import pandas as pd

from .models import (
    ColumnMetadata, AnalysisConfig, ImputationSuggestion
)
from .io import load_metadata, load_data
from .exceptions import should_skip_column
from .outliers import analyze_outliers
from .mechanism import analyze_missingness_mechanism
from .proposal import propose_imputation_method

# Set up simple logging
logger = logging.getLogger(__name__)


class SimpleImputationAnalyzer:
    """
    Lightweight imputation analyzer for client applications.
    
    Focuses on core functionality:
    - Intelligent imputation recommendations
    - Adaptive thresholds
    - Business rule integration
    - Simple, fast API
    """
    
    def __init__(self, config: AnalysisConfig = None):
        """Initialize analyzer with configuration."""
        self.config = config or AnalysisConfig()
        
    def analyze(
        self, 
        metadata_path: str, 
        data_path: str
    ) -> List[ImputationSuggestion]:
        """
        Analyze dataset and return imputation suggestions.
        
        Args:
            metadata_path: Path to metadata CSV file
            data_path: Path to data CSV file
            
        Returns:
            List of ImputationSuggestion objects
        """
        logger.info(f"Analyzing dataset: {data_path}")
        start_time = time.time()
        
        # Load metadata and data
        metadata_list = load_metadata(metadata_path)
        if isinstance(metadata_list, list):
            metadata_dict = {meta.column_name: meta for meta in metadata_list}
        else:
            # Handle enterprise metadata format
            from .io import convert_enterprise_to_legacy
            legacy_metadata = convert_enterprise_to_legacy(metadata_list)
            metadata_dict = {meta.column_name: meta for meta in legacy_metadata}
            metadata_list = legacy_metadata
        
        data = load_data(data_path, metadata_list)
        
        # Analyze each column
        suggestions = []
        for metadata in metadata_list:
            column_name = metadata.column_name
            
            # Skip if column doesn't exist or should be skipped
            if column_name not in data.columns:
                logger.warning(f"Column {column_name} not found in data - skipping")
                continue
                
            if should_skip_column(column_name, self.config):
                logger.info(f"Skipping column {column_name} per configuration")
                continue
            
            # Analyze single column
            data_series = data[column_name]
            
            # Step 1: Outlier analysis
            outlier_analysis = analyze_outliers(data_series, metadata, self.config)
            
            # Step 2: Missingness mechanism analysis
            missingness_analysis = analyze_missingness_mechanism(
                column_name, data, metadata_dict, self.config
            )
            
            # Step 3: Imputation method proposal
            imputation_proposal = propose_imputation_method(
                column_name, data_series, metadata, missingness_analysis, 
                outlier_analysis, self.config, data, metadata_dict
            )
            
            # Create suggestion
            suggestion = ImputationSuggestion(
                column_name=column_name,
                missing_count=missingness_analysis.missing_count,
                missing_percentage=missingness_analysis.missing_percentage,
                mechanism=missingness_analysis.mechanism.value,
                proposed_method=imputation_proposal.method.value,
                rationale=imputation_proposal.rationale,
                outlier_count=outlier_analysis.outlier_count,
                outlier_percentage=outlier_analysis.outlier_percentage,
                outlier_handling=outlier_analysis.handling_strategy.value,
                outlier_rationale=outlier_analysis.rationale,
                confidence_score=imputation_proposal.confidence_score
            )
            
            suggestions.append(suggestion)
        
        duration = time.time() - start_time
        logger.info(f"Analysis completed in {duration:.2f}s - {len(suggestions)} suggestions")
        
        return suggestions
    
    def analyze_dataframe(
        self,
        data: pd.DataFrame,
        metadata: Union[List[ColumnMetadata], Dict[str, ColumnMetadata]]
    ) -> List[ImputationSuggestion]:
        """
        Analyze DataFrame directly with metadata objects.
        
        Args:
            data: Pandas DataFrame to analyze
            metadata: List or dict of ColumnMetadata objects
            
        Returns:
            List of ImputationSuggestion objects
        """
        logger.info(f"Analyzing DataFrame with {len(data)} rows, {len(data.columns)} columns")
        start_time = time.time()
        
        # Normalize metadata to dict format
        if isinstance(metadata, list):
            metadata_dict = {meta.column_name: meta for meta in metadata}
            metadata_list = metadata
        else:
            metadata_dict = metadata
            metadata_list = list(metadata.values())
        
        # Analyze each column
        suggestions = []
        for meta in metadata_list:
            column_name = meta.column_name
            
            # Skip if column doesn't exist or should be skipped
            if column_name not in data.columns:
                logger.warning(f"Column {column_name} not found in data - skipping")
                continue
                
            if should_skip_column(column_name, self.config):
                logger.info(f"Skipping column {column_name} per configuration")
                continue
            
            # Analyze single column
            data_series = data[column_name]
            
            # Step 1: Outlier analysis
            outlier_analysis = analyze_outliers(data_series, meta, self.config)
            
            # Step 2: Missingness mechanism analysis
            missingness_analysis = analyze_missingness_mechanism(
                column_name, data, metadata_dict, self.config
            )
            
            # Step 3: Imputation method proposal
            imputation_proposal = propose_imputation_method(
                column_name, data_series, meta, missingness_analysis, 
                outlier_analysis, self.config, data, metadata_dict
            )
            
            # Create suggestion
            suggestion = ImputationSuggestion(
                column_name=column_name,
                missing_count=missingness_analysis.missing_count,
                missing_percentage=missingness_analysis.missing_percentage,
                mechanism=missingness_analysis.mechanism.value,
                proposed_method=imputation_proposal.method.value,
                rationale=imputation_proposal.rationale,
                outlier_count=outlier_analysis.outlier_count,
                outlier_percentage=outlier_analysis.outlier_percentage,
                outlier_handling=outlier_analysis.handling_strategy.value,
                outlier_rationale=outlier_analysis.rationale,
                confidence_score=imputation_proposal.confidence_score
            )
            
            suggestions.append(suggestion)
        
        duration = time.time() - start_time
        logger.info(f"DataFrame analysis completed in {duration:.2f}s - {len(suggestions)} suggestions")
        
        return suggestions


# Simple convenience function for client applications
def analyze_imputation_requirements(
    metadata_path: str,
    data_path: str,
    config: AnalysisConfig = None
) -> List[ImputationSuggestion]:
    """
    Simple function to analyze imputation requirements.
    
    Args:
        metadata_path: Path to metadata CSV file
        data_path: Path to data CSV file  
        config: Optional analysis configuration
        
    Returns:
        List of ImputationSuggestion objects
        
    Example:
        >>> suggestions = analyze_imputation_requirements('meta.csv', 'data.csv')
        >>> for s in suggestions:
        ...     print(f"{s.column_name}: {s.proposed_method}")
    """
    analyzer = SimpleImputationAnalyzer(config)
    return analyzer.analyze(metadata_path, data_path)


def analyze_dataframe(
    data: pd.DataFrame,
    metadata: Union[List[ColumnMetadata], Dict[str, ColumnMetadata]],
    config: AnalysisConfig = None
) -> List[ImputationSuggestion]:
    """
    Simple function to analyze DataFrame directly.
    
    Args:
        data: Pandas DataFrame to analyze
        metadata: Column metadata (list or dict)
        config: Optional analysis configuration
        
    Returns:
        List of ImputationSuggestion objects
        
    Example:
        >>> import pandas as pd
        >>> from funimpute.models import ColumnMetadata
        >>> 
        >>> data = pd.DataFrame({'age': [25, None, 30], 'name': ['A', 'B', None]})
        >>> metadata = [
        ...     ColumnMetadata('age', 'integer'),
        ...     ColumnMetadata('name', 'string')
        ... ]
        >>> suggestions = analyze_dataframe(data, metadata)
    """
    analyzer = SimpleImputationAnalyzer(config)
    return analyzer.analyze_dataframe(data, metadata)