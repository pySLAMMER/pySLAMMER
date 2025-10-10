# pySLAMMER Verification Guide for Developers

This guide explains how to use pytest to verify pySLAMMER results against legacy SLAMMER data.

## Overview

The verification system compares pySLAMMER results against reference SLAMMER results using statistical tests to ensure compatibility and accuracy. It supports testing different versions of pySLAMMER and generates detailed reports.

## Quick Start

### Test Current pySLAMMER Version
```bash
pytest tests/test_verification.py -v
```

### Test Specific pySLAMMER Version
```bash
pytest tests/test_verification.py --pyslammer-version 0.2.4 -v
```

## Command Reference

### Basic Usage
| Command | Description |
|---------|-------------|
| `pytest tests/test_verification.py` | Test auto-detected pySLAMMER version |
| `pytest tests/test_verification.py -v` | Verbose output showing test details |
| `pytest tests/test_verification.py -s` | Show print statements (useful for new version generation) |

### Version-Specific Testing
| Command | Description |
|---------|-------------|
| `pytest tests/test_verification.py --pyslammer-version 0.2.2` | Test existing version 0.2.2 |
| `pytest tests/test_verification.py --pyslammer-version 0.3.0` | Test new version (will trigger generation) |
| `pytest tests/test_verification.py --pyslammer-version dev` | Test development version |

### Advanced Options
| Command | Description |
|---------|-------------|
| `pytest tests/test_verification.py::test_rigid_method_group_pass_rate` | Run only RIGID method test |
| `pytest tests/test_verification.py::test_linear_regression_parameters` | Run only linear regression tests |
| `pytest tests/test_verification.py --tb=short` | Shorter traceback on failures |

## What Gets Tested

The verification suite runs these statistical tests:

### 1. Group Pass Rate Tests
- **RIGID Method**: Individual test pass rate ≥ 95%
- **DECOUPLED Method**: Individual test pass rate ≥ 95%  
- **COUPLED Method**: Individual test pass rate ≥ 95%

### 2. Linear Regression Tests
For each method (RIGID/DECOUPLED/COUPLED) and direction (normal/inverse):
- **R² ≥ 0.99**: Strong correlation with SLAMMER results
- **Slope = 1 ± 0.01**: Results scale correctly
- **Intercept = 0 ± 0.1 cm**: No systematic bias

### 3. Report Generation
- Generates markdown report with detailed results
- Saves to `tests/verification_data/results/verification_report_v{version}.md`

## File Structure

```
tests/
├── test_verification.py                    # Main test file
├── verification_data/
│   ├── results/
│   │   ├── slammer_results.json.gz         # Reference SLAMMER data
│   │   ├── pyslammer_{version}_results.json.gz  # pySLAMMER results
│   │   └── verification_report_v{version}.md    # Generated reports
│   ├── cache/                              # Temporary analysis cache
│   └── schemas/
│       └── results_schema.json             # Data validation schema
├── verification/
│   ├── config/
│   │   ├── verification_config.toml        # Tolerance settings
│   │   └── generate_report.py              # Report generation
│   ├── data_loader.py                      # Data loading utilities
│   ├── comparisons.py                      # Statistical comparisons
│   ├── schemas.py                          # Data models
│   └── generate_pyslammer_verification_results.py  # Result generation
└── conftest.py                             # pytest configuration
```

## Version Detection

The system automatically detects pySLAMMER version in this order:
1. `--pyslammer-version` command line argument
2. Installed package version (`importlib.metadata.version("pyslammer")`)
3. Git describe (`git describe --tags --dirty`)
4. Fallback to "dev"

## New Version Workflow

When testing a new version:

1. **Check for existing results**: System checks for `pyslammer_{version}_results.json.gz`
2. **Generate if missing**: Runs ~2600 analyses with current pySLAMMER code (3-5 minutes)
3. **Cache cleanup**: Deletes temporary cache files after collection
4. **Run verification**: Compares against SLAMMER reference data
5. **Generate report**: Creates detailed markdown report

## Understanding Results

