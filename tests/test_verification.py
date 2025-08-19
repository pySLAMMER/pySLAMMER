#!/usr/bin/env python3
"""
Pytest integration for the pySLAMMER verification framework.

This module provides comprehensive test coverage for the verification system
and integration with CI/CD pipelines.
"""

import pytest
import json
import tempfile
from pathlib import Path
from typing import List, Dict, Any

from verification.data_loader import DataManager, ConfigManager
from verification.comparisons import ComparisonEngine, VerificationSummary
from verification.schemas import TestRecord, Results, VerificationData
from verification.cli import VerificationRunner


class TestVerificationFramework:
    """Test suite for the verification framework components."""
    
    @pytest.fixture(scope="class")
    def data_manager(self):
        """Fixture providing a DataManager instance."""
        return DataManager()
    
    @pytest.fixture(scope="class") 
    def config_manager(self):
        """Fixture providing a ConfigManager instance."""
        return ConfigManager()
    
    @pytest.fixture(scope="class")
    def comparison_engine(self, config_manager):
        """Fixture providing a ComparisonEngine instance."""
        return ComparisonEngine(config_manager)
    
    @pytest.fixture(scope="class")
    def verification_runner(self):
        """Fixture providing a VerificationRunner instance."""
        return VerificationRunner()
    
    @pytest.fixture(scope="class")
    def reference_data(self, data_manager):
        """Fixture providing loaded reference data."""
        return data_manager.load_reference_data()
    
    @pytest.fixture
    def sample_test_records(self, reference_data):
        """Fixture providing a small sample of test records."""
        return reference_data.tests[:5]  # First 5 tests for fast execution


class TestDataManagement(TestVerificationFramework):
    """Test data loading and management functionality."""
    
    def test_reference_data_loading(self, data_manager):
        """Test that reference data loads successfully."""
        data = data_manager.load_reference_data()
        
        assert isinstance(data, VerificationData)
        assert data.schema_version == "1.0"
        assert len(data.tests) > 0
        assert data.metadata is not None
    
    def test_reference_data_validation(self, data_manager):
        """Test that reference data passes schema validation."""
        # This should not raise any ValidationError
        data = data_manager.load_reference_data(validate=True)
        assert len(data.tests) > 0
    
    def test_data_filtering(self, data_manager, reference_data):
        """Test filtering functionality."""
        # Test method filtering
        rigid_tests = data_manager.filter_tests(reference_data, methods=["rigid"])
        assert all(test.analysis.method == "rigid" for test in rigid_tests)
        assert len(rigid_tests) > 0
        
        decoupled_tests = data_manager.filter_tests(reference_data, methods=["decoupled"])
        assert all(test.analysis.method == "decoupled" for test in decoupled_tests)
        
        # Test combined filtering
        combined_tests = data_manager.filter_tests(
            reference_data, 
            methods=["rigid", "decoupled"]
        )
        assert len(combined_tests) == len(rigid_tests) + len(decoupled_tests)
    
    def test_cache_key_generation(self, data_manager, sample_test_records):
        """Test cache key generation is deterministic."""
        test_record = sample_test_records[0]
        
        key1 = data_manager.generate_cache_key(test_record, "1.0.0")
        key2 = data_manager.generate_cache_key(test_record, "1.0.0")
        
        assert key1 == key2  # Should be deterministic
        assert len(key1) == 16  # Should be 16 character hash
        
        # Different version should produce different key
        key3 = data_manager.generate_cache_key(test_record, "1.0.1")
        assert key1 != key3


class TestConfigurationManagement(TestVerificationFramework):
    """Test configuration and tolerance management."""
    
    def test_tolerance_retrieval(self, config_manager):
        """Test tolerance setting retrieval."""
        # Test method-specific tolerances
        rigid_tolerance = config_manager.get_tolerance("rigid")
        assert rigid_tolerance.relative > 0
        assert rigid_tolerance.absolute > 0
        
        decoupled_tolerance = config_manager.get_tolerance("decoupled")
        assert decoupled_tolerance.relative > 0
        assert decoupled_tolerance.absolute > 0
    
    def test_value_dependent_tolerances(self, config_manager):
        """Test value-dependent tolerance logic."""
        # Small displacement should get special tolerance
        small_tolerance = config_manager.get_tolerance("rigid", displacement_value=0.1)
        normal_tolerance = config_manager.get_tolerance("rigid", displacement_value=10.0)
        
        # Small displacements should have different (typically more lenient) tolerances
        assert small_tolerance.absolute != normal_tolerance.absolute
    
    def test_additional_output_tolerances(self, config_manager):
        """Test additional output tolerance retrieval."""
        kmax_tolerance = config_manager.get_additional_output_tolerance("kmax")
        vs_tolerance = config_manager.get_additional_output_tolerance("vs")
        damping_tolerance = config_manager.get_additional_output_tolerance("damping")
        
        assert all(tol > 0 for tol in [kmax_tolerance, vs_tolerance, damping_tolerance])


