"""
Unit tests for enterprise metadata functionality.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from funimpute.enterprise_models import EnterpriseMetadata, EnterpriseColumnMetadata
from funimpute.schema_validator import SchemaValidator, validate_metadata_file, convert_legacy_metadata, MetadataValidationError
from funimpute.enterprise_loader import EnterpriseMetadataLoader, MetadataCache, load_enterprise_metadata


class TestSchemaValidator:
    """Test schema validation functionality."""
    
    def test_valid_metadata_passes_validation(self):
        """Test that valid metadata passes all validation checks."""
        valid_metadata = {
            "schema_info": {
                "schema_version": "1.0.0",
                "metadata_version": "1.0.0",
                "created_at": "2024-01-01T00:00:00Z",
                "owner": "test@company.com",
                "dataset_name": "test_dataset"
            },
            "columns": [
                {
                    "name": "user_id",
                    "data_type": "integer",
                    "required": True,
                    "unique": True,
                    "description": "Unique user identifier",
                    "version": "1.0.0"
                }
            ]
        }
        
        validator = SchemaValidator()
        metadata, errors = validator.validate_complete(valid_metadata)
        
        assert metadata is not None
        assert len(errors) == 0
        assert metadata.schema_info.dataset_name == "test_dataset"
        assert len(metadata.columns) == 1
        assert metadata.columns[0].name == "user_id"
    
    def test_invalid_schema_fails_validation(self):
        """Test that invalid metadata fails validation."""
        invalid_metadata = {
            "schema_info": {
                "schema_version": "1.0.0"
                # Missing required fields
            },
            "columns": []
        }
        
        validator = SchemaValidator()
        metadata, errors = validator.validate_complete(invalid_metadata)
        
        assert len(errors) > 0
        assert any("required" in error.lower() for error in errors)
    
    def test_business_rules_validation(self):
        """Test business rules validation."""
        metadata_with_rules = {
            "schema_info": {
                "schema_version": "1.0.0",
                "metadata_version": "1.0.0",
                "created_at": "2024-01-01T00:00:00Z",
                "owner": "test@company.com",
                "dataset_name": "test_dataset"
            },
            "columns": [
                {
                    "name": "amount",
                    "data_type": "float",
                    "required": True,
                    "unique": False,
                    "description": "Transaction amount",
                    "version": "1.0.0",
                    "business_rules": [
                        {
                            "rule_id": "AMOUNT_001",
                            "expression": "amount > 0",
                            "description": "Amount must be positive",
                            "severity": "error",
                            "active": True
                        },
                        {
                            "rule_id": "AMOUNT_002", 
                            "expression": "DROP TABLE users",  # Dangerous SQL
                            "description": "Malicious rule",
                            "severity": "error",
                            "active": True
                        }
                    ]
                }
            ]
        }
        
        validator = SchemaValidator()
        metadata, errors = validator.validate_complete(metadata_with_rules)
        
        # Should have business rule validation errors
        business_errors = validator.validate_business_rules(metadata)
        assert len(business_errors) > 0
        assert any("dangerous" in error.lower() for error in business_errors)
    
    def test_consistency_validation(self):
        """Test metadata consistency validation."""
        inconsistent_metadata = {
            "schema_info": {
                "schema_version": "1.0.0",
                "metadata_version": "1.0.0",
                "created_at": "2024-01-01T00:00:00Z",
                "owner": "test@company.com",
                "dataset_name": "test_dataset"
            },
            "columns": [
                {
                    "name": "user_id",
                    "data_type": "categorical",
                    "required": True,
                    "unique": True,
                    "description": "User ID",
                    "version": "1.0.0",
                    "imputation_config": {
                        "default_imputer": "regression",  # Inconsistent with categorical
                        "missing_strategy_hint": "MCAR"
                    },
                    "governance": {
                        "data_classification": "public",
                        "is_pii": True  # Inconsistent - PII should not be public
                    }
                }
            ]
        }
        
        validator = SchemaValidator()
        metadata, errors = validator.validate_complete(inconsistent_metadata)
        
        consistency_errors = validator.validate_metadata_consistency(metadata)
        assert len(consistency_errors) > 0
        assert any("categorical" in error.lower() for error in consistency_errors)
        assert any("pii" in error.lower() for error in consistency_errors)


class TestLegacyConversion:
    """Test conversion from legacy CSV format."""
    
    def test_convert_legacy_metadata(self):
        """Test conversion of legacy metadata to enterprise format."""
        legacy_metadata = [
            {
                "column_name": "user_id",
                "data_type": "integer",
                "unique_flag": True,
                "nullable": False,
                "description": "User identifier",
                "min_value": 1,
                "max_value": 999999,
                "business_rule": "user_id > 0"
            },
            {
                "column_name": "email",
                "data_type": "string",
                "unique_flag": True,
                "nullable": False,
                "description": "User email",
                "max_length": 255
            }
        ]
        
        enterprise_dict = convert_legacy_metadata(legacy_metadata)
        
        assert "schema_info" in enterprise_dict
        assert "columns" in enterprise_dict
        assert len(enterprise_dict["columns"]) == 2
        
        # Check first column conversion
        user_id_col = enterprise_dict["columns"][0]
        assert user_id_col["name"] == "user_id"
        assert user_id_col["data_type"] == "integer"
        assert user_id_col["unique"] == True
        assert user_id_col["required"] == True
        assert "constraints" in user_id_col
        assert user_id_col["constraints"]["min_value"] == 1
        assert user_id_col["constraints"]["max_value"] == 999999
        assert "business_rules" in user_id_col
        
        # Check second column conversion
        email_col = enterprise_dict["columns"][1]
        assert email_col["name"] == "email"
        assert "constraints" in email_col
        assert email_col["constraints"]["max_length"] == 255


class TestMetadataCache:
    """Test metadata caching functionality."""
    
    def test_cache_set_and_get(self):
        """Test basic cache operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = MetadataCache(temp_dir)
            
            # Create test metadata
            metadata = EnterpriseMetadata(
                schema_info={
                    "schema_version": "1.0.0",
                    "metadata_version": "1.0.0", 
                    "created_at": "2024-01-01T00:00:00Z",
                    "owner": "test@company.com",
                    "dataset_name": "test"
                },
                columns=[]
            )
            
            # Test cache set and get
            source = "test_source"
            cache.set(source, metadata)
            cached_metadata = cache.get(source)
            
            assert cached_metadata is not None
            assert cached_metadata.schema_info.dataset_name == "test"
    
    def test_cache_expiry(self):
        """Test cache expiry functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = MetadataCache(temp_dir)
            
            metadata = EnterpriseMetadata(
                schema_info={
                    "schema_version": "1.0.0",
                    "metadata_version": "1.0.0",
                    "created_at": "2024-01-01T00:00:00Z", 
                    "owner": "test@company.com",
                    "dataset_name": "test"
                },
                columns=[]
            )
            
            source = "test_source"
            cache.set(source, metadata)
            
            # Should get cached version with long max_age
            cached = cache.get(source, max_age_hours=24)
            assert cached is not None
            
            # Should not get cached version with very short max_age
            cached = cache.get(source, max_age_hours=0)
            assert cached is None


class TestEnterpriseMetadataLoader:
    """Test enterprise metadata loader."""
    
    def test_load_from_file(self):
        """Test loading metadata from JSON file."""
        metadata_dict = {
            "schema_info": {
                "schema_version": "1.0.0",
                "metadata_version": "1.0.0",
                "created_at": "2024-01-01T00:00:00Z",
                "owner": "test@company.com",
                "dataset_name": "test_dataset"
            },
            "columns": [
                {
                    "name": "test_col",
                    "data_type": "string",
                    "required": False,
                    "unique": False,
                    "description": "Test column",
                    "version": "1.0.0"
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(metadata_dict, f)
            temp_path = f.name
        
        try:
            loader = EnterpriseMetadataLoader(cache_enabled=False)
            metadata = loader.load_from_file(temp_path)
            
            assert metadata is not None
            assert metadata.schema_info.dataset_name == "test_dataset"
            assert len(metadata.columns) == 1
            assert metadata.columns[0].name == "test_col"
        finally:
            os.unlink(temp_path)
    
    def test_load_from_url(self):
        """Test loading metadata from URL."""
        metadata_dict = {
            "schema_info": {
                "schema_version": "1.0.0",
                "metadata_version": "1.0.0",
                "created_at": "2024-01-01T00:00:00Z",
                "owner": "test@company.com",
                "dataset_name": "test_dataset"
            },
            "columns": []
        }
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = metadata_dict
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            loader = EnterpriseMetadataLoader(cache_enabled=False)
            metadata = loader.load_from_url("http://example.com/metadata.json")
            
            assert metadata is not None
            assert metadata.schema_info.dataset_name == "test_dataset"
    
    def test_load_from_legacy_csv(self):
        """Test loading and converting legacy CSV metadata."""
        csv_content = """column_name,data_type,unique_flag,nullable,description
