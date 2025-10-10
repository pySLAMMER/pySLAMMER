# pySLAMMER Package Specifications

This document defines the API specifications, expected behavior, and validation requirements for the pySLAMMER package classes.

## Overview

The pySLAMMER package provides classes for earthquake sliding block analysis. The core classes follow a hierarchical design where `GroundMotion` represents earthquake records and `SlidingBlockAnalysis` serves as a base class for specific analysis methods.

## Core Classes

### `GroundMotion`

**Purpose**: Represents and validates earthquake ground motion records.

#### Constructor Signature
```python
GroundMotion(accel: ArrayLike, dt: float, name: str = "None")
```

#### Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `accel` | `ArrayLike` | Required | Ground motion acceleration record in g |
| `dt` | `float` | Required | Time step of the record (s) |
| `name` | `str` | `"None"` | Name of the record |

#### Validation Requirements

**Input Validation:**
- **TypeError/ValueError**: `accel` must be convertible to numpy array
  - Error message: `"Could not convert accel to numeric array: {original_error}"`
- **ValueError**: `accel` must be 1-dimensional
  - Error message: `"accel must be 1-dimensional, got {accel.ndim}D"`
- **ValueError**: `dt` must be positive (> 0)
  - Error message: `"Time step dt must be positive, got {dt}"`

**Warnings:**
- **UserWarning**: `dt > 0.1` (unusually large time step)
  - Warning message: `"Time step dt={dt:.4f}s is unusually large for ground motion data. Typical range is 0.001-0.04s. Please verify this is correct."`

#### Public Attributes
| Attribute | Type | Description |
|-----------|------|-------------|
| `accel` | `np.ndarray` | Ground motion acceleration in g |
| `dt` | `float` | Time step in seconds |
| `name` | `str` | Record name |
| `pga` | `float` | Peak ground acceleration in g |
| `mean_period` | `float` | Mean period of the ground motion |

#### Expected Behavior
- `accel` is stored as float64 numpy array
- `pga` is computed as `max(abs(accel))`
- `mean_period` computed using FFT analysis
- String representation includes name, PGA, dt, and number of points

---

### `SlidingBlockAnalysis`

**Purpose**: Base class for sliding block analysis methods. Handles input validation, unit conversion, and provides common integration methods.

#### Constructor Signature
```python
SlidingBlockAnalysis(ky: float, ground_motion: Union[GroundMotion, dict], 
                    scale_factor: float = 1.0, target_pga: float = None)
```

#### Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ky` | `float` | Required | Yield acceleration in g |
| `ground_motion` | `GroundMotion` or `dict` | Required | Ground motion data |
| `scale_factor` | `float` | `1.0` | Scaling factor for acceleration |
| `target_pga` | `float` | `None` | Target PGA for automatic scaling |

#### Ground Motion Dictionary Format
When providing `ground_motion` as dict:
```python
{
    "accel": ArrayLike,  # Required: acceleration data
    "dt": float,         # Required: time step  
    "name": str          # Optional: defaults to "Unknown"
}
```

#### Validation Requirements

**Input Validation:**
- **ValueError**: `ky` must be positive (> 0)
  - Error message: `"Yield acceleration ky must be positive, got {ky} (upslope sliding not yet supported)."`
- **ValueError**: Cannot provide both `scale_factor` and `target_pga`
  - Error message: `"Both target_pga and scale_factor cannot be provided at the same time."`
- **TypeError**: `ground_motion` must be GroundMotion object or dict
  - Error message: `"ground_motion must be GroundMotion object or dict, got {type}"`
- **ValueError**: Invalid ground motion dictionary
  - Error message: `"Invalid ground_motion dictionary: {details}"`
- **KeyError**: Missing required keys in dictionary
  - Error message: `"Missing required keys: {missing_keys}"`

#### Expected Behavior

**Initialization:**
- `ky` converted to m/s² (multiplied by `G_EARTH = 9.80665`)
- Input acceleration copied and scaled by `scale_factor` or computed scale from `target_pga`
- If `target_pga` provided: `scale_factor = target_pga / max(abs(ground_motion.accel))`

**Unit Conversion (`_compile_base_attributes()`):**
- `ground_acc`: Input acceleration converted to m/s² (`a_in * G_EARTH`)
- `ground_vel`: First integral of `ground_acc` using trapezoidal rule
- `ground_disp`: Second integral (integral of `ground_vel`)
- Initial conditions: `ground_vel[0] = 0`, `ground_disp[0] = 0`

**Base Class Behavior:**
- Calling `sliding_block_plot()` without subclass analysis should raise error
- All motion attributes initially `None` until analysis performed
- Motion integration uses `scipy.integrate.cumulative_trapezoid`