class TestStatisticalComparison(TestVerificationFramework):
    """Test statistical comparison engine."""
    
    def test_individual_comparison(self, comparison_engine):
        """Test individual test comparison logic."""
        result = comparison_engine.compare_individual_test(
            test_id="test_comparison",
            method="rigid",
            direction="normal",
            legacy_value=10.0,
            pyslammer_value=10.2
        )
        
        assert result.test_id == "test_comparison"
        assert result.method == "rigid"
        assert result.direction == "normal"
        assert result.legacy_value == 10.0
        assert result.pyslammer_value == 10.2
        assert abs(result.absolute_error - 0.2) < 1e-10  # Account for floating point precision
        assert abs(result.relative_error - 0.02) < 1e-6  # 2% error
    
    def test_small_displacement_handling(self, comparison_engine):
        """Test special handling for small displacements."""
        # Very small displacement should pass due to special tolerance handling
        result = comparison_engine.compare_individual_test(
            test_id="small_test",
            method="rigid", 
            direction="normal",
            legacy_value=0.1,  # Small displacement
            pyslammer_value=0.12  # 20% relative error but small absolute
        )
        
        assert result.passes_tolerance  # Should pass due to small displacement tolerance
    
    def test_zero_value_handling(self, comparison_engine):
        """Test handling of zero values."""
        result = comparison_engine.compare_individual_test(
            test_id="zero_test",
            method="rigid",
            direction="normal", 
            legacy_value=0.0,
            pyslammer_value=0.01
        )
        
        assert result.legacy_value == 0.0
        assert result.pyslammer_value == 0.01
        assert result.absolute_error == 0.01
        # Relative error should be handled gracefully (inf or special case)
    
    def test_group_analysis(self, comparison_engine):
        """Test group statistical analysis."""
        # Create sample individual results
        individual_results = []
        for i in range(5):
            result = comparison_engine.compare_individual_test(
                test_id=f"test_{i}",
                method="rigid",
                direction="normal",
                legacy_value=float(i + 1),
                pyslammer_value=float(i + 1) * 1.01  # 1% error
            )
            individual_results.append(result)
        
        group_result = comparison_engine.analyze_group(individual_results, "rigid", "normal")
        
        assert group_result.method == "rigid"
        assert group_result.direction == "normal"
        assert group_result.number_of_samples == 5
        assert group_result.percent_passing_individual_tests > 0
        assert 0.99 < group_result.lin_regression_slope < 1.05  # Should be close to 1.01
        assert group_result.lin_regression_r_squared > 0.95  # Should be high correlation
    
    def test_verification_summary_generation(self, comparison_engine):
        """Test comprehensive verification summary."""
        # Create mixed results
        individual_results = []
        
        # Some passing rigid tests
        for i in range(3):
            result = comparison_engine.compare_individual_test(
                f"rigid_{i}", "rigid", "normal", 
                float(i + 1), float(i + 1) * 1.01
            )
            individual_results.append(result)
        
        # Some failing decoupled tests  
        for i in range(2):
            result = comparison_engine.compare_individual_test(
                f"decoupled_{i}", "decoupled", "normal",
                float(i + 10), float(i + 10) * 1.20  # 20% error - should fail
            )
            individual_results.append(result)
        
        summary = comparison_engine.generate_verification_summary(individual_results)
        
        assert isinstance(summary, VerificationSummary)
        assert summary.total_tests == 5
        assert summary.passing_tests < summary.total_tests  # Some should fail
        assert summary.failing_tests > 0
        assert 0 <= summary.overall_pass_rate <= 100
        assert "rigid" in summary.method_summaries
        assert "decoupled" in summary.method_summaries