user_id,integer,true,false,User identifier
email,string,true,false,User email"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name
        
        try:
            loader = EnterpriseMetadataLoader(cache_enabled=False)
            metadata = loader.load_from_legacy_csv(temp_path)
            
            assert metadata is not None
            assert len(metadata.columns) == 2
            assert metadata.columns[0].name == "user_id"
            assert metadata.columns[0].data_type.value == "integer"
            assert metadata.columns[0].unique == True
            assert metadata.columns[0].required == True
        finally:
            os.unlink(temp_path)
    
    def test_convert_to_legacy_format(self):
        """Test converting enterprise metadata to legacy format."""
        enterprise_metadata = EnterpriseMetadata(
            schema_info={
                "schema_version": "1.0.0",
                "metadata_version": "1.0.0",
                "created_at": "2024-01-01T00:00:00Z",
                "owner": "test@company.com",
                "dataset_name": "test"
            },
            columns=[
                EnterpriseColumnMetadata(
                    name="user_id",
                    data_type="integer",
                    required=True,
                    unique=True,
                    description="User ID",
                    version="1.0.0"
                )
            ]
        )
        
        loader = EnterpriseMetadataLoader()
        legacy_columns = loader.convert_to_legacy_format(enterprise_metadata)
        
        assert len(legacy_columns) == 1
        assert legacy_columns[0].column_name == "user_id"
        assert legacy_columns[0].data_type == "integer"
        assert legacy_columns[0].unique_flag == True


