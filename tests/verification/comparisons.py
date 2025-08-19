"""
Statistical comparison engine for verification framework.

This module implements both individual test comparisons and group statistical analysis
to validate pySLAMMER results against legacy SLAMMER data.
"""

import math
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import numpy as np
from scipy import stats

from .schemas import TestRecord, Results
from .data_loader import ConfigManager, ToleranceSettings


@dataclass
class IndividualComparisonResult:
    """Result of comparing a single test case."""
    test_id: str
    method: str  # Rigid, Decoupled, Coupled
    direction: str  # Normal, Inverse
    
    # Statistical measures
    absolute_error: float
    relative_error: float
    percent_difference: float
    
    # Pass/fail status
    passes_tolerance: bool
    tolerance_used: ToleranceSettings
    
    # Context
    legacy_value: float
    pyslammer_value: float
    units: str = "cm"


@dataclass
class GroupComparisonResult:
    """Result of comparing a group of test cases."""
    method: str  # Rigid, Decoupled, Coupled
    direction: str  # Normal, Inverse, All
    
    # Statistical measures
    number_of_samples: int
    percent_passing_individual_tests: float
    lin_regression_slope: float
    lin_regression_intercept: float
    lin_regression_r_squared: float
    
    # Pass/fail status
    passes_tolerance: bool
    
    # Additional statistics
    mean_relative_error: float
    std_relative_error: float
    max_absolute_error: float


@dataclass
class VerificationSummary:
    """Overall verification results summary."""
    total_tests: int
    passing_tests: int
    failing_tests: int
    overall_pass_rate: float
    
    individual_results: List[IndividualComparisonResult]
    group_results: List[GroupComparisonResult]
    
    # Method-specific summaries
    method_summaries: Dict[str, Dict[str, Any]]


class ComparisonEngine:
    """Statistical comparison engine for verification framework."""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """Initialize comparison engine.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager or ConfigManager()
    
    def compare_individual_test(self, 
                              test_id: str,
                              method: str,
                              direction: str,
                              legacy_value: float,
                              pyslammer_value: float) -> IndividualComparisonResult:
        """Compare a single test result.
        
        Args:
            test_id: Unique test identifier
            method: Analysis method (rigid, decoupled, coupled)
            direction: Direction (normal, inverse)
            legacy_value: Expected result from legacy SLAMMER
            pyslammer_value: Computed result from pySLAMMER
            
        Returns:
            Individual comparison result
        """
        # Calculate error metrics
        absolute_error = abs(pyslammer_value - legacy_value)
        
        if legacy_value != 0:
            relative_error = absolute_error / abs(legacy_value)
            percent_difference = ((pyslammer_value - legacy_value) / legacy_value) * 100
        else:
            # Handle case where legacy value is zero
            relative_error = float('inf') if absolute_error > 0 else 0
            percent_difference = float('inf') if pyslammer_value != 0 else 0
        
        # Get tolerance settings
        tolerance = self.config_manager.get_tolerance(method, legacy_value)
        
        # Check if test passes tolerance
        passes_absolute = absolute_error <= tolerance.absolute
        passes_relative = relative_error <= tolerance.relative
        
        # For very small displacements, use special handling
        if legacy_value <= self.config_manager.config.get("tolerances", {}).get("value_dependent", {}).get("small_displacement_threshold", 0.5):
            # For small displacements, use absolute tolerance primarily
            passes_tolerance = passes_absolute
        else:
            # For normal displacements, both absolute and relative must pass
            passes_tolerance = passes_absolute and passes_relative
        
        return IndividualComparisonResult(
            test_id=test_id,
            method=method,
            direction=direction,
            absolute_error=absolute_error,
            relative_error=relative_error,
            percent_difference=percent_difference,
            passes_tolerance=passes_tolerance,
            tolerance_used=tolerance,
            legacy_value=legacy_value,
            pyslammer_value=pyslammer_value
        )
    
    def compare_test_record(self, 
                          test_record: TestRecord,
                          pyslammer_results: Results) -> List[IndividualComparisonResult]:
        """Compare all directions for a single test record.
        
        Args:
            test_record: Reference test record with expected results
            pyslammer_results: Computed results from pySLAMMER
            
        Returns:
            List of individual comparison results for each direction
        """
        results = []
        method = test_record.analysis.method
        
        # Compare normal direction
        normal_result = self.compare_individual_test(
            test_id=f"{test_record.test_id}_normal",
            method=method,
            direction="normal",
            legacy_value=test_record.results.normal_displacement_cm,
            pyslammer_value=pyslammer_results.normal_displacement_cm
        )
        results.append(normal_result)
        
        # Compare inverse direction
        inverse_result = self.compare_individual_test(
            test_id=f"{test_record.test_id}_inverse",
            method=method,
            direction="inverse",
            legacy_value=test_record.results.inverse_displacement_cm,
            pyslammer_value=pyslammer_results.inverse_displacement_cm
        )
        results.append(inverse_result)
        
        return results
    
    def analyze_group(self, 
                     individual_results: List[IndividualComparisonResult],
                     method: str,
                     direction: str = "All") -> GroupComparisonResult:
        """Perform group statistical analysis.
        
        Args:
            individual_results: List of individual comparison results
            method: Analysis method to analyze
            direction: Direction to analyze ("Normal", "Inverse", or "All")
            
        Returns:
            Group comparison result
        """
        # Filter results by method and direction
        filtered_results = [
            r for r in individual_results 
            if r.method == method and (direction == "All" or r.direction.lower() == direction.lower())
        ]
        
        if not filtered_results:
            return GroupComparisonResult(
                method=method,
                direction=direction,
                number_of_samples=0,
                percent_passing_individual_tests=0.0,
                lin_regression_slope=0.0,
                lin_regression_intercept=0.0,
                lin_regression_r_squared=0.0,
                passes_tolerance=False,
                mean_relative_error=0.0,
                std_relative_error=0.0,
                max_absolute_error=0.0
            )
        
        # Calculate basic statistics
        number_of_samples = len(filtered_results)
        passing_tests = sum(1 for r in filtered_results if r.passes_tolerance)
        percent_passing = (passing_tests / number_of_samples) * 100
        
        # Extract values for regression analysis
        legacy_values = np.array([r.legacy_value for r in filtered_results])
        pyslammer_values = np.array([r.pyslammer_value for r in filtered_results])
        
        # Calculate linear regression
        regression_result = stats.linregress(legacy_values, pyslammer_values)
        slope = float(regression_result.slope)
        intercept = float(regression_result.intercept)
        r_squared = float(regression_result.rvalue ** 2)
        
        # Additional statistics
        relative_errors = [r.relative_error for r in filtered_results if not math.isinf(r.relative_error)]
        mean_relative_error = float(np.mean(relative_errors)) if relative_errors else 0.0
        std_relative_error = float(np.std(relative_errors)) if relative_errors else 0.0
        max_absolute_error = max(r.absolute_error for r in filtered_results)
        
        # Check group tolerances
        config = self.config_manager.config
        group_tolerances = config.get("tolerances", {})
        
        passes_percent_threshold = percent_passing >= group_tolerances.get("percent_passing_individual_tests", 95.0)
        passes_slope = (group_tolerances.get("lin_regression_slope_min", 0.99) <= 
                       slope <= 
                       group_tolerances.get("lin_regression_slope_max", 1.01))
        passes_intercept = (group_tolerances.get("lin_regression_intercept_min", -0.1) <= 
                           intercept <= 
                           group_tolerances.get("lin_regression_intercept_max", 0.1))
        passes_r_squared = r_squared >= group_tolerances.get("lin_regression_r_squared_min", 0.99)
        
        passes_tolerance = all([passes_percent_threshold, passes_slope, passes_intercept, passes_r_squared])
        
        return GroupComparisonResult(
            method=method,
            direction=direction,
            number_of_samples=number_of_samples,
            percent_passing_individual_tests=percent_passing,
            lin_regression_slope=slope,
            lin_regression_intercept=intercept,
            lin_regression_r_squared=r_squared,
            passes_tolerance=passes_tolerance,
            mean_relative_error=mean_relative_error,
            std_relative_error=std_relative_error,
            max_absolute_error=max_absolute_error
        )
    
    def generate_verification_summary(self, 
                                    individual_results: List[IndividualComparisonResult]) -> VerificationSummary:
        """Generate comprehensive verification summary.
        
        Args:
            individual_results: All individual comparison results
            
        Returns:
            Complete verification summary
        """
        total_tests = len(individual_results)
        passing_tests = sum(1 for r in individual_results if r.passes_tolerance)
        failing_tests = total_tests - passing_tests
        overall_pass_rate = (passing_tests / total_tests * 100) if total_tests > 0 else 0.0
        
        # Generate group analyses
        methods = list(set(r.method for r in individual_results))
        directions = ["Normal", "Inverse", "All"]
        
        group_results = []
        for method in methods:
            for direction in directions:
                group_result = self.analyze_group(individual_results, method, direction)
                if group_result.number_of_samples > 0:  # Only include non-empty groups
                    group_results.append(group_result)
        
        # Generate method-specific summaries
        method_summaries = {}
        for method in methods:
            method_results = [r for r in individual_results if r.method == method]
            method_passing = sum(1 for r in method_results if r.passes_tolerance)
            method_summaries[method] = {
                "total_tests": len(method_results),
                "passing_tests": method_passing,
                "pass_rate": (method_passing / len(method_results) * 100) if method_results else 0.0,
                "mean_absolute_error": np.mean([r.absolute_error for r in method_results]) if method_results else 0.0,
                "mean_relative_error": np.mean([r.relative_error for r in method_results if not math.isinf(r.relative_error)]) if method_results else 0.0
            }
        
        return VerificationSummary(
            total_tests=total_tests,
            passing_tests=passing_tests,
            failing_tests=failing_tests,
            overall_pass_rate=overall_pass_rate,
            individual_results=individual_results,
            group_results=group_results,
            method_summaries=method_summaries
        )
    
    def format_comparison_report(self, 
                               summary: VerificationSummary,
                               include_passed: bool = False,
                               detailed: bool = True) -> str:
        """Format verification results as a readable report.
        
        Args:
            summary: Verification summary to format
            include_passed: Whether to include passed tests in detail
            detailed: Whether to include detailed statistics
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 80)
        report.append("PYSLAMMER VERIFICATION REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Overall summary
        report.append(f"Overall Results:")
        report.append(f"  Total Tests: {summary.total_tests}")
        report.append(f"  Passing: {summary.passing_tests} ({summary.overall_pass_rate:.1f}%)")
        report.append(f"  Failing: {summary.failing_tests}")
        report.append("")
        
        # Method-specific summaries
        report.append("Method-Specific Results:")
        for method, method_stats in summary.method_summaries.items():
            report.append(f"  {method.upper()}:")
            report.append(f"    Tests: {method_stats['total_tests']}")
            report.append(f"    Pass Rate: {method_stats['pass_rate']:.1f}%")
            report.append(f"    Mean Absolute Error: {method_stats['mean_absolute_error']:.3f} cm")
            report.append(f"    Mean Relative Error: {method_stats['mean_relative_error']:.1%}")
        report.append("")
        
        # Group statistical analysis
        if detailed and summary.group_results:
            report.append("Group Statistical Analysis:")
            for group in summary.group_results:
                status = "PASS" if group.passes_tolerance else "FAIL"
                report.append(f"  {group.method.upper()} - {group.direction} [{status}]:")
                report.append(f"    Samples: {group.number_of_samples}")
                report.append(f"    Individual Pass Rate: {group.percent_passing_individual_tests:.1f}%")
                report.append(f"    Regression: y = {group.lin_regression_slope:.4f}x + {group.lin_regression_intercept:.4f}")
                report.append(f"    R²: {group.lin_regression_r_squared:.4f}")
                report.append(f"    Mean Relative Error: {group.mean_relative_error:.1%}")
            report.append("")
        
        # Failed tests detail
        failed_tests = [r for r in summary.individual_results if not r.passes_tolerance]
        if failed_tests:
            report.append(f"Failed Tests ({len(failed_tests)}):")
            for test in failed_tests:
                report.append(f"  {test.test_id}:")
                report.append(f"    Expected: {test.legacy_value:.3f} cm")
                report.append(f"    Actual: {test.pyslammer_value:.3f} cm")
                report.append(f"    Absolute Error: {test.absolute_error:.3f} cm")
                report.append(f"    Relative Error: {test.relative_error:.1%}")
            report.append("")
        
        # Passed tests detail (if requested)
        if include_passed:
            passed_tests = [r for r in summary.individual_results if r.passes_tolerance]
            if passed_tests:
                report.append(f"Passed Tests ({len(passed_tests)}):")
                for test in passed_tests:
                    report.append(f"  {test.test_id}: {test.pyslammer_value:.3f} cm (error: {test.relative_error:.1%})")
                report.append("")
        
        report.append("=" * 80)
        return "\n".join(report)