#### Public Attributes (Post-Initialization)
| Attribute | Type | Description |
|-----------|------|-------------|
| `ky` | `float` | Yield acceleration in m/s² |
| `a_in` | `np.ndarray` | Scaled input acceleration in g |
| `dt` | `float` | Time step in seconds |
| `scale_factor` | `float` | Applied scaling factor |
| `motion_name` | `str` | Ground motion name |

#### Analysis Attributes (Set by subclasses)
| Attribute | Type | Initial | Description |
|-----------|------|---------|-------------|
| `ground_acc` | `np.ndarray` | `None` | Ground acceleration in m/s² |
| `ground_vel` | `np.ndarray` | `None` | Ground velocity in m/s |
| `ground_disp` | `np.ndarray` | `None` | Ground displacement in m |
| `block_acc` | `np.ndarray` | `None` | Block acceleration in m/s² |
| `block_vel` | `np.ndarray` | `None` | Block velocity in m/s |
| `block_disp` | `np.ndarray` | `None` | Block displacement in m |
| `sliding_vel` | `np.ndarray` | `None` | Sliding velocity in m/s |
| `sliding_disp` | `np.ndarray` | `None` | Sliding displacement in m |

## Comparison with Legacy Results from SLAMMER

This section defines requirements for automated verification against legacy SLAMMER (Java) results to ensure backward compatibility and regression detection.

### Purpose
Maintain confidence that pySLAMMER produces equivalent results to the legacy SLAMMER software by implementing automated comparison testing with configurable tolerances.

### Requirements Summary
1. **Replace Excel dependencies** with version-controlled, tamper-resistant data formats
2. **Implement intelligent caching** to avoid redundant computations
3. **Provide automated regression detection** with statistical analysis
4. **Enable selective re-computation** for releases or code changes
5. **Integrate with CI/CD pipeline** for continuous verification

### Current Implementation
- Existing verification code in `verification_processes.py` 
- Legacy data stored in `SLAMMER_results.xlsx`
- Manual comparison process using Jupyter notebooks

### Future Implementation
See detailed implementation plan: **[verification_implementation_plan.md](./verification_implementation_plan.md)**

The plan includes:
- JSON-based data storage with schema validation
- Intelligent caching system with dependency tracking  
- Statistical comparison engine with configurable tolerances
- CLI interface for verification operations
- pytest integration for automated testing
- CI/CD integration for regression detection

### Expected Verification Coverage
- **Analysis Methods**: Rigid, Decoupled, Coupled sliding block analysis
- **Test Directions**: Normal, Inverse, and Average directions
- **Statistical Metrics**: Absolute error, relative error, percentage difference
- **Tolerance Checking**: Method-specific and value-dependent tolerances
- **Performance Tracking**: Computation time and memory usage regression

## Design Patterns and Best Practices

### Error Handling
- Use specific exception types (`ValueError`, `TypeError`, `KeyError`)
- Provide descriptive error messages with actual values
- Validate inputs early in constructors
- Use warnings for questionable but valid inputs

### Unit Consistency
- Ground motion and yield accelerations always input and reported in g
- Internal calculations in SI units (m/s²)
- Wrap acceleration variables in single underscores if they're not in g (e.g., `_ky_ = ky * G_EARTH`)
- Clear documentation of expected units for all parameters

### Inheritance Pattern
- Base class handles common validation and setup
- Subclasses implement specific analysis algorithms
- Protected methods (`_compile_*`) for internal operations
- Public methods for user interface

### Integration and Numerical Methods
- Use scipy for numerical integration (trapezoidal rule)
- Consistent initial conditions (zero velocity/displacement)
- Preserve array lengths through integration

## Testing Requirements

Each class should have comprehensive tests covering:
- Valid input acceptance
- All specified error conditions
- Boundary value testing
- Expected behavior verification
- Unit conversion accuracy
- Integration with dependent classes

## Future Specifications

When adding specifications for `RigidAnalysis`, `DecoupledAnalysis`, and `CoupledAnalysis`:
- Follow the same format structure
- Specify inheritance relationships with `SlidingBlockAnalysis`
- Document analysis-specific parameters and methods
- Define expected output attributes and accuracy requirements
- Include performance characteristics if relevant

When adding specs for RigidAnalysis, DecoupledAnalysis, and CoupledAnalysis:

  1. Method-specific parameters (analysis algorithms, convergence criteria)
  2. Performance requirements (computation time, memory usage)
  3. Accuracy specifications (numerical precision, validation against known solutions)
  4. Output format requirements (result attributes, plotting capabilities)
  5. Compatibility requirements (version dependencies, optional features)

  The updated format provides a solid foundation that's professional, comprehensive, and
  maintainable for expanding to additional classes.