class TestCLIIntegration(TestVerificationFramework):
    """Test CLI functionality and integration."""
    
    def test_verification_runner_initialization(self, verification_runner):
        """Test VerificationRunner initializes correctly."""
        assert verification_runner.data_manager is not None
        assert verification_runner.config_manager is not None
        assert verification_runner.comparison_engine is not None
    
    def test_small_verification_run(self, verification_runner):
        """Test running verification on a small subset."""
        results = verification_runner.run_verification(
            methods=["rigid"],
            max_tests=3
        )
        
        assert "summary" in results
        assert "individual_results" in results 
        assert "metadata" in results
        
        summary = results["summary"]
        assert summary.total_tests > 0
        assert len(results["individual_results"]) > 0
        
        metadata = results["metadata"]
        assert metadata["total_reference_tests"] == 3
        assert metadata["filters"]["methods"] == ["rigid"]
    
    def test_results_serialization(self, verification_runner):
        """Test that verification results can be serialized to JSON."""
        results = verification_runner.run_verification(max_tests=2)
        
        # Test JSON serialization of key components
        summary = results["summary"]
        metadata = results["metadata"]
        
        # Should be able to convert to dict and serialize
        summary_dict = {
            "total_tests": summary.total_tests,
            "passing_tests": summary.passing_tests,
            "overall_pass_rate": summary.overall_pass_rate
        }
        
        # This should not raise an exception
        json_str = json.dumps(summary_dict)
        assert len(json_str) > 0
        
        # Metadata should also be serializable
        json_str = json.dumps(metadata)
        assert len(json_str) > 0


@pytest.mark.verification
@pytest.mark.slow
class TestLegacyVerification:
    """High-level verification tests for legacy compatibility.
    
    These tests run the actual verification process against reference data
    and are marked as 'slow' since they may take longer to execute.
    """
    
    def test_verification_passes_tolerance(self):
        """Test that verification passes within acceptable tolerances."""
        runner = VerificationRunner()
        
        # Run on a reasonable sample size
        results = runner.run_verification(max_tests=20)
        summary = results["summary"]
        
        # We expect high pass rate for simulated data
        assert summary.overall_pass_rate >= 70.0, f"Pass rate too low: {summary.overall_pass_rate}%"
        assert summary.total_tests == 40  # 20 tests × 2 directions
    
    @pytest.mark.parametrize("method", ["rigid", "decoupled", "coupled"])
    def test_method_specific_verification(self, method):
        """Test verification for specific analysis methods."""
        runner = VerificationRunner()
        
        results = runner.run_verification(
            methods=[method],
            max_tests=5
        )
        
        summary = results["summary"]
        assert summary.total_tests > 0
        assert method in summary.method_summaries
        
        method_stats = summary.method_summaries[method]
        assert method_stats["total_tests"] > 0
        assert 0 <= method_stats["pass_rate"] <= 100
    
    def test_verification_report_generation(self):
        """Test that verification reports can be generated."""
        runner = VerificationRunner()
        
        results = runner.run_verification(max_tests=5)
        summary = results["summary"]
        
        # Test text report generation
        report = runner.comparison_engine.format_comparison_report(
            summary, include_passed=True, detailed=True
        )
        
        assert len(report) > 0
        assert "PYSLAMMER VERIFICATION REPORT" in report
        assert "Overall Results:" in report
        assert "Method-Specific Results:" in report
    
    def test_cache_functionality(self):
        """Test that caching works correctly."""
        runner = VerificationRunner()
        
        # First run - should populate cache
        results1 = runner.run_verification(max_tests=2, force_recompute=True)
        
        # Second run - should use cache
        results2 = runner.run_verification(max_tests=2, force_recompute=False)
        
        # Results should be similar (cache working)
        assert results1["summary"].total_tests == results2["summary"].total_tests
    
    def test_filtering_functionality(self):
        """Test that filtering works correctly."""
        runner = VerificationRunner()
        
        # Test method filtering
        rigid_results = runner.run_verification(methods=["rigid"], max_tests=3)
        assert "rigid" in rigid_results["summary"].method_summaries
        assert len(rigid_results["summary"].method_summaries) == 1
        
        # Test multiple method filtering
        multi_results = runner.run_verification(
            methods=["rigid", "decoupled"], 
            max_tests=3
        )
        assert len(multi_results["summary"].method_summaries) <= 2


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_method_filtering(self):
        """Test handling of invalid method names."""
        runner = VerificationRunner()
        
        # Should handle gracefully - no tests should match
        results = runner.run_verification(methods=["invalid_method"], max_tests=5)
        assert results["summary"].total_tests == 0
    
    def test_empty_result_handling(self):
        """Test handling when no tests are found."""
        runner = VerificationRunner()
        
        # Filter that should return no results
        results = runner.run_verification(test_ids=["nonexistent_test"])
        assert results["summary"].total_tests == 0
        assert results["summary"].passing_tests == 0
        assert results["summary"].failing_tests == 0


# End of test file