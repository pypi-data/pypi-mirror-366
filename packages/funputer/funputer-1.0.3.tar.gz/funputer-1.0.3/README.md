# FunImpute - Enterprise-Grade Imputation Analysis & Suggestion Service

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

FunImpute is a comprehensive, production-ready imputation analysis service that provides intelligent suggestions for handling missing data and outliers in your datasets. Rather than performing imputation directly, it analyzes your data patterns and provides expert recommendations with full audit trails and observability metrics.

## 🚀 Key Features

- **Intelligent Analysis**: Automatically detects missingness mechanisms (MCAR, MAR, MNAR) using statistical tests
- **Outlier Detection**: IQR-based outlier detection with configurable thresholds
- **Smart Suggestions**: Context-aware imputation method recommendations based on data type, business rules, and statistical properties
- **Enterprise-Ready**: Full audit logging, Prometheus metrics, and production-grade error handling
- **Modular Architecture**: Clean separation of concerns with pluggable components
- **CLI Interface**: Easy-to-use command-line interface with comprehensive options
- **Type Safety**: Full type hints and Pydantic validation throughout

## 📦 Installation

### From Source (Development)

```bash
git clone <repository-url>
cd funimpute
pip install -e .
```

### From PyPI (Coming Soon)

```bash
pip install funimpute
```

## 🏃 Quick Start

### Basic Usage

```bash
# Analyze your dataset
impute-analyze --metadata metadata.csv --data data.csv

# With custom configuration
impute-analyze -m metadata.csv -d data.csv -c config.yml

# Override specific settings
impute-analyze -m metadata.csv -d data.csv --iqr-multiplier 2.0 --metrics-port 8002
```

### Python API

```python
from funimpute import analyze_imputation_requirements

# Run analysis
suggestions = analyze_imputation_requirements(
    metadata_path="metadata.csv",
    data_path="data.csv",
    config_path="config.yml"  # Optional
)

# Access results
for suggestion in suggestions:
    print(f"{suggestion.column}: {suggestion.proposed_method}")
    print(f"Confidence: {suggestion.confidence_score:.3f}")
```

## 📋 Input Requirements

### Metadata CSV Format

Your metadata file must contain the following columns:

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `column_name` | string | ✅ | Name of the data column |
| `data_type` | string | ✅ | One of: integer, float, string, categorical, datetime, boolean |
| `min_value` | float | ❌ | Minimum valid value (for numeric types) |
| `max_value` | float | ❌ | Maximum valid value (for numeric types) |
| `max_length` | integer | ❌ | Maximum string length |
| `unique_flag` | boolean | ✅ | Whether column contains unique identifiers |
| `dependent_column` | string | ❌ | Name of related column for dependency analysis |
| `business_rule` | string | ❌ | Business constraints and rules |
| `description` | string | ❌ | Human-readable description |

### Example Metadata

```csv
column_name,data_type,min_value,max_value,max_length,unique_flag,dependent_column,business_rule,description
Material_ID,integer,1,999999,,TRUE,,,,"Unique identifier for materials"
Unit_Price,float,0.01,1000,,FALSE,Category,"Category A: >50, Category B: 10-50","Must be positive","Price per unit"
Category,categorical,,,1,FALSE,,,,"Material category: A, B, or C"
```

## ⚙️ Configuration

### Configuration File (YAML)

```yaml
# Outlier detection parameters
iqr_multiplier: 1.5
outlier_percentage_threshold: 0.05

# Missingness analysis parameters
correlation_threshold: 0.3
chi_square_alpha: 0.05
point_biserial_threshold: 0.2

# Data quality thresholds
skewness_threshold: 2.0
missing_percentage_threshold: 0.8

# Output paths
output_path: "imputation_suggestions.csv"
audit_log_path: "audit_logs.jsonl"

# Monitoring
metrics_port: 8001
```

### Environment Variables

Override any configuration setting using environment variables:

```bash
export FUNIMPUTE_IQR_MULTIPLIER=2.0
export FUNIMPUTE_OUTLIER_THRESHOLD=0.1
export FUNIMPUTE_CORRELATION_THRESHOLD=0.4
export FUNIMPUTE_METRICS_PORT=8002
export FUNIMPUTE_OUTPUT_PATH="custom_suggestions.csv"
export FUNIMPUTE_AUDIT_LOG_PATH="custom_audit.jsonl"
```

## 📊 Output Files

### Imputation Suggestions CSV

The main output file contains comprehensive recommendations:

| Column | Description |
|--------|-------------|
| `Column` | Column name |
| `Missing_Count` | Number of missing values |
| `Missing_%` | Percentage of missing values |
| `Mechanism` | Detected missingness mechanism (MCAR/MAR/MNAR) |
| `Proposed_Method` | Recommended imputation method |
| `Rationale` | Explanation for the recommendation |
| `Outlier_Count` | Number of outliers detected |
| `Outlier_%` | Percentage of outliers |
| `Outlier_Handling` | Recommended outlier handling strategy |
| `Outlier_Rationale` | Explanation for outlier handling |
| `Confidence_Score` | Confidence in recommendation (0-1) |

### Audit Logs (JSONL)

Detailed audit trail in JSON Lines format for compliance and debugging:

