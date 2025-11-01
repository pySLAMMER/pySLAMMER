"""
Generate verification report markdown from results data.

This script replaces the static template with dynamic generation based on
actual verification results and configuration values.
"""

try:
    import tomli
except ImportError:
    import tomllib as tomli
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


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


def load_config() -> Dict[str, Any]:
    """Load verification configuration from TOML file."""
    config_path = Path(__file__).parent / "verification_config.toml"
    with open(config_path, "rb") as f:
        return tomli.load(f)


def format_pass_fail(
    value: float, min_val: float, max_val: Optional[float] = None
) -> str:
    """Format a value with pass/fail indicator."""
    if max_val is not None:
        passed = min_val <= value <= max_val
    else:
        passed = value >= min_val

    return f"{value:.6f} {'✅' if passed else '❌'}"


def format_slope_intercept(
    slope: float, intercept: float, config: Dict[str, Any]
) -> Tuple[str, str]:
    """Format slope and intercept with pass/fail indicators."""
    tol = config["tolerances"]

    slope_passed = (
        tol["lin_regression_slope_min"] <= slope <= tol["lin_regression_slope_max"]
    )
    intercept_passed = (
        tol["lin_regression_intercept_min"]
        <= intercept
        <= tol["lin_regression_intercept_max"]
    )

    slope_str = f"{slope:.6f} {'✅' if slope_passed else '❌'}"
    intercept_str = f"{intercept:.3f} {'✅' if intercept_passed else '❌'}"

    return slope_str, intercept_str


def format_pass_rate(rate: float, config: Dict[str, Any]) -> str:
    """Format pass rate with pass/fail indicator."""
    threshold = config["tolerances"]["percent_passing_individual_tests"]
    passed = rate >= threshold
    return f"{rate:.1f}% {'✅' if passed else '❌'}"


def generate_report(results: VerificationResults) -> str:
    """Generate the complete verification report markdown."""
    config = load_config()
    tol = config["tolerances"]

    # Format results for each method
    methods = {
        "RIGID": results.rigid,
        "DECOUPLED": results.decoupled,
        "COUPLED": results.coupled,
    }

    method_sections = []

    for method_name, method_results in methods.items():
        # Format R² values
        normal_r2 = format_pass_fail(
            method_results.normal_r2, tol["lin_regression_r_squared_min"]
        )
        inverse_r2 = format_pass_fail(
            method_results.inverse_r2, tol["lin_regression_r_squared_min"]
        )

        # Format slope and intercept
        normal_slope, normal_intercept = format_slope_intercept(
            method_results.normal_slope, method_results.normal_intercept, config
        )
        inverse_slope, inverse_intercept = format_slope_intercept(
            method_results.inverse_slope, method_results.inverse_intercept, config
        )

        # Format pass rate
        pass_rate = format_pass_rate(method_results.individual_pass_rate, config)

        section = f"""### {method_name} Method:
- Normal: R² = {normal_r2}, slope = {normal_slope}, intercept = {normal_intercept}
- Inverse: R² = {inverse_r2}, slope = {inverse_slope}, intercept = {inverse_intercept}
- Combined: {pass_rate} individual pass rate"""

        method_sections.append(section)

    # Generate tolerance section
    small_threshold = config["tolerances"]["value_dependent"][
        "small_displacement_threshold"
    ]
    small_abs = config["tolerances"]["value_dependent"]["small_displacement_absolute"]
    default_rel = config["tolerances"]["default_relative"]
    default_abs = config["tolerances"]["default_absolute"]
    group_pass_rate = config["tolerances"]["percent_passing_individual_tests"]

    report = f"""# Verification Report
pySLAMMER version: {results.pyslammer_version}
SLAMMER version: {results.slammer_version}

## Verification Results

{chr(10).join(method_sections)}

## Verification Tolerances

### Linear regression tolerance
  - R$^2 \\le {tol["lin_regression_r_squared_min"]:.2f}$
  - slope $= 1 \\pm {abs(1 - tol["lin_regression_slope_min"]):.2f}$
  - intercept $= 0 \\pm {tol["lin_regression_intercept_max"]:.1f}$ cm

### Individual test tolerance
The individual test tolerances are enforced in aggregate by the group pass rate tolerance.

Expected values > {small_threshold} cm:
  - Relative error <= {default_rel * 100:.0f}%
  - Absolute error <= {default_abs} cm
  
Expected values <= {small_threshold} cm:
  - Absolute error <= {small_abs:.2f} cm

### Group pass rate tolerance
- Group pass rate $\\ge {group_pass_rate:.0f}$%"""

    return report


def save_report(
    results: VerificationResults, output_path: Optional[Path] = None
) -> Path:
    """Generate and save verification report."""
    report_content = generate_report(results)

    if output_path is None:
        output_path = (
            Path(__file__).parent.parent
            / "results"
            / f"verification_report_v{results.pyslammer_version}.md"
        )

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        f.write(report_content)

    return output_path


if __name__ == "__main__":
    # Example usage - this will be replaced by actual results from test_verification.py
    example_results = VerificationResults(
        pyslammer_version="0.2.2",
        slammer_version="1.1",
        rigid=MethodResults(
            0.999999, 1.000703, -0.015, 0.999998, 1.000911, -0.019, 98.9
        ),
        decoupled=MethodResults(
            0.999999, 1.000830, 0.022, 0.999999, 1.001098, 0.016, 98.0
        ),
        coupled=MethodResults(
            0.999999, 1.000665, 0.003, 0.999999, 1.001000, -0.005, 99.0
        ),
    )

    output_path = save_report(example_results)
    print(f"Report generated: {output_path}")
