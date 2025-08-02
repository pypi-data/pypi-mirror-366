# FunPuter - Intelligent Imputation Analysis

**Simple, fast, intelligent recommendations for handling missing data.**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/pypi/v/funputer.svg)](https://pypi.org/project/funputer/)

FunImpute analyzes your data and suggests the best imputation methods based on:
- **Missing data mechanisms** (MCAR, MAR, MNAR detection)
- **Data types** and statistical properties  
- **Business rules** and column dependencies
- **Adaptive thresholds** based on your dataset characteristics

## Quick Start

### Installation
```bash
pip install funputer
```

### Basic Usage

**Python API (Recommended)**
```python
import funimpute

# Analyze your dataset
suggestions = funputer.analyze_imputation_requirements(
    metadata_path="metadata.csv",
    data_path="data.csv"
)

# Use the suggestions
for suggestion in suggestions:
    print(f"{suggestion.column_name}: {suggestion.proposed_method}")
    print(f"  Rationale: {suggestion.rationale}")
    print(f"  Confidence: {suggestion.confidence_score:.3f}")
```

**Command Line**
```bash
# Analyze and save results
funputer -m metadata.csv -d data.csv -o suggestions.csv

# View results
funputer -m metadata.csv -d data.csv --verbose
```

## Metadata Format

Create a CSV with your column information:

```csv
column_name,data_type,min_value,max_value,unique_flag,dependent_column,business_rule,description
user_id,integer,1,999999,TRUE,,,User identifier
age,integer,0,120,FALSE,,Must be positive,User age
income,float,0,,FALSE,age,Higher with age,Annual income
category,categorical,,,FALSE,,,User category A/B/C
```

**Required columns:**
- `column_name`: Name of your data column
- `data_type`: One of `integer`, `float`, `string`, `categorical`, `datetime`, `boolean`

**Optional columns:**
- `min_value`, `max_value`: Valid ranges for numeric data
- `unique_flag`: Set to `TRUE` for ID columns
- `dependent_column`: Related column for dependency analysis
- `business_rule`: Business constraints or relationships
- `description`: Human-readable description

## Client Application Integration

### Direct DataFrame Analysis
```python
import pandas as pd
import funimpute
from funputer import ColumnMetadata

# Your data
data = pd.DataFrame({
    'age': [25, None, 35, 42, None],
    'income': [50000, 60000, None, 80000, 45000],
    'category': ['A', 'B', None, 'A', 'C']
})

# Define metadata programmatically
metadata = [
    ColumnMetadata('age', 'integer', min_value=0, max_value=120),
    ColumnMetadata('income', 'float', dependent_column='age', business_rule='Higher with age'),
    ColumnMetadata('category', 'categorical')
]

# Get suggestions
suggestions = funputer.analyze_dataframe(data, metadata)

# Apply suggestions (Phase 2 - your implementation)
for s in suggestions:
    if s.proposed_method == "Median":
        data[s.column_name].fillna(data[s.column_name].median(), inplace=True)
    elif s.proposed_method == "Mode":
        data[s.column_name].fillna(data[s.column_name].mode().iloc[0], inplace=True)
    # ... implement other methods as needed
```

### Configuration
```python
from funputer import AnalysisConfig

# Custom analysis settings
config = AnalysisConfig(
    iqr_multiplier=2.0,           # Outlier detection sensitivity
    correlation_threshold=0.4,    # Relationship detection threshold
    skewness_threshold=1.5        # Mean vs median decision point
)

suggestions = funputer.analyze_imputation_requirements(
    "metadata.csv", "data.csv", config=config
)
```

## What You Get

Each suggestion includes:

```python
suggestion.column_name          # 'age'
suggestion.proposed_method      # 'Median'
suggestion.rationale           # 'Numeric data with MCAR mechanism...'
suggestion.confidence_score    # 0.847
suggestion.missing_count       # 15
suggestion.missing_percentage  # 0.075 (7.5%)
```

**Available Methods:**
- `Mean`, `Median`, `Mode` - Statistical imputation
- `Regression`, `kNN` - Predictive imputation  
- `Business Rule` - Domain-specific logic
- `Forward Fill`, `Backward Fill` - Temporal imputation
- `Manual Backfill` - Requires human intervention
- `No action needed` - No missing values

## Key Features

✅ **Intelligent Analysis** - Detects missing data mechanisms automatically  
✅ **Business Rule Integration** - Uses your domain knowledge  
✅ **Adaptive Thresholds** - Adjusts based on your data characteristics  
✅ **High Performance** - Analyzes 100+ columns in seconds  
✅ **Simple API** - Easy integration with existing workflows  
✅ **Type Safe** - Full type hints and validation  

## Real-World Example

```python
# Your existing data pipeline
import pandas as pd
import funimpute

def process_customer_data(df):
    # 1. Define your metadata once
    metadata = [
        ColumnMetadata('customer_id', 'integer', unique_flag=True),
        ColumnMetadata('age', 'integer', min_value=0, max_value=120),
        ColumnMetadata('income', 'float', dependent_column='age'),
        ColumnMetadata('segment', 'categorical'),
    ]
    
    # 2. Get intelligent suggestions
    suggestions = funputer.analyze_dataframe(df, metadata)
    
    # 3. Apply high-confidence suggestions automatically
    for s in suggestions:
        if s.confidence_score > 0.8:
            if s.proposed_method == "Median":
                df[s.column_name].fillna(df[s.column_name].median(), inplace=True)
            elif s.proposed_method == "Mode":
                df[s.column_name].fillna(df[s.column_name].mode().iloc[0], inplace=True)
        else:
            print(f"Manual review needed for {s.column_name}: {s.rationale}")
    
    return df
```

## Distribution

- **PyPI Package**: `pip install funputer`
- **Source Code**: Available on GitHub
- **Requirements**: Python 3.9+, pandas, numpy, scipy

## License

MIT License - Use freely in commercial and open-source projects.

---

**Focus**: Get intelligent imputation recommendations, not complex infrastructure.  
**Philosophy**: Simple tools that scale with your needs.