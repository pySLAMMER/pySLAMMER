#!/usr/bin/env python3
"""
Test script for Phase 5: Statistical Comparison Engine.
"""

import sys
from pathlib import Path

# Add the verification module to path
sys.path.append(str(Path(__file__).parent))

from verification.comparisons import ComparisonEngine, IndividualComparisonResult, GroupComparisonResult
from verification.data_loader import DataManager, ConfigManager
from verification.schemas import Results


def test_individual_comparison():
    """Test individual test comparison logic."""
    print("=== Testing Individual Comparison ===")
    
    engine = ComparisonEngine()
    
    # Test normal case
    result = engine.compare_individual_test(
        test_id="test_rigid_01",
        method="rigid",
        direction="normal",
        legacy_value=10.5,
        pyslammer_value=10.3
    )
    
    print(f"Test: {result.test_id}")
    print(f"  Legacy: {result.legacy_value:.3f} cm")
    print(f"  Computed: {result.pyslammer_value:.3f} cm")
    print(f"  Absolute Error: {result.absolute_error:.3f} cm")
    print(f"  Relative Error: {result.relative_error:.1%}")
    print(f"  Passes: {result.passes_tolerance}")
    print(f"  Tolerance Used: ±{result.tolerance_used.absolute} cm, ±{result.tolerance_used.relative:.1%}")
    print()
    
    # Test small displacement case
    small_result = engine.compare_individual_test(
        test_id="test_rigid_small",
        method="rigid", 
        direction="normal",
        legacy_value=0.2,  # Small displacement
        pyslammer_value=0.25
    )
    
    print(f"Small displacement test: {small_result.test_id}")
    print(f"  Legacy: {small_result.legacy_value:.3f} cm")
    print(f"  Computed: {small_result.pyslammer_value:.3f} cm")
    print(f"  Absolute Error: {small_result.absolute_error:.3f} cm")
    print(f"  Relative Error: {small_result.relative_error:.1%}")
    print(f"  Passes: {small_result.passes_tolerance}")
    print()
    
    # Test zero case
    zero_result = engine.compare_individual_test(
        test_id="test_rigid_zero",
        method="rigid",
        direction="normal", 
        legacy_value=0.0,
        pyslammer_value=0.01
    )
    
    print(f"Zero displacement test: {zero_result.test_id}")
    print(f"  Legacy: {zero_result.legacy_value:.3f} cm")
    print(f"  Computed: {zero_result.pyslammer_value:.3f} cm")
    print(f"  Absolute Error: {zero_result.absolute_error:.3f} cm")
    print(f"  Relative Error: {zero_result.relative_error}")
    print(f"  Passes: {zero_result.passes_tolerance}")


def test_group_comparison():
    """Test group statistical analysis."""
    print("\n=== Testing Group Comparison ===")
    
    engine = ComparisonEngine()
    
    # Create sample individual results
    individual_results = []
    
    # Perfect correlation test data
    test_data = [
        (1.0, 1.01),   # Very close
        (2.0, 2.02),   # Very close
        (5.0, 5.05),   # Very close
        (10.0, 10.1),  # Very close
        (15.0, 15.15), # Very close
        (20.0, 20.2),  # Very close
    ]
    
    for i, (legacy, computed) in enumerate(test_data):
        result = engine.compare_individual_test(
            test_id=f"test_rigid_{i:02d}",
            method="rigid",
            direction="normal",
            legacy_value=legacy,
            pyslammer_value=computed
        )
        individual_results.append(result)
    
    # Analyze group
    group_result = engine.analyze_group(individual_results, "rigid", "normal")
    
    print(f"Group Analysis - {group_result.method.upper()} {group_result.direction}:")
    print(f"  Samples: {group_result.number_of_samples}")
    print(f"  Individual Pass Rate: {group_result.percent_passing_individual_tests:.1f}%")
    print(f"  Regression: y = {group_result.lin_regression_slope:.4f}x + {group_result.lin_regression_intercept:.4f}")
    print(f"  R²: {group_result.lin_regression_r_squared:.4f}")
    print(f"  Mean Relative Error: {group_result.mean_relative_error:.1%}")
    print(f"  Std Relative Error: {group_result.std_relative_error:.1%}")
    print(f"  Max Absolute Error: {group_result.max_absolute_error:.3f} cm")
    print(f"  Group Passes: {group_result.passes_tolerance}")


