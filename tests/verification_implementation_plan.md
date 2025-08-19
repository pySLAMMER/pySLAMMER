# Automated Legacy Verification Implementation Plan

This document outlines the comprehensive plan for implementing an automated verification system to compare pySLAMMER results with legacy SLAMMER (Java) results.

## Overview

The goal is to replace the current ad-hoc Excel-based verification process with a robust, automated system that ensures pySLAMMER maintains compatibility with legacy SLAMMER results while providing better maintainability and security.

## Current State Analysis

The existing system (`verification_processes.py` and `SLAMMER_comp.ipynb`):
- ✅ Compares pySLAMMER results with SLAMMER (Java) legacy results
- ✅ Tests Rigid, Decoupled, and Coupled analysis methods  
- ✅ Runs both normal and inverse directions, calculates averages
- ✅ Handles data reformatting and deduplication
- ❌ Uses Excel files (security/portability concerns)
- ❌ Jupyter notebook dependency 
- ❌ No automated caching or CLI interface

## Implementation Plan

## ✅ **PROGRESS STATUS** (Updated Aug 2024)

### **Completed:**
- **Phase 1: Data Migration & Schema** ✅ COMPLETE
  - JSON schema implemented (`legacy_results_schema.json`)
  - Excel data successfully migrated to JSON format
  - Reference data: `slammer_results.json` (1.8MB) and compressed `.json.gz` (52KB)
  - Schema validation working with comprehensive test coverage

- **Phase 2: Data Storage Infrastructure** ✅ COMPLETE  
  - Full directory structure established (`verification_data/` with subdirs)
  - Configuration system implemented (`verification_config.toml`)
  - Data management with compression and validation
  - Intelligent path resolution and error handling

- **Phase 3: Verification Framework** ✅ COMPLETE
  - Core data models implemented (`schemas.py`)
  - Data loading and caching framework (`data_loader.py`) 
  - Schema validation with proper error handling
  - Configuration management with tolerance settings
  - Test infrastructure (`test_phase2_infrastructure.py`)

- **Phase 5: Statistical Comparison Engine** ✅ COMPLETE
  - Individual test comparison with configurable tolerances
  - Group statistical analysis with linear regression
  - Comprehensive reporting system
  - Special handling for edge cases and small displacements

- **Phase 6: CLI Interface** ✅ COMPLETE
  - Full command-line interface with `run`, `report`, `cache`, `migrate` commands
  - Filtering by methods, earthquakes, test IDs
  - Multiple output formats (text, JSON, CSV)
  - Intelligent caching with cache management
  - Progress bars and detailed reporting

- **Phase 7: Integration with Test Suite** ✅ COMPLETE
  - Comprehensive pytest test suite with 24 test cases
  - Test classes for data management, configuration, statistical comparison, CLI integration
  - Parametrized tests for different analysis methods
  - Fast and slow test categories with `--runslow` option
  - GitHub Actions CI/CD workflow with multi-job pipeline
  - Test runner script for convenient local testing
  - Error handling and edge case coverage

### **Next Steps:**
- Phase 4: Complete intelligent caching system (basic caching implemented)
- Documentation and deployment guide

---

### Phase 1: Data Migration & Schema ✅

**One-time Migration Script:**
```python
def migrate_excel_to_json():
    """Convert existing Excel files to new JSON format"""
    # Read SLAMMER_results.xlsx
    # Extract reference data vs. computed results
    # Validate against schema
    # Generate compressed JSON files
    # Create checksums for integrity
```

**JSON Schema Design:**
```json
{
  "schema_version": "1.0",
  "metadata": {
    "source": "SLAMMER v7.55",
    "date_extracted": "2024-01-01",
    "total_tests": 1250
  },
  "tests": [
    {
      "test_id": "eq1_rec1_rigid_normal",
      "earthquake": "Northridge 1994",
      "record": "TAR090.txt", 
      "method": "rigid",
      "direction": "normal",
      "parameters": {
        "ky_g": 0.15,
        "target_pga": 0.25,
        "damping_ratio": null,
        "ref_strain": null
      },
      "expected_result": {
        "max_sliding_disp_cm": 4.23,
        "units": "cm"
      }
    }
  ]
}
```

**Benefits:**
- Version control friendly (no binary Excel files)
- Tamper-resistant (checksums, schema validation)
- Faster I/O (compressed JSON)
- Platform independent

### Phase 2: Data Storage Infrastructure ✅

**Set up directory structure and data handling:**

```
verification_data/
├── schemas/
│   └── legacy_results_schema.json    # JSON schema validation
├── reference/
│   └── slammer_results.json.gz       # Legacy SLAMMER results (compressed)
├── cache/
│   └── pyslammer_results.json.gz     # Cached pySLAMMER results
└── config/
    └── verification_config.toml       # Test configurations & tolerances
```

**Data Management Components:**
- `DataManager`: Handles data loading/saving with validation
- Schema validation using JSON Schema
- Compressed storage for large datasets

### Phase 3: Verification Framework ✅ (Partial)

**Core Components:**

```
verification/
├── __init__.py
├── core.py              # VerificationRunner, ResultCache
├── comparisons.py       # Statistical comparison methods
├── data_loader.py       # Load/save verification data
├── schemas.py           # Pydantic models for validation
└── cli.py               # Command-line interface
```

**Key Classes:**
- `VerificationRunner`: Orchestrates verification process
- `ResultCache`: Intelligent caching with dependency tracking
- `ComparisonEngine`: Statistical analysis and tolerance checking
- `DataManager`: Handles data loading/saving with validation

### Phase 4: Intelligent Caching System 💾