```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "column_name": "Unit_Price",
  "data_type": "float",
  "processing_duration_seconds": 0.245,
  "missing_analysis": {
    "missing_count": 15,
    "missing_percentage": 0.075,
    "mechanism": "MAR",
    "test_statistic": 0.342,
    "p_value": 0.023,
    "related_columns": ["Category"],
    "rationale": "Significant relationship found with Category"
  },
  "outlier_analysis": {
    "outlier_count": 8,
    "outlier_percentage": 0.04,
    "lower_bound": 5.25,
    "upper_bound": 95.75,
    "handling_strategy": "Cap to bounds",
    "rationale": "Low outlier percentage - cap to statistical bounds"
  },
  "imputation_proposal": {
    "method": "Regression",
    "rationale": "Numeric data with MAR mechanism - use regression with predictors: Category",
    "parameters": {
      "predictors": ["Category"],
      "estimator": "BayesianRidge"
    },
    "confidence_score": 0.847
  }
}
```

## 📈 Monitoring & Observability

### Prometheus Metrics

FunImpute exposes comprehensive metrics on `http://localhost:8001/metrics`:

- `funimpute_columns_processed_total`: Total columns processed by data type and mechanism
- `funimpute_missing_values_total`: Total missing values across all columns
- `funimpute_outliers_total`: Total outliers detected
- `funimpute_analysis_duration_seconds`: Analysis time per column
- `funimpute_confidence_score`: Distribution of confidence scores
- `funimpute_data_quality_score`: Overall data quality assessment

### Example Grafana Dashboard

```promql
# Data quality overview
funimpute_data_quality_score{dataset="production"}

# Missing data distribution
sum by (mechanism) (funimpute_columns_processed_total)

# Analysis performance
histogram_quantile(0.95, funimpute_analysis_duration_seconds_bucket)
```

## 🏗️ Architecture

### Modular Design

```
funimpute/
├── __init__.py          # Package exports
├── models.py            # Data models and validation
├── io.py               # Input/output operations
├── outliers.py         # Outlier detection logic
├── mechanism.py        # Missingness mechanism analysis
├── proposal.py         # Imputation method proposals
├── metrics.py          # Prometheus metrics
├── analyzer.py         # Main orchestration
└── cli.py              # Command-line interface
```

### Key Components

1. **IO Module**: Handles metadata validation, configuration loading, and file operations
2. **Outliers Module**: IQR-based outlier detection with business rule integration
3. **Mechanism Module**: Statistical tests for missingness mechanism detection
4. **Proposal Module**: Intelligent imputation method selection with confidence scoring
5. **Metrics Module**: Comprehensive observability and monitoring
6. **Analyzer Module**: Main orchestration and workflow management

## 🧪 Testing

Run the test suite:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=funimpute --cov-report=html
```

## 🔧 Development

### Code Quality

```bash
# Format code
black funimpute/ tests/

# Sort imports
isort funimpute/ tests/

# Type checking
mypy funimpute/

# Linting
flake8 funimpute/ tests/
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Ensure code quality checks pass
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📚 Advanced Usage

### Custom Analysis Pipeline

```python
from funimpute import ImputationAnalyzer, AnalysisConfig

# Custom configuration
config = AnalysisConfig(
    iqr_multiplier=2.0,
    outlier_percentage_threshold=0.1,
    correlation_threshold=0.4
)

# Create analyzer
analyzer = ImputationAnalyzer(config)

# Run analysis
suggestions = analyzer.analyze_dataset("metadata.csv", "data.csv")

# Access detailed results
for result in analyzer.analysis_results:
    print(f"Column: {result.column_name}")
    print(f"Confidence: {result.imputation_proposal.confidence_score}")
    print(f"Processing time: {result.processing_duration_seconds:.3f}s")
```

### Integration with ML Pipelines

```python
import pandas as pd
from funimpute import analyze_imputation_requirements

# Get suggestions
suggestions = analyze_imputation_requirements("meta.csv", "data.csv")

# Filter high-confidence suggestions
high_confidence = [s for s in suggestions if s.confidence_score > 0.8]

# Apply suggestions programmatically
for suggestion in high_confidence:
    if suggestion.proposed_method == "Median":
        # Apply median imputation
        pass
    elif suggestion.proposed_method == "Regression":
        # Apply regression imputation
        pass
```

## 🚨 Production Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install -e .

EXPOSE 8001

CMD ["impute-analyze", "--metadata", "/data/metadata.csv", "--data", "/data/data.csv"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: funimpute-analyzer
spec:
  replicas: 1
  selector:
    matchLabels:
      app: funimpute-analyzer
  template:
    metadata:
      labels:
        app: funimpute-analyzer
    spec:
      containers:
      - name: analyzer
        image: funimpute:latest
        ports:
        - containerPort: 8001
        env:
        - name: FUNIMPUTE_METRICS_PORT
          value: "8001"
        volumeMounts:
        - name: data-volume
          mountPath: /data
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

- 📧 Email: support@funimpute.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-org/funimpute/issues)
- 📖 Documentation: [Full Documentation](https://funimpute.readthedocs.io)

## 🙏 Acknowledgments

- Built with ❤️ using pandas, scikit-learn, and Pydantic
- Inspired by best practices in data science and MLOps
- Special thanks to the open-source community