def test_verification_summary():
    """Test complete verification summary generation."""
    print("\n=== Testing Verification Summary ===")
    
    engine = ComparisonEngine()
    
    # Create mixed test results
    individual_results = []
    
    # Good rigid tests
    for i in range(5):
        result = engine.compare_individual_test(
            test_id=f"rigid_{i:02d}",
            method="rigid",
            direction="normal",
            legacy_value=float(i + 1),
            pyslammer_value=float(i + 1) * 1.01  # 1% error
        )
        individual_results.append(result)
    
    # Some failing decoupled tests
    for i in range(3):
        result = engine.compare_individual_test(
            test_id=f"decoupled_{i:02d}",
            method="decoupled", 
            direction="normal",
            legacy_value=float(i + 10),
            pyslammer_value=float(i + 10) * 1.10  # 10% error - should fail
        )
        individual_results.append(result)
    
    # Generate summary
    summary = engine.generate_verification_summary(individual_results)
    
    print(f"Verification Summary:")
    print(f"  Total Tests: {summary.total_tests}")
    print(f"  Passing: {summary.passing_tests}")
    print(f"  Failing: {summary.failing_tests}")
    print(f"  Overall Pass Rate: {summary.overall_pass_rate:.1f}%")
    print()
    
    print("Method Summaries:")
    for method, stats in summary.method_summaries.items():
        print(f"  {method.upper()}:")
        print(f"    Tests: {stats['total_tests']}")
        print(f"    Pass Rate: {stats['pass_rate']:.1f}%")
        print(f"    Mean Absolute Error: {stats['mean_absolute_error']:.3f} cm")
    print()
    
    print("Group Results:")
    for group in summary.group_results:
        status = "PASS" if group.passes_tolerance else "FAIL"
        print(f"  {group.method.upper()} {group.direction}: {status}")


def test_report_formatting():
    """Test report formatting."""
    print("\n=== Testing Report Formatting ===")
    
    engine = ComparisonEngine()
    
    # Create a simple test case
    individual_results = [
        engine.compare_individual_test("test_01", "rigid", "normal", 10.0, 10.1),
        engine.compare_individual_test("test_02", "rigid", "normal", 5.0, 4.8),
        engine.compare_individual_test("test_03", "decoupled", "normal", 15.0, 16.5),  # Should fail
    ]
    
    summary = engine.generate_verification_summary(individual_results)
    report = engine.format_comparison_report(summary, include_passed=True, detailed=True)
    
    print("Generated Report:")
    print(report)


def test_real_data_sample():
    """Test with actual reference data sample."""
    print("\n=== Testing with Real Reference Data ===")
    
    try:
        data_mgr = DataManager()
        verification_data = data_mgr.load_reference_data()
        
        print(f"Loaded {len(verification_data.tests)} reference tests")
        
        # Get a few sample tests for demonstration
        sample_tests = verification_data.tests[:3]
        engine = ComparisonEngine()
        
        individual_results = []
        
        for test_record in sample_tests:
            # Simulate pySLAMMER results (using reference values with small perturbations)
            simulated_results = Results(
                normal_displacement_cm=test_record.results.normal_displacement_cm * 1.02,  # 2% difference
                inverse_displacement_cm=test_record.results.inverse_displacement_cm * 0.98,  # 2% difference
                kmax=test_record.results.kmax,
                vs_final_mps=test_record.results.vs_final_mps,
                damping_final=test_record.results.damping_final
            )
            
            # Compare
            comparisons = engine.compare_test_record(test_record, simulated_results)
            individual_results.extend(comparisons)
        
        # Generate summary
        summary = engine.generate_verification_summary(individual_results)
        print(f"\nReal Data Test Summary:")
        print(f"  Total Tests: {summary.total_tests}")
        print(f"  Pass Rate: {summary.overall_pass_rate:.1f}%")
        
        # Show sample individual results
        for result in individual_results[:3]:
            print(f"  {result.test_id}: {result.pyslammer_value:.3f} cm vs {result.legacy_value:.3f} cm (Pass: {result.passes_tolerance})")
            
    except Exception as e:
        print(f"Could not test with real data: {e}")


if __name__ == "__main__":
    test_individual_comparison()
    test_group_comparison()
    test_verification_summary()
    test_report_formatting()
    test_real_data_sample()
    print("\n=== Phase 5 Comparison Engine Tests Complete ===")