**Cache Strategy:**
```python
class ResultCache:
    def get_cached_result(self, test_config: TestConfig) -> Optional[Result]:
        """Return cached result if valid, None if needs recompute"""
        
    def should_recompute(self, test_config: TestConfig) -> bool:
        """Check if result needs recomputation based on:
        - Code version changes
        - Parameter changes  
        - Force refresh flag
        """
        
    def store_result(self, test_config: TestConfig, result: Result):
        """Store result with metadata (timestamp, version, checksums)"""
```

**Cache Invalidation Triggers:**
- pySLAMMER version changes
- Input parameter modifications
- Manual force refresh (`--force-recompute`)
- Configurable cache expiry

### Phase 5: Statistical Comparison Engine 📊

**Comparison Metrics:**
**Individual comparison**
```python
@dataclass
class IndividualComparisonResult:
    test_id: str
    method: str  # Rigid, Decoupled, Coupled
    direction: str  # Normal, Inverse
    
    # Statistical measures
    absolute_error: float
    relative_error: float
    percent_difference: float
    
    # Pass/fail status
    passes_tolerance: bool
    tolerance_used: float
    
    # Context
    legacy_value: float
    pyslammer_value: float
    units: str
```

**Group comparison**
```python
@dataclass
class GroupComparisonResult:
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
```

**Tolerance Configuration:**
**Individual comparison**
```toml
# verification_config.toml
[tolerances]
default_relative = 0.02  # 5%
default_absolute = 1.0  # 1 cm

[tolerances.value_dependent]
# Stricter tolerances for smaller displacements
small_displacement_threshold = 0.5  # cm
small_displacement_tolerance = { relative = inf, absolute = 0.05 }
```

**Group comparison**
```toml
# verification_config.toml
[tolerances]
percent_passing_individual_tests = 0.95  # 95%
lin_regression_slope_min = 0.99
lin_regression_slope_max = 1.01
lin_regression_intercept_min = -0.1
lin_regression_intercept_max = 0.1
lin_regression_r_squared_min = 0.99
```

### Phase 6: CLI Interface ✅

**Command Structure:**
```bash
# Run verification for all tests
uv run python -m verification run

# Run specific subset
uv run python -m verification run --methods rigid,decoupled --force-recompute

# Compare and report
uv run python -m verification report --format json --output results.json

# Show cache status
uv run python -m verification cache --status

# Clear cache
uv run python -m verification cache --clear

# Convert legacy Excel data (one-time migration)
uv run python -m verification migrate --from SLAMMER_results.xlsx
```

### Phase 7: Integration with Test Suite ✅

**Pytest Integration:**
```python
# tests/test_verification.py
@pytest.mark.verification
@pytest.mark.slow
class TestLegacyVerification:
    def test_verification_passes(self):
        """Run verification and ensure all tests pass tolerances"""
        
    @pytest.mark.parametrize("method", ["rigid", "decoupled", "coupled"])
    def test_method_specific_verification(self, method):
        """Test specific analysis methods"""
        
    def test_verification_report_generation(self):
        """Ensure reports can be generated"""
```

**CI/CD Integration:**
- Add to GitHub Actions with caching
- Generate verification reports on releases
- Fail CI if verification tolerances exceeded


## Implementation Timeline

**Recommended Implementation Order:**

1. **Week 1**: Data migration script + JSON schema design (Phase 1)
2. **Week 2**: Data storage infrastructure + verification framework (Phases 2-3)  
3. **Week 3**: Caching system + statistical comparison engine (Phases 4-5)
4. **Week 4**: CLI interface + pytest integration (Phases 6-7)
5. **Week 5**: Documentation + CI/CD integration

## Key Benefits

- **Security**: No more editable Excel files, checksums for integrity
- **Performance**: Intelligent caching reduces redundant computations
- **Maintainability**: Pure Python, version controlled, schema validated
- **Flexibility**: Configurable tolerances, multiple output formats
- **Automation**: CI/CD integration, automated regression detection
- **Extensibility**: Easy to add new analysis methods or comparison metrics

## Technical Requirements

### Dependencies
- `pydantic` for data validation
- `click` for CLI interface
- `toml` for configuration files
- `jsonschema` for schema validation
- `pytest` for testing integration
- `pandas` for data manipulation (during migration)

### File Structure
```
tests/
├── verification/           # New verification framework
│   ├── __init__.py
│   ├── core.py
│   ├── comparisons.py
│   ├── data_loader.py
│   ├── schemas.py
│   └── cli.py
├── verification_data/      # Data storage
│   ├── schemas/
│   ├── reference/
│   ├── cache/
│   └── config/
├── test_verification.py    # Pytest integration
└── migrate_legacy_data.py  # One-time migration script
```

## Success Criteria

1. ✅ All legacy Excel data successfully migrated to JSON format (Phase 1) **DONE**
2. ✅ Data storage infrastructure handles validation and compression (Phase 2) **DONE**
3. 🔄 Verification framework orchestrates the comparison process (Phase 3) **PARTIAL**
4. 🔄 Intelligent caching reduces redundant computations (Phase 4) **PARTIAL**
5. ✅ Statistical comparisons identify regressions within defined tolerances (Phase 5) **DONE**
6. ✅ CLI interface provides easy access to all functionality (Phase 6) **DONE**
7. ✅ Integration with pytest and CI/CD pipelines (Phase 7) **DONE**
8. ⏳ Documentation and examples for maintainers **PENDING**
9. ⏳ Performance improvement over current Excel-based approach **PENDING**

## Future Enhancements

- **Web Dashboard**: Visual reporting interface
- **Benchmarking**: Performance regression detection
- **Parameterized Testing**: Automatic generation of test cases
- **Multi-version Comparison**: Compare across pySLAMMER versions
- **Statistical Analysis**: Trend analysis and outlier detection

This system will provide robust, automated verification against legacy SLAMMER results while being maintainable and extensible for future development.