class TestIntegration:
    """Integration tests for enterprise metadata functionality."""
    
    def test_end_to_end_validation_and_loading(self):
        """Test complete workflow from file to validated metadata."""
        metadata_dict = {
            "schema_info": {
                "schema_version": "1.0.0",
                "metadata_version": "1.0.0",
                "created_at": "2024-01-01T00:00:00Z",
                "owner": "test@company.com",
                "dataset_name": "integration_test"
            },
            "columns": [
                {
                    "name": "user_id",
                    "data_type": "integer",
                    "required": True,
                    "unique": True,
                    "description": "User identifier",
                    "version": "1.0.0",
                    "constraints": {
                        "min_value": 1,
                        "max_value": 999999
                    }
                },
                {
                    "name": "email",
                    "data_type": "string",
                    "required": True,
                    "unique": True,
                    "description": "User email",
                    "version": "1.0.0",
                    "constraints": {
                        "max_length": 255,
                        "regex_pattern": "^[\\w\\.-]+@[\\w\\.-]+\\.[a-zA-Z]{2,}$"
                    }
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(metadata_dict, f)
            temp_path = f.name
        
        try:
            # Test the convenience function
            metadata = load_enterprise_metadata(temp_path, source_type="file", validate=True)
            
            assert metadata is not None
            assert metadata.schema_info.dataset_name == "integration_test"
            assert len(metadata.columns) == 2
            
            # Test getting specific column
            user_id_col = metadata.get_column("user_id")
            assert user_id_col is not None
            assert user_id_col.unique == True
            assert user_id_col.constraints.min_value == 1
            
            # Test getting unique columns
            unique_cols = metadata.get_unique_columns()
            assert len(unique_cols) == 2
            assert all(col.unique for col in unique_cols)
            
        finally:
            os.unlink(temp_path)


if __name__ == '__main__':
    pytest.main([__file__])
