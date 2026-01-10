# Verification Report
pySLAMMER version: dev_dwtol
SLAMMER version: 1.1

## Verification Results

### RIGID Method:
- Normal: R² = 0.999999 ✅, slope = 1.000703 ✅, intercept = -0.015 ✅
- Inverse: R² = 0.999998 ✅, slope = 1.000911 ✅, intercept = -0.019 ✅
- Combined: 98.9% ✅ individual pass rate
### DECOUPLED Method:
- Normal: R² = 0.999999 ✅, slope = 1.000718 ✅, intercept = -0.006 ✅
- Inverse: R² = 0.999999 ✅, slope = 1.000905 ✅, intercept = -0.010 ✅
- Combined: 98.7% ✅ individual pass rate
### COUPLED Method:
- Normal: R² = 0.999999 ✅, slope = 1.000665 ✅, intercept = 0.003 ✅
- Inverse: R² = 0.999999 ✅, slope = 1.001000 ✅, intercept = -0.005 ✅
- Combined: 99.0% ✅ individual pass rate

## Verification Tolerances

### Linear regression tolerance
  - R$^2 \le 0.99$
  - slope $= 1 \pm 0.01$
  - intercept $= 0 \pm 0.1$ cm

### Individual test tolerance
The individual test tolerances are enforced in aggregate by the group pass rate tolerance.

Expected values > 0.5 cm:
  - Relative error <= 2%
  - Absolute error <= 1.0 cm
  
Expected values <= 0.5 cm:
  - Absolute error <= 0.05 cm

### Group pass rate tolerance
- Group pass rate $\ge 95$%