"""
Tests comparing pySLAMMER results against SLAMMER reference data.

Evaluates linear regression parameters and group pass rates are within the tolerances
set in verification_config.toml.

"""

import importlib.metadata
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pytest
import numpy as np
import scipy.stats
from verification.comparisons import ConfigManager
from verification.data_loader import DataManager
from verification.config.generate_report import save_report


@dataclass
class MethodResults:
    """Results for a single analysis method (RIGID, DECOUPLED, COUPLED)."""

    normal_r2: float
    normal_slope: float
    normal_intercept: float
    inverse_r2: float
    inverse_slope: float
    inverse_intercept: float
    individual_pass_rate: float


@dataclass
class VerificationResults:
    """Complete verification results for all methods."""

    pyslammer_version: str
    slammer_version: str
    rigid: MethodResults
    decoupled: MethodResults
    coupled: MethodResults


def get_pyslammer_version(requested_version: Optional[str] = None) -> str:
    """Get pySLAMMER version to test."""
    if requested_version:
        return requested_version
    
    try:
        return importlib.metadata.version("pyslammer")
    except importlib.metadata.PackageNotFoundError:
        # Fallback to git describe or default
        try:
            result = subprocess.run(
                ["git", "describe", "--tags", "--dirty"], 
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "dev"


def check_pyslammer_results_exist(version: str) -> bool:
    """Check if pySLAMMER results exist for specified version."""
    # Use the same filename format as DataManager (keeping periods)
    results_path = Path(__file__).parent / "verification_data" / "results" / f"pyslammer_{version}_results.json.gz"
    return results_path.exists()


def generate_pyslammer_results_if_needed(version: str) -> None:
    """Generate pySLAMMER results if they don't exist."""
    if not check_pyslammer_results_exist(version):
        # Import and run the generation script
        from verification.generate_pyslammer_verification_results import run_verification_analyses, collect_and_save_pyslammer_results
        
        print(f"Generating pySLAMMER results for version {version}...")
        print("This may take a few minutes...")
        
        # First run all analyses and cache individual results
        run_verification_analyses(pyslammer_version=version)
        
        # Then collect cached results into versioned file
        collect_and_save_pyslammer_results(pyslammer_version=version)


def calculate_linear_regression_stats(expected: np.ndarray, actual: np.ndarray) -> tuple[float, float, float]:
    """Calculate linear regression R², slope, and intercept."""
    result = scipy.stats.linregress(expected, actual)
    slope = result.slope
    intercept = result.intercept
    r_squared = result.rvalue ** 2
    return r_squared, slope, intercept


def calculate_individual_pass_rate(expected: np.ndarray, actual: np.ndarray, config: dict) -> float:
    """Calculate individual test pass rate based on tolerances."""
    tol = config["tolerances"]
    small_threshold = tol["value_dependent"]["small_displacement_threshold"]
    
    passes = 0
    total = len(expected)
    
    for exp, act in zip(expected, actual):
        abs_error = abs(act - exp)
        
        if abs(exp) <= small_threshold:
            # Use absolute tolerance for small values
            small_abs_tol = tol["value_dependent"]["small_displacement_absolute"]
            passed = abs_error <= small_abs_tol
        else:
            # Use relative and absolute tolerance for larger values
            rel_error = abs_error / abs(exp) if exp != 0 else float('inf')
            passed = (rel_error <= tol["default_relative"] and 
                     abs_error <= tol["default_absolute"])
        
        if passed:
            passes += 1
    
    return (passes / total) * 100


def run_verification_tests(version: str) -> VerificationResults:
    """Run complete verification test suite."""
    # Load data and configuration
    data_manager = DataManager()
    config_manager = ConfigManager()
    config = config_manager.config
    
    # Load reference and test data
    reference_data = data_manager.load_reference_data()
    test_data = data_manager.load_results("pyslammer", version=version)
    
    # Initialize results structure
    method_results = {}
    
    # Test each analysis method
    for method in ["rigid", "decoupled", "coupled"]:
        # Get data for this method
        ref_method_data = data_manager.filter_analyses(reference_data, methods=[method])
        test_method_data = data_manager.filter_analyses(test_data, methods=[method])
        
        # Calculate stats for normal direction
        ref_normal = np.array([r.results.normal_displacement_cm for r in ref_method_data])
        test_normal = np.array([r.results.normal_displacement_cm for r in test_method_data])
        normal_r2, normal_slope, normal_intercept = calculate_linear_regression_stats(ref_normal, test_normal)
        
        # Calculate stats for inverse direction  
        ref_inverse = np.array([r.results.inverse_displacement_cm for r in ref_method_data])
        test_inverse = np.array([r.results.inverse_displacement_cm for r in test_method_data])
        inverse_r2, inverse_slope, inverse_intercept = calculate_linear_regression_stats(ref_inverse, test_inverse)
        
        # Calculate combined pass rate
        combined_ref = np.concatenate([ref_normal, ref_inverse])
        combined_test = np.concatenate([test_normal, test_inverse])
        pass_rate = calculate_individual_pass_rate(combined_ref, combined_test, config)
        
        method_results[method] = MethodResults(
            normal_r2=normal_r2,
            normal_slope=normal_slope, 
            normal_intercept=normal_intercept,
            inverse_r2=inverse_r2,
            inverse_slope=inverse_slope,
            inverse_intercept=inverse_intercept,
            individual_pass_rate=pass_rate
        )
    
    return VerificationResults(
        pyslammer_version=version,
        slammer_version="1.1",  # This should come from reference data
        rigid=method_results["rigid"],
        decoupled=method_results["decoupled"], 
        coupled=method_results["coupled"]
    )


@pytest.fixture(scope="session")
def pyslammer_version(request):
    """Get pySLAMMER version to test."""
    return get_pyslammer_version(request.config.getoption("--pyslammer-version", default=None))


@pytest.fixture(scope="session") 
def verification_results(pyslammer_version):
    """Generate verification results for the test session."""
    # Ensure results exist
    generate_pyslammer_results_if_needed(pyslammer_version)
    
    # Run verification tests
    return run_verification_tests(pyslammer_version)


def test_rigid_method_group_pass_rate(verification_results):
    """Test that RIGID method group pass rate meets tolerance."""
    config = ConfigManager().config
    min_pass_rate = config["tolerances"]["percent_passing_individual_tests"]
    
    assert verification_results.rigid.individual_pass_rate >= min_pass_rate, \
        f"RIGID method pass rate {verification_results.rigid.individual_pass_rate:.1f}% below threshold {min_pass_rate}%"


def test_decoupled_method_group_pass_rate(verification_results):
    """Test that DECOUPLED method group pass rate meets tolerance.""" 
    config = ConfigManager().config
    min_pass_rate = config["tolerances"]["percent_passing_individual_tests"]
    
    assert verification_results.decoupled.individual_pass_rate >= min_pass_rate, \
        f"DECOUPLED method pass rate {verification_results.decoupled.individual_pass_rate:.1f}% below threshold {min_pass_rate}%"


def test_coupled_method_group_pass_rate(verification_results):
    """Test that COUPLED method group pass rate meets tolerance."""
    config = ConfigManager().config  
    min_pass_rate = config["tolerances"]["percent_passing_individual_tests"]
    
    assert verification_results.coupled.individual_pass_rate >= min_pass_rate, \
        f"COUPLED method pass rate {verification_results.coupled.individual_pass_rate:.1f}% below threshold {min_pass_rate}%"


def test_linear_regression_parameters(verification_results):
    """Test that linear regression parameters are within tolerance for all methods."""
    config = ConfigManager().config
    tol = config["tolerances"]
    
    methods = [
        ("RIGID", verification_results.rigid),
        ("DECOUPLED", verification_results.decoupled), 
        ("COUPLED", verification_results.coupled)
    ]
    
    for method_name, results in methods:
        # Test normal direction
        assert results.normal_r2 >= tol["lin_regression_r_squared_min"], \
            f"{method_name} normal R² {results.normal_r2:.6f} below minimum {tol['lin_regression_r_squared_min']}"
        assert tol["lin_regression_slope_min"] <= results.normal_slope <= tol["lin_regression_slope_max"], \
            f"{method_name} normal slope {results.normal_slope:.6f} outside range [{tol['lin_regression_slope_min']}, {tol['lin_regression_slope_max']}]"
        assert tol["lin_regression_intercept_min"] <= results.normal_intercept <= tol["lin_regression_intercept_max"], \
            f"{method_name} normal intercept {results.normal_intercept:.3f} outside range [{tol['lin_regression_intercept_min']}, {tol['lin_regression_intercept_max']}]"
            
        # Test inverse direction
        assert results.inverse_r2 >= tol["lin_regression_r_squared_min"], \
            f"{method_name} inverse R² {results.inverse_r2:.6f} below minimum {tol['lin_regression_r_squared_min']}"
        assert tol["lin_regression_slope_min"] <= results.inverse_slope <= tol["lin_regression_slope_max"], \
            f"{method_name} inverse slope {results.inverse_slope:.6f} outside range [{tol['lin_regression_slope_min']}, {tol['lin_regression_slope_max']}]"
        assert tol["lin_regression_intercept_min"] <= results.inverse_intercept <= tol["lin_regression_intercept_max"], \
            f"{method_name} inverse intercept {results.inverse_intercept:.3f} outside range [{tol['lin_regression_intercept_min']}, {tol['lin_regression_intercept_max']}]"


def test_generate_verification_report(verification_results, tmp_path):
    """Generate and save verification report."""
    # Save to both temp path (for test) and permanent results directory
    temp_path = tmp_path / f"verification_report_v{verification_results.pyslammer_version}.md"
    permanent_path = Path(__file__).parent / "verification_data" / "results" / f"verification_report_v{verification_results.pyslammer_version}.md"
    
    # Ensure results directory exists
    permanent_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to permanent location
    saved_path = save_report(verification_results, permanent_path)
    print(f"Verification report saved to: {saved_path}")
    
    assert saved_path.exists(), f"Report not generated at {saved_path}"
    
    # Verify report contains key information
    report_content = saved_path.read_text()
    assert verification_results.pyslammer_version in report_content
    assert "Verification Results" in report_content
    assert "RIGID" in report_content
    assert "DECOUPLED" in report_content  
    assert "COUPLED" in report_content