### Test Output
```
tests/test_verification.py::test_rigid_method_group_pass_rate PASSED     [ 20%]
tests/test_verification.py::test_decoupled_method_group_pass_rate PASSED [ 40%]
tests/test_verification.py::test_coupled_method_group_pass_rate PASSED   [ 60%]
tests/test_verification.py::test_linear_regression_parameters PASSED     [ 80%]
tests/test_verification.py::test_generate_verification_report PASSED     [100%]
```

### Failure Examples
```
FAILED tests/test_verification.py::test_rigid_method_group_pass_rate
AssertionError: RIGID method pass rate 93.2% below threshold 95%
```

### Generation Output (New Versions)
```
Generating pySLAMMER results for version 0.3.0...
This may take a few minutes...
Found 2610 analyses matching criteria
Successfully ran 2610 new analyses  
Saved 2610 pySLAMMER results to .../pyslammer_0.3.0_results.json.gz
Cleaned up 2610 cached result files
```

## Configuration

### Tolerance Settings
Edit `tests/verification/config/verification_config.toml`:

```toml
[tolerances]
percent_passing_individual_tests = 95.0  # Group pass rate threshold
lin_regression_r_squared_min = 0.99      # R² minimum
lin_regression_slope_min = 0.99          # Slope range
lin_regression_slope_max = 1.01
lin_regression_intercept_min = -0.1      # Intercept range (cm)
lin_regression_intercept_max = 0.1
```

### Individual Test Tolerances
```toml
[tolerances.value_dependent]
small_displacement_threshold = 0.5  # cm
small_displacement_absolute = 0.05  # cm (for values ≤ 0.5 cm)

default_relative = 0.02             # 2% (for values > 0.5 cm)
default_absolute = 1.0              # 1 cm (for values > 0.5 cm)
```

## Troubleshooting

### Common Issues

**Import Error**: Missing functions
```
ImportError: cannot import name 'main' from 'verification.generate_pyslammer_verification_results'
```
- Solution: Check function names in generation script

**No Results Found**: Missing result files
```
FileNotFoundError: pySLAMMER results not found at .../pyslammer_0.3.0_results.json.gz
```
- Solution: Let system generate results or check filename format

**Cache Issues**: Stale cache files
```
ValueError: No cached pySLAMMER results found
```
- Solution: Delete cache directory and regenerate

**Test Failures**: Statistical thresholds not met
```
AssertionError: RIGID method pass rate 93.2% below threshold 95%
```
- Solution: Check pySLAMMER implementation or adjust tolerances

### Debug Commands

```bash
# Show detailed output during generation
pytest tests/test_verification.py --pyslammer-version 0.3.0 -v -s

# Run single test for debugging
pytest tests/test_verification.py::test_rigid_method_group_pass_rate -v

# Show full traceback
pytest tests/test_verification.py --tb=long
```

### Manual Verification

```python
# Check if results exist
from tests.test_verification import check_pyslammer_results_exist
print(check_pyslammer_results_exist("0.2.2"))

# Generate results manually
from tests.verification.generate_pyslammer_verification_results import run_verification_analyses, collect_and_save_pyslammer_results
run_verification_analyses(pyslammer_version="0.3.0")
collect_and_save_pyslammer_results(pyslammer_version="0.3.0")
```

## Best Practices

1. **Test Before Releases**: Always run verification before tagging new versions
2. **Use Version Tags**: Prefer semantic version tags over "dev" for releases  
3. **Check Reports**: Review generated reports for statistical trends
4. **Archive Results**: Keep result files for historical comparison
5. **Update Tolerances**: Adjust tolerances based on expected precision changes

## Integration with CI/CD

Example GitHub Actions workflow:
```yaml
- name: Run pySLAMMER Verification
  run: |
    pytest tests/test_verification.py --pyslammer-version ${{ github.ref_name }} -v
    
- name: Upload Verification Report
  uses: actions/upload-artifact@v3
  with:
    name: verification-report-${{ github.ref_name }}
    path: tests/verification_data/results/verification_report_v${{ github.ref_name }}.md
```

## Support

For issues with the verification system:
1. Check this guide for common solutions
2. Review tolerance settings in `verification_config.toml`
3. Examine generated reports for statistical insights
4. Check individual test outputs with `-v` flag