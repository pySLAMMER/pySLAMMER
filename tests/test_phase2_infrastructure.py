#!/usr/bin/env python3
"""
Test script for Phase 2 infrastructure components.
"""

import sys
from pathlib import Path

# Add the verification module to path
sys.path.append(str(Path(__file__).parent))

from verification.data_loader import DataManager, ConfigManager
from verification.schemas import ValidationError


def test_config_manager():
    """Test the configuration manager."""
    print("=== Testing ConfigManager ===")
    
    config_mgr = ConfigManager()
    
    # Test tolerance retrieval
    rigid_tolerance = config_mgr.get_tolerance("rigid")
    print(f"Rigid tolerance: {rigid_tolerance.relative:.1%} relative, {rigid_tolerance.absolute} cm absolute")
    
    decoupled_tolerance = config_mgr.get_tolerance("decoupled")
    print(f"Decoupled tolerance: {decoupled_tolerance.relative:.1%} relative, {decoupled_tolerance.absolute} cm absolute")
    
    # Test value-dependent tolerances
    small_disp_tolerance = config_mgr.get_tolerance("rigid", displacement_value=0.5)
    print(f"Small displacement tolerance: {small_disp_tolerance.relative:.1%} relative, {small_disp_tolerance.absolute} cm absolute")
    
    large_disp_tolerance = config_mgr.get_tolerance("rigid", displacement_value=75.0)
    print(f"Large displacement tolerance: {large_disp_tolerance.relative:.1%} relative, {large_disp_tolerance.absolute} cm absolute")
    
    # Test additional output tolerances
    kmax_tolerance = config_mgr.get_additional_output_tolerance("kmax")
    print(f"Kmax tolerance: {kmax_tolerance:.1%}")


def test_data_manager():
    """Test the data manager."""
    print("\n=== Testing DataManager ===")
    
    data_mgr = DataManager()
    
    try:
        # Load reference data
        verification_data = data_mgr.load_reference_data()
        print(f"Loaded {len(verification_data.tests)} test records")
        print(f"Schema version: {verification_data.schema_version}")
        print(f"Source: {verification_data.metadata.get('source_program')} {verification_data.metadata.get('source_version')}")
        
        # Test filtering
        rigid_tests = data_mgr.filter_tests(verification_data, methods=["rigid"])
        print(f"Rigid tests: {len(rigid_tests)}")
        
        decoupled_tests = data_mgr.filter_tests(verification_data, methods=["decoupled"])
        print(f"Decoupled tests: {len(decoupled_tests)}")
        
        coupled_tests = data_mgr.filter_tests(verification_data, methods=["coupled"])
        print(f"Coupled tests: {len(coupled_tests)}")
        
        # Test cache key generation
        sample_test = verification_data.tests[0]
        cache_key = data_mgr.generate_cache_key(sample_test, "1.0.0")
        print(f"Sample cache key: {cache_key}")
        
        # Show a sample test record
        print(f"\nSample test record:")
        print(f"  ID: {sample_test.test_id}")
        print(f"  Method: {sample_test.analysis.method}")
        print(f"  Earthquake: {sample_test.ground_motion_parameters.earthquake}")
        print(f"  ky_g: {sample_test.site_parameters.ky_g}")
        print(f"  Normal displacement: {sample_test.results.normal_displacement_cm} cm")
        
    except ValidationError as e:
        print(f"Validation error: {e}")
    except FileNotFoundError as e:
        print(f"File not found: {e}")


def test_schema_validation():
    """Test schema validation."""
    print("\n=== Testing Schema Validation ===")
    
    data_mgr = DataManager()
    
    # Test with valid data
    try:
        verification_data = data_mgr.load_reference_data(validate=True)
        print("✓ Reference data passes schema validation")
    except ValidationError as e:
        print(f"✗ Reference data failed validation: {e}")
    
    # Test with invalid data
    invalid_test = {
        "test_id": "invalid_test",
        "ground_motion_parameters": {
            "earthquake": "Test EQ",
            "record_file": "test.txt",
            # Missing required field: target_pga_g
        },
        "analysis": {"method": "rigid"},
        "site_parameters": {"ky_g": 0.15},
        "results": {
            "normal_displacement_cm": 1.0,
            "inverse_displacement_cm": 0.8
        }
    }
    
    try:
        data_mgr.schema_validator.validate_test_record(invalid_test)
        print("✗ Invalid data should have failed validation")
    except ValidationError:
        print("✓ Invalid data correctly rejected by schema validation")


if __name__ == "__main__":
    test_config_manager()
    test_data_manager() 
    test_schema_validation()
    print("\n=== Phase 2 Infrastructure Tests Complete